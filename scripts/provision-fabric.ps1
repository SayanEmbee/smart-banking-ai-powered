# =========================================================================
# Real-Time Banking Risk & Fraud Intelligence - Fabric Workspace Deployer
# =========================================================================
#
# This script automates:
# 1. Workspace Discovery / Creation
# 2. Assigning the Workspace to your F-Capacity
# 3. Provisioning the Lakehouse (BankingFraudLakehouse)
# 4. Uploading the pre-seeded historical CSV directly to OneLake
# 5. Provisioning the KQL Database (BankingRiskDB)
# 6. Provisioning the Eventstream (BankingTransactionStream)
#
# Authentication is performed via your active Azure CLI token context.

$ErrorActionPreference = "Stop"

# Define config file path
$configPath = Join-Path $PSScriptRoot "..`config`accelerator-config.json"
if (-not (Test-Path $configPath)) {
    $configPath = Join-Path $PSScriptRoot "config`accelerator-config.json"
}

if (-not (Test-Path $configPath)) {
    Write-Error "Could not locate config/accelerator-config.json. Please run from the project root."
}

Write-Host "--------------------------------------------------"
Write-Host "   Microsoft Fabric Assets Automated Deployer     "
Write-Host "--------------------------------------------------"

# Load Configuration
Write-Host "Reading settings from $configPath..."
$config = Get-Content -Raw -Path $configPath | ConvertFrom-Json

$workspaceName = $config.workspaceName
$lakehouseName = $config.lakehouseName
$kqlDbName = $config.kqlDatabaseName
$streamName = $config.eventstreamName
$capacityId = $config.capacityId

if ([string]::IsNullOrEmpty($capacityId)) {
    Write-Warning "Fabric Capacity ID is empty in accelerator-config.json."
    Write-Warning "Please run 'infra/create-capacity.ps1' first, or assign the workspace manually."
}

# 1. Fetch Entra ID Access Tokens from Azure CLI
Write-Host "Fetching access tokens via Azure CLI..."
$fabricToken = ""
$storageToken = ""
try {
    # Access token for Fabric REST API
    $fabricToken = az account get-access-token --resource "https://api.fabric.microsoft.com" --query accessToken -o tsv
    # Access token for OneLake Storage DFS API
    $storageToken = az account get-access-token --resource "https://storage.azure.com" --query accessToken -o tsv
} catch {
    Write-Error "Failed to retrieve active access tokens. Ensure you are signed in via 'az login'."
}

$fabricHeaders = @{
    "Authorization" = "Bearer $fabricToken"
    "Content-Type"  = "application/json"
}

$storageHeaders = @{
    "Authorization" = "Bearer $storageToken"
}

# Helper: Invoke Fabric REST API call
function Invoke-FabricApi {
    param(
        [string]$Uri,
        [string]$Method = "GET",
        [object]$Body = $null
    )
    $params = @{
        Headers     = $fabricHeaders
        Uri         = $Uri
        Method      = $Method
        ContentType = "application/json"
    }
    if ($Body) {
        $params.Body = ($Body | ConvertTo-Json -Depth 10)
    }
    
    try {
        return Invoke-RestMethod @params
    } catch {
        Write-Error "Fabric API Error ($Method to $Uri): $_"
    }
}

# 2. Discover or Create Workspace
Write-Host "Checking if Workspace '$workspaceName' exists..."
$workspaces = Invoke-FabricApi -Uri "https://api.fabric.microsoft.com/v1/workspaces"
$workspace = $workspaces.value | Where-Object { $_.displayName -eq $workspaceName }
$workspaceId = ""

if ($workspace) {
    $workspaceId = $workspace.id
    Write-Host "Found existing Workspace '$workspaceName' (ID: $workspaceId)"
} else {
    Write-Host "Workspace '$workspaceName' not found. Creating workspace..."
    $createBody = @{
        displayName = $workspaceName
    }
    $newWorkspace = Invoke-FabricApi -Uri "https://api.fabric.microsoft.com/v1/workspaces" -Method "POST" -Body $createBody
    $workspaceId = $newWorkspace.id
    Write-Host "Workspace created successfully! (ID: $workspaceId)"
}
$config.workspaceId = $workspaceId

# 3. Assign Workspace to Capacity
if (-not [string]::IsNullOrEmpty($capacityId)) {
    Write-Host "Assigning Workspace '$workspaceName' to Capacity..."
    try {
        $assignBody = @{
            capacityId = $capacityId
        }
        $assignUri = "https://api.fabric.microsoft.com/v1/workspaces/$workspaceId/assignToCapacity"
        Invoke-FabricApi -Uri $assignUri -Method "POST" -Body $assignBody | Out-Null
        Write-Host "Workspace assigned to capacity successfully."
    } catch {
        Write-Warning "Could not assign workspace to capacity automatically. You can do this manually in Workspace Settings."
    }
}

# 4. Fetch Existing Workspace Items to check existence (Idempotency)
Write-Host "Listing items in workspace to check for existing resources..."
$itemsList = Invoke-FabricApi -Uri "https://api.fabric.microsoft.com/v1/workspaces/$workspaceId/items"
$existingItems = $itemsList.value

# 5. Idempotently Create Lakehouse
$lakehouse = $existingItems | Where-Object { $_.displayName -eq $lakehouseName -and $_.type -eq "Lakehouse" }
$lakehouseId = ""
if ($lakehouse) {
    $lakehouseId = $lakehouse.id
    Write-Host "Lakehouse '$lakehouseName' already exists (ID: $lakehouseId)"
} else {
    Write-Host "Lakehouse '$lakehouseName' not found. Creating Lakehouse..."
    $lhBody = @{
        displayName = $lakehouseName
        type        = "Lakehouse"
    }
    $newLh = Invoke-FabricApi -Uri "https://api.fabric.microsoft.com/v1/workspaces/$workspaceId/items" -Method "POST" -Body $lhBody
    $lakehouseId = $newLh.id
    Write-Host "Lakehouse created successfully! (ID: $lakehouseId)"
}
$config.lakehouseId = $lakehouseId

# 6. Upload Historical CSV directly to OneLake Files
$csvPath = Join-Path $PSScriptRoot "..`data`historical_credit_card_fraud.csv"
if (-not (Test-Path $csvPath)) {
    $csvPath = Join-Path $PSScriptRoot "data`historical_credit_card_fraud.csv"
}

if (Test-Path $csvPath) {
    Write-Host "Uploading historical transactions dataset directly to OneLake..."
    $oneLakeUrl = "https://onelake.dfs.fabric.microsoft.com/$workspaceId/lakehouses/$lakehouseId/Files/historical_credit_card_fraud.csv"
    
    try {
        # Initialize the file in OneLake
        $initParams = @{
            Headers = $storageHeaders
            Uri     = "$oneLakeUrl`?action=create"
            Method  = "PUT"
        }
        Invoke-RestMethod @initParams | Out-Null
        
        # Write contents to OneLake
        $fileBytes = [System.IO.File]::ReadAllBytes($csvPath)
        $writeParams = @{
            Headers     = $storageHeaders
            Uri         = "$oneLakeUrl`?action=append&position=0"
            Method      = "PATCH"
            Body        = $fileBytes
            ContentType = "application/octet-stream"
        }
        Invoke-RestMethod @writeParams | Out-Null
        
        # Flush/Commit the file
        $flushParams = @{
            Headers = $storageHeaders
            Uri     = "$oneLakeUrl`?action=flush&position=$($fileBytes.Length)"
            Method  = "PATCH"
        }
        Invoke-RestMethod @flushParams | Out-Null
        
        Write-Host "Success! Uploaded historical CSV to OneLake Files."
    } catch {
        Write-Warning "OneLake upload failed: $_. You can manually drag and drop historical_credit_card_fraud.csv into the Lakehouse Files view."
    }
}

# 7. Idempotently Create KQL Database (KqlDatabase Item type)
$kqlDb = $existingItems | Where-Object { $_.displayName -eq $kqlDbName -and $_.type -eq "KqlDatabase" }
$kqlDbId = ""
if ($kqlDb) {
    $kqlDbId = $kqlDb.id
    Write-Host "KQL Database '$kqlDbName' already exists (ID: $kqlDbId)"
} else {
    Write-Host "KQL Database '$kqlDbName' not found. Creating database..."
    $dbBody = @{
        displayName = $kqlDbName
        type        = "KqlDatabase"
    }
    $newDb = Invoke-FabricApi -Uri "https://api.fabric.microsoft.com/v1/workspaces/$workspaceId/items" -Method "POST" -Body $dbBody
    $kqlDbId = $newDb.id
    Write-Host "KQL Database created successfully! (ID: $kqlDbId)"
}
$config.kqlDatabaseId = $kqlDbId

# 8. Idempotently Create Eventstream
$stream = $existingItems | Where-Object { $_.displayName -eq $streamName -and $_.type -eq "Eventstream" }
$streamId = ""
if ($stream) {
    $streamId = $stream.id
    Write-Host "Eventstream '$streamName' already exists (ID: $streamId)"
} else {
    Write-Host "Eventstream '$streamName' not found. Creating Eventstream..."
    $streamBody = @{
        displayName = $streamName
        type        = "Eventstream"
    }
    $newStream = Invoke-FabricApi -Uri "https://api.fabric.microsoft.com/v1/workspaces/$workspaceId/items" -Method "POST" -Body $streamBody
    $streamId = $newStream.id
    Write-Host "Eventstream created successfully! (ID: $streamId)"
}
$config.eventstreamId = $streamId

# 9. Update Configuration file
Write-Host "Writing resolved workspace and asset IDs back to accelerator-config.json..."
$jsonContent = ConvertTo-Json $config -Depth 10
Set-Content -Path $configPath -Value $jsonContent

Write-Host "--------------------------------------------------"
Write-Host "   Fabric Provisioning Completed!                 "
Write-Host "   Workspace ID:  $workspaceId"
Write-Host "   Lakehouse ID:  $lakehouseId"
Write-Host "   KQL DB ID:     $kqlDbId"
Write-Host "   Eventstream ID:$streamId"
Write-Host "--------------------------------------------------"
Write-Host "   To complete KQL mappings & Eventstream routing,"
Write-Host "   follow the steps detailed in your README.md."
Write-Host "--------------------------------------------------"
