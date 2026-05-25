# =========================================================================
# Real-Time Banking Risk & Fraud Intelligence - Interactive Capacity Orchestrator
# =========================================================================
#
# This script guides you through setting up your Microsoft Fabric capacity:
# 1. Prompts for Deployment Mode (Existing Capacity vs. Provision New Capacity)
# 2. Prompts for target Azure Subscription, Resource Group, and Capacity Names
# 3. Resolves and registers Capacity IDs, resetting Workspace IDs for a fresh redeployment
#
# Authentication is performed via your active Azure CLI credentials context.

$ErrorActionPreference = "Stop"

# Define config file path
$configPath = Join-Path $PSScriptRoot "../config/accelerator-config.json"
if (-not (Test-Path $configPath)) {
    $configPath = Join-Path $PSScriptRoot "config/accelerator-config.json"
}

if (-not (Test-Path $configPath)) {
    Write-Error "Could not locate config/accelerator-config.json. Please run from the project root."
}

Write-Host "=================================================="
Write-Host "    MICROSOFT FABRIC CAPACITY ORCHESTRATION       "
Write-Host "=================================================="

# Load Configuration
$config = Get-Content -Raw -Path $configPath | ConvertFrom-Json

# 1. Interactive Menu Prompts
Write-Host ""
Write-Host "Select your capacity deployment pathway:"
Write-Host "  [existing] : Link to a pre-existing capacity (e.g. fabricespl01)"
Write-Host "  [new]      : Provision a brand new Fabric Capacity (Sku: F2) via Bicep template"
Write-Host ""

$deploymentMode = ""
while ($deploymentMode -ne "existing" -and $deploymentMode -ne "new") {
    $deploymentMode = Read-Host "Enter deployment mode (existing/new)"
    $deploymentMode = $deploymentMode.ToLower().Trim()
}

Write-Host "`nConfigure your target environment settings (Press Enter to keep current default):"
Write-Host "----------------------------------------------------------------------"

# Workspace Prompt
$workspaceName = $config.workspaceName
if ([string]::IsNullOrEmpty($workspaceName)) { $workspaceName = "SmartBankingRiskWorkspace" }
$inputWorkspace = Read-Host "Fabric Workspace Name [default: $workspaceName]"
if (-not [string]::IsNullOrEmpty($inputWorkspace)) { $workspaceName = $inputWorkspace.Trim() }

# Subscription Prompt
$subscriptionId = $config.subscriptionId
$inputSub = Read-Host "Azure Subscription ID [default: $subscriptionId]"
if (-not [string]::IsNullOrEmpty($inputSub)) { $subscriptionId = $inputSub.Trim() }

# Resource Group Prompt
$rgName = $config.resourceGroup
if ($deploymentMode -eq "existing") {
    $inputRg = Read-Host "Azure Resource Group Name (Optional, press Enter for default, or type 'none' to skip) [default: $rgName]"
    if ($inputRg -eq 'none') {
        $rgName = ""
    } elseif (-not [string]::IsNullOrEmpty($inputRg)) {
        $rgName = $inputRg.Trim()
    }
} else {
    $inputRg = Read-Host "Azure Resource Group Name [default: $rgName]"
    if (-not [string]::IsNullOrEmpty($inputRg)) { $rgName = $inputRg.Trim() }
}

# Capacity Name Prompt
$capacityName = $config.capacityName
$inputCap = Read-Host "Fabric Capacity Name [default: $capacityName]"
if (-not [string]::IsNullOrEmpty($inputCap)) { $capacityName = $inputCap.Trim() }

# Location and SKU settings
$location = $config.location
if ([string]::IsNullOrEmpty($location)) { $location = "CentralIndia" }
$sku = $config.capacitySku
if ([string]::IsNullOrEmpty($sku)) { $sku = "F8" }

if ($deploymentMode -eq "new") {
    $inputLoc = Read-Host "Azure Deployment Location [default: $location]"
    if (-not [string]::IsNullOrEmpty($inputLoc)) { $location = $inputLoc.Trim() }
    
    $inputSku = Read-Host "Capacity SKU size (e.g. F2, F4, F8) [default: $sku]"
    if (-not [string]::IsNullOrEmpty($inputSku)) { $sku = $inputSku.Trim() }
}

# 2. Check Azure CLI Status
Write-Host "`nChecking Azure CLI authentication..."
try {
    $accountInfo = az account show --query "{subscriptionName:name, subscriptionId:id}" -o json | ConvertFrom-Json
    Write-Host "Logged in to subscription: $($accountInfo.subscriptionName) ($($accountInfo.subscriptionId))"
} catch {
    Write-Error "Please run 'az login' and select your subscription before executing this script."
}

# Set active subscription if specified
if (-not [string]::IsNullOrEmpty($subscriptionId)) {
    Write-Host "Setting active subscription to $subscriptionId..."
    az account set --subscription $subscriptionId
} else {
    $subscriptionId = $accountInfo.subscriptionId
}

# 3. Get Signed-in User Details for Capacity Admin
Write-Host "Fetching signed-in user principal details..."
$adminUser = ""
try {
    $adminUser = az ad signed-in-user show --query userPrincipalName -o tsv
    Write-Host "Logged-in user: $adminUser"
} catch {
    $adminUser = "admin@smartbank.com"
}

$capacityId = ""

# 4. Execute Selected Deployment Mode
if ($deploymentMode -eq "existing") {
    # EXISTING CAPACITY MODE
    Write-Host "`nResolving existing Fabric Capacity details..."
    
    # 1. ALWAYS Try Fabric SaaS API lookup first (Requires ZERO Azure Resource Group or Subscription permissions!)
    Write-Host "Querying Fabric SaaS capacities list via Fabric REST API..."
    try {
        $fabricToken = az account get-access-token --resource "https://api.fabric.microsoft.com" --query accessToken -o tsv
        $headers = @{
            "Authorization" = "Bearer $fabricToken"
            "Content-Type"  = "application/json"
        }
        
        $res = Invoke-RestMethod -Headers $headers -Uri "https://api.fabric.microsoft.com/v1/capacities" -Method "GET"
        $capacitiesList = $res.value
        if ($null -eq $capacitiesList) {
            $capacitiesList = $res.Body.value
        }
        
        $targetCapacity = $capacitiesList | Where-Object { $_.displayName -eq $capacityName -or $_.id -eq $capacityName }
        if ($null -ne $targetCapacity) {
            $capacityId = $targetCapacity.id
            Write-Host "Success! Found capacity '$capacityName' in Fabric Portal."
            Write-Host "Capacity ID (GUID): $capacityId"
        } else {
            Write-Warning "Capacity '$capacityName' not found in Fabric SaaS capacities list. Will try Azure CLI lookup..."
        }
    } catch {
        Write-Warning "Fabric SaaS capacities API query failed: $_. Falling back to Azure CLI lookup..."
    }
    
    # 2. Fallback to Azure CLI lookup (only if SaaS lookup didn't find the capacity ID)
    if ([string]::IsNullOrEmpty($capacityId)) {
        Write-Host "Falling back to Azure Resource Manager lookup via Azure CLI..."
        try {
            if (-not [string]::IsNullOrEmpty($rgName)) {
                Write-Host "Verifying Resource Group '$rgName'..."
                try {
                    az group show --name $rgName -o none
                    Write-Host "Resource Group '$rgName' verified successfully."
                } catch {
                    Write-Warning "Could not access Resource Group '$rgName' via Azure CLI."
                }
            }
            
            # Ensure microsoft-fabric extension is installed
            Write-Host "Ensuring Microsoft Fabric CLI extension is installed..."
            $extensions = az extension list --query "[].name" -o json | ConvertFrom-Json
            if ("microsoft-fabric" -notin $extensions) {
                Write-Host "Installing microsoft-fabric extension..."
                az extension add --name microsoft-fabric -y
            }

            # Query existing Fabric Capacity resource ID via CLI show
            if (-not [string]::IsNullOrEmpty($rgName)) {
                Write-Host "Resolving Fabric Capacity ID for '$capacityName' inside Resource Group '$rgName'..."
                try {
                    $capacityId = az fabric capacity show --resource-group $rgName --name $capacityName --query id -o tsv
                    if ($capacityId) {
                        Write-Host "Successfully resolved Fabric Capacity ID in Resource Group '$rgName': $capacityId"
                    }
                } catch {
                    Write-Host "Capacity not found in Resource Group '$rgName'. Moving to subscription-wide search..."
                }
            }
            
            # Fallback search across all resource groups in the active subscription
            if ([string]::IsNullOrEmpty($capacityId)) {
                Write-Host "Searching for capacity '$capacityName' across all resource groups in active subscription..."
                $searchResult = az fabric capacity list --query "[?name=='$capacityName']" -o json
                if (-not [string]::IsNullOrEmpty($searchResult) -and $searchResult -ne "[]") {
                    $parsedSearch = $searchResult | ConvertFrom-Json
                    if ($parsedSearch.Count -gt 0 -or $null -ne $parsedSearch.resourceGroup) {
                        $matched = if ($parsedSearch.Count -gt 0) { $parsedSearch[0] } else { $parsedSearch }
                        $rgName = $matched.resourceGroup
                        $capacityId = $matched.id
                        Write-Host "Success! Found capacity '$capacityName' inside Resource Group '$rgName'."
                        Write-Host "Capacity ID: $capacityId"
                    }
                }
            }
        } catch {
            Write-Warning "Azure CLI lookup encountered errors: $_"
        }
    }
    
    if ([string]::IsNullOrEmpty($capacityId)) {
        Write-Error "Could not locate Fabric capacity '$capacityName' under your logged-in Fabric or Azure context. Please verify that your account has access to the capacity '$capacityName'."
    }
} else {
    # NEW CAPACITY MODE
    Write-Host "`nChecking if Resource Group '$rgName' exists..."
    try {
        az group show --name $rgName -o none
        Write-Host "Resource Group '$rgName' already exists."
    } catch {
        Write-Host "Resource Group '$rgName' not found. Creating in location '$location'..."
        az group create --name $rgName --location $location -o table
        Write-Host "Resource Group created successfully."
    }

    # Ensure microsoft-fabric extension is installed
    Write-Host "Ensuring Microsoft Fabric CLI extension is installed..."
    $extensions = az extension list --query "[].name" -o json | ConvertFrom-Json
    if ("microsoft-fabric" -notin $extensions) {
        Write-Host "Installing microsoft-fabric extension..."
        az extension add --name microsoft-fabric -y
    }

    # Provision Capacity via Bicep template
    $bicepPath = Join-Path $PSScriptRoot "main.bicep"
    if (-not (Test-Path $bicepPath)) {
        Write-Error "Could not locate main.bicep at $bicepPath"
    }

    Write-Host "Deploying new Fabric Capacity '$capacityName' (SKU: $sku) inside Resource Group '$rgName'..."
    Write-Host "This process may take 1-3 minutes..."
    try {
        $deployResult = az deployment group create `
            --resource-group $rgName `
            --template-file $bicepPath `
            --parameters capacityName=$capacityName skuName=$sku location=$location adminMembers="['$adminUser']" `
            --query "properties.outputs.capacityId.value" -o tsv
            
        $capacityId = $deployResult
        Write-Host "Fabric Capacity deployed successfully via Bicep!"
    } catch {
        Write-Error "Bicep deployment failed: $_"
    }
}

# 5. Save Configuration Details & Reset Asset IDs for New Workspace Creation
Write-Host "`nWriting updated configurations to accelerator-config.json..."
$config.workspaceName = $workspaceName
$config.capacityId = $capacityId
$config.subscriptionId = $subscriptionId
$config.resourceGroup = $rgName
$config.location = $location
$config.capacityName = $capacityName
$config.capacitySku = $sku

# Reset resource IDs to trigger clean creations in the new workspace!
$config.workspaceId = ""
$config.lakehouseId = ""
$config.kqlDatabaseId = ""
$config.eventstreamId = ""

$jsonContent = ConvertTo-Json $config -Depth 10
Set-Content -Path $configPath -Value $jsonContent

Write-Host "--------------------------------------------------"
Write-Host "   Capacity Configuration Successful!             "
Write-Host "   Mode Selected: $deploymentMode"
Write-Host "   Workspace Name:$workspaceName (ID cleared for redeployment)"
Write-Host "   Capacity Name: $capacityName"
Write-Host "   Capacity ID:   $capacityId"
Write-Host "--------------------------------------------------"
Write-Host "   You are now ready to launch the clean cloud    "
Write-Host "   workspace deployment by running:               "
Write-Host "   .\scripts\provision-fabric.ps1                 "
Write-Host "--------------------------------------------------"
