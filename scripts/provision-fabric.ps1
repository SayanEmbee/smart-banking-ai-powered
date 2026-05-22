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
$configPath = Join-Path $PSScriptRoot "../config/accelerator-config.json"
if (-not (Test-Path $configPath)) {
    $configPath = Join-Path $PSScriptRoot "config/accelerator-config.json"
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

# Helper: Dynamically resolve Fabric SaaS Capacity GUID from Capacity name or resource ID
function Get-FabricCapacityGuid {
    param (
        [string]$CapacityNameOrId
    )

    if ([string]::IsNullOrEmpty($CapacityNameOrId)) {
        return ""
    }

    # If it's already a GUID format, return it directly!
    if ($CapacityNameOrId -match '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$') {
        return $CapacityNameOrId
    }

    Write-Host "Resolving Fabric SaaS Capacity GUID for capacity name: $CapacityNameOrId..."
    try {
        # Fetch capacities using the current Fabric token
        $capacitiesUri = "https://api.fabric.microsoft.com/v1/capacities"
        $capacitiesResponse = Invoke-FabricApi -Uri $capacitiesUri -Method "GET"
        
        $capacitiesList = $capacitiesResponse.value
        if ($null -eq $capacitiesList) {
            $capacitiesList = $capacitiesResponse.Body.value
        }
        
        # Search by display name (or capacity name)
        $targetCapacity = $capacitiesList | Where-Object { $_.displayName -eq $CapacityNameOrId -or $_.id -eq $CapacityNameOrId }
        
        if ($null -ne $targetCapacity) {
            $resolvedGuid = $targetCapacity.id
            Write-Host "Successfully resolved Capacity GUID: $resolvedGuid"
            return $resolvedGuid
        }
    } catch {
        Write-Warning "Failed to resolve Fabric Capacity GUID dynamically: $_"
    }

    # Fallback: if we can extract the name from an Azure Resource ID path
    if ($CapacityNameOrId -like "*/providers/Microsoft.Fabric/capacities/*") {
        $extractedName = $CapacityNameOrId.Split("/")[-1]
        Write-Host "Extracted capacity name from Resource ID: $extractedName. Retrying resolution..."
        return Get-FabricCapacityGuid -CapacityNameOrId $extractedName
    }

    return ""
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

# 3. Assign Workspace to Capacity with GUID resolution and Retries (to handle active directory sync latency)
if (-not [string]::IsNullOrEmpty($capacityId)) {
    $capacityGuid = Get-FabricCapacityGuid -CapacityNameOrId $capacityId
    if ([string]::IsNullOrEmpty($capacityGuid) -and -not [string]::IsNullOrEmpty($config.capacityName)) {
        $capacityGuid = Get-FabricCapacityGuid -CapacityNameOrId $config.capacityName
    }
    
    if ([string]::IsNullOrEmpty($capacityGuid)) {
        Write-Error "Could not resolve a valid 36-character SaaS GUID for Fabric Capacity '$capacityId'."
    }
    
    # Save the resolved SaaS Capacity GUID back to config
    if ($config.capacityId -ne $capacityGuid) {
        $config.capacityId = $capacityGuid
        $jsonContent = ConvertTo-Json $config -Depth 10
        Set-Content -Path $configPath -Value $jsonContent
    }

    Write-Host "Assigning Workspace '$workspaceName' to Capacity (GUID: $capacityGuid)..."
    $retryCount = 3
    $assigned = $false
    for ($i = 1; $i -le $retryCount; $i++) {
        try {
            $assignBody = @{
                capacityId = $capacityGuid
            }
            $assignUri = "https://api.fabric.microsoft.com/v1/workspaces/$workspaceId/assignToCapacity"
            Invoke-FabricApi -Uri $assignUri -Method "POST" -Body $assignBody | Out-Null
            Write-Host "Workspace assigned to capacity successfully."
            $assigned = $true
            break
        } catch {
            Write-Warning "Attempt $i to assign workspace to capacity failed. Retrying in 15 seconds..."
            Start-Sleep -Seconds 15
        }
    }
    if (-not $assigned) {
        Write-Error "Failed to assign Workspace to Capacity. Fabric requires your workspace to be bound to an active F-Capacity to deploy premium items like Lakehouses. Please manually assign the workspace '$workspaceName' to the capacity '$capacityGuid' in the Microsoft Fabric Portal (Workspace Settings -> Premium -> Fabric Capacity) before running this script again."
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
    Write-Host "Waiting 15 seconds for OneLake DFS metadata synchronization..."
    Start-Sleep -Seconds 15
}
$config.lakehouseId = $lakehouseId

# 6. Upload Historical CSV directly to OneLake Files
$csvPath = Join-Path $PSScriptRoot "../data/historical_credit_card_fraud.csv"
if (-not (Test-Path $csvPath)) {
    $csvPath = Join-Path $PSScriptRoot "data/historical_credit_card_fraud.csv"
}

if (Test-Path $csvPath) {
    Write-Host "Uploading historical transactions dataset directly to OneLake..."
    # Correct OneLake DFS URL structure: workspaceId/lakehouseId/Files/path
    $oneLakeUrl = "https://onelake.dfs.fabric.microsoft.com/$workspaceId/$lakehouseId/Files/historical_credit_card_fraud.csv"
    
    try {
        # Initialize the file in OneLake
        $initParams = @{
            Headers = $storageHeaders
            Uri     = "$oneLakeUrl`?resource=file"
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

# 7. Idempotently Create Eventhouse & its default KQL Database
$kqlDb = $existingItems | Where-Object { $_.displayName -eq $kqlDbName -and ($_.type -eq "KQLDatabase" -or $_.type -eq "KqlDatabase") }
$kqlDbId = ""

if ($kqlDb) {
    $kqlDbId = $kqlDb.id
    Write-Host "KQL Database '$kqlDbName' already exists (ID: $kqlDbId)"
} else {
    # Check if the Eventhouse already exists
    $eventhouse = $existingItems | Where-Object { $_.displayName -eq $kqlDbName -and $_.type -eq "Eventhouse" }
    if (-not $eventhouse) {
        Write-Host "Eventhouse '$kqlDbName' not found. Creating Eventhouse..."
        $ehBody = @{
            displayName = $kqlDbName
            type        = "Eventhouse"
        }
        $newEh = Invoke-FabricApi -Uri "https://api.fabric.microsoft.com/v1/workspaces/$workspaceId/items" -Method "POST" -Body $ehBody
        Write-Host "Eventhouse created successfully! (ID: $($newEh.id))"
        Write-Host "Waiting 10 seconds for default child KQL Database to be provisioned..."
        Start-Sleep -Seconds 10
    }
    
    # Re-fetch items to locate the auto-created child KQL Database
    Write-Host "Locating the auto-created child KQL Database..."
    $updatedItems = Invoke-FabricApi -Uri "https://api.fabric.microsoft.com/v1/workspaces/$workspaceId/items"
    $kqlDb = $updatedItems.value | Where-Object { $_.displayName -eq $kqlDbName -and ($_.type -eq "KQLDatabase" -or $_.type -eq "KqlDatabase") }
    
    if ($kqlDb) {
        $kqlDbId = $kqlDb.id
        Write-Host "Located auto-created KQL Database successfully! (ID: $kqlDbId)"
    } else {
        Write-Error "Eventhouse was created, but the default child KQL Database '$kqlDbName' could not be resolved."
    }
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
