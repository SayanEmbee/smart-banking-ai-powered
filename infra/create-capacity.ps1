# =========================================================================
# Real-Time Banking Risk & Fraud Intelligence - Azure Capacity Provisioning
# =========================================================================
#
# This script automates the creation of:
# 1. An Azure Resource Group (if missing)
# 2. An Azure Microsoft Fabric Capacity (Sku: F2)
#
# Once created, it saves the resolved Capacity ID to accelerator-config.json.

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
Write-Host "   Azure Microsoft Fabric Capacity Provisioner    "
Write-Host "--------------------------------------------------"

# Load Configuration
Write-Host "Reading settings from $configPath..."
$config = Get-Content -Raw -Path $configPath | ConvertFrom-Json

$subscriptionId = $env:AZURE_SUBSCRIPTION_ID
if ([string]::IsNullOrEmpty($subscriptionId)) {
    $subscriptionId = $config.subscriptionId
}

$rgName = $env:AZURE_RESOURCE_GROUP
if ([string]::IsNullOrEmpty($rgName)) {
    $rgName = $config.resourceGroup
}

$location = $env:AZURE_LOCATION
if ([string]::IsNullOrEmpty($location)) {
    $location = $config.location
}

$capacityName = $config.capacityName
$sku = $config.capacitySku

if ([string]::IsNullOrEmpty($rgName) -or [string]::IsNullOrEmpty($capacityName)) {
    Write-Error "resourceGroup and capacityName must be populated in accelerator-config.json"
}

# 1. Check Azure CLI Status
Write-Host "Checking Azure CLI authentication..."
try {
    $accountInfo = az account show --query "{subscriptionName:name, subscriptionId:id}" -o json | ConvertFrom-Json
    Write-Host "Logged in to subscription: $($accountInfo.subscriptionName) ($($accountInfo.subscriptionId))"
} catch {
    Write-Error "Please run 'az login' and select your subscription before executing this script."
}

# Set active subscription if specified in config
if (-not [string]::IsNullOrEmpty($subscriptionId)) {
    Write-Host "Setting subscription to $subscriptionId..."
    az account set --subscription $subscriptionId
} else {
    $subscriptionId = $accountInfo.subscriptionId
}

# 2. Get Signed-in User Principal Name for Capacity Admin Assignment
Write-Host "Fetching signed-in user details..."
try {
    $adminUser = az ad signed-in-user show --query userPrincipalName -o tsv
    Write-Host "Capacity Administrator will be assigned to: $adminUser"
} catch {
    $adminUser = ""
    Write-Warning "Could not fetch signed-in user principal name. Capacity admin might need manual configuration."
}

# 3. Verify Existing Resource Group and Retrieve Fabric Capacity Details
Write-Host "Verifying existing Resource Group '$rgName' and Fabric Capacity '$capacityName'..."

$capacityId = ""
try {
    # 3.1 Verify Resource Group exists
    az group show --name $rgName -o none
    Write-Host "Resource Group '$rgName' verified successfully."
    
    # 3.2 Install microsoft-fabric extension if missing
    Write-Host "Ensuring Microsoft Fabric CLI extension is installed..."
    $extensions = az extension list --query "[].name" -o json | ConvertFrom-Json
    if ("microsoft-fabric" -notin $extensions) {
        Write-Host "Installing microsoft-fabric extension..."
        az extension add --name microsoft-fabric -y
    } else {
        Write-Host "microsoft-fabric extension is already installed."
    }

    # 3.3 Query existing Fabric Capacity resource ID
    Write-Host "Resolving Fabric Capacity ID for '$capacityName'..."
    try {
        $capacityId = az fabric capacity show --resource-group $rgName --name $capacityName --query id -o tsv
        if ($capacityId) {
            Write-Host "Successfully resolved Fabric Capacity ID in Resource Group '$rgName': $capacityId"
        }
    } catch {
        # Fallback: search across all resource groups in the active subscription
        Write-Host "Capacity not found in Resource Group '$rgName'. Searching across all resource groups in active subscription..."
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
    
    if ([string]::IsNullOrEmpty($capacityId)) {
        Write-Error "Could not locate Fabric capacity '$capacityName' inside subscription '$subscriptionId'."
    }
} catch {
    Write-Error "Failed to locate the existing resource group '$rgName' or Fabric capacity '$capacityName' inside subscription '$subscriptionId'. Please verify they exist and that your CLI session has access."
}

# 6. Save Details back to config file
Write-Host "Writing Capacity ID to accelerator-config.json..."
$config.capacityId = $capacityId
$config.subscriptionId = $subscriptionId
$config.resourceGroup = $rgName
$config.location = $location

$jsonContent = ConvertTo-Json $config -Depth 10
Set-Content -Path $configPath -Value $jsonContent

Write-Host "--------------------------------------------------"
Write-Host "   Provisioning Completed Successfully!           "
Write-Host "   Capacity ID: $capacityId"
Write-Host "--------------------------------------------------"
