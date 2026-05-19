// =========================================================================
// Real-Time Banking Risk & Fraud Intelligence - Fabric Capacity Bicep
// =========================================================================
//
// Bicep template to provision a Microsoft Fabric Capacity (F-SKU) idempotently.

@description('The name of the Microsoft Fabric Capacity resource.')
param capacityName string

@description('The location where the Fabric Capacity will be provisioned.')
param location string = resourceGroup().location

@description('The SKU size for the Fabric Capacity. Standard trial/dev starts at F2.')
@allowed([
  'F2'
  'F4'
  'F8'
  'F16'
  'F32'
  'F64'
])
param skuName string = 'F2'

@description('An array of Entra ID user principal names (emails) to assign as capacity administrators.')
param adminMembers array

resource fabricCapacity 'Microsoft.Fabric/capacities@2022-07-01-preview' = {
  name: capacityName
  location: location
  sku: {
    name: skuName
    tier: 'Fabric'
  }
  properties: {
    administration: {
      members: adminMembers
    }
  }
}

@description('The resource ID of the newly created Microsoft Fabric Capacity.')
output capacityId string = fabricCapacity.id
