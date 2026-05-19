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
$configPath = Join-Path $PSScriptRoot "..`config`accelerator-config.json"
if (-not (Test-Path $configPath)) {
    $configPath = Join-Path $PSScriptRoot "config`accelerator-config.json"
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

$subscriptionId = $config.subscriptionId
$rgName = $config.resourceGroup
$capacityName = $config.capacityName
$location = $config.location
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

# 3. Verify or Create Resource Group
Write-Host "Checking if Resource Group '$rgName' exists..."
$rgExists = $false
try {
    az group show --name $rgName -o none
    $rgExists = $true
    Write-Host "Resource Group '$rgName' already exists."
} catch {
    Write-Host "Resource Group '$rgName' not found. Creating in location '$location'..."
    az group create --name $rgName --location $location -o table
    Write-Host "Resource Group created successfully."
}

# 4. Install az fabric extension if missing
Write-Host "Ensuring Microsoft Fabric CLI extension is installed..."
$extensions = az extension list --query "[].name" -o json | ConvertFrom-Json
if ("microsoft-fabric" -notin $extensions) {
    Write-Host "Installing microsoft-fabric extension..."
    az extension add --name microsoft-fabric -y
} else {
    Write-Host "microsoft-fabric extension is already installed."
}

# 5. Verify or Create Fabric Capacity (Sku: F2)
Write-Host "Checking if Fabric Capacity '$capacityName' exists in '$rgName'..."
$capacityId = ""
$capacityExists = $false
try {
    $capShow = az resource show --resource-group $rgName --name $capacityName --resource-type "Microsoft.Fabric/capacities" --query "id" -o tsv
    if (-not [string]::IsNullOrEmpty($capShow)) {
        $capacityId = $capShow
        $capacityExists = $true
        Write-Host "Fabric Capacity '$capacityName' already exists."
    }
} catch {
    # Resource doesn't exist, proceed to create
}

if (-not $capacityExists) {
    Write-Host "Fabric Capacity '$capacityName' not found. Deploying new F2 Capacity in '$location'..."
    Write-Host "This process may take 1-3 minutes..."
    
    if (-not [string]::IsNullOrEmpty($adminUser)) {
        $capCreate = az fabric capacity create --name $capacityName --resource-group $rgName --sku $sku --location $location --admin-members $adminUser --query "id" -o tsv
    } else {
        # Fallback if user retrieval failed
        $capCreate = az fabric capacity create --name $capacityName --resource-group $rgName --sku $sku --location $location --query "id" -o tsv
    }
    
    $capacityId = $capCreate
    Write-Host "Fabric Capacity created successfully!"
}

# 6. Save Details back to config file
Write-Host "Writing Capacity ID to accelerator-config.json..."
$config.capacityId = $capacityId
$config.subscriptionId = $subscriptionId

$jsonContent = ConvertTo-Json $config -Depth 10
Set-Content -Path $configPath -Value $jsonContent

Write-Host "--------------------------------------------------"
Write-Host "   Provisioning Completed Successfully!           "
Write-Host "   Capacity ID: $capacityId"
Write-Host "--------------------------------------------------"
