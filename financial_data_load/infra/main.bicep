// Infrastructure for Financial Data Load Workshop
// Deploys AI Services account, project, and model deployments

@minLength(1)
@maxLength(64)
@description('Environment name used to generate unique resource names')
param environmentName string

@description('Location for all resources')
param location string = resourceGroup().location

@description('Principal ID for role assignments')
param principalId string = ''

@description('Skip role assignments on redeployment')
param skipRoleAssignments bool = false

// Chat completion model
@description('Name of the chat model to deploy')
param chatModelName string = 'gpt-5.2'
@description('Version of the chat model to deploy')
param chatModelVersion string = '2025-12-11'
@description('SKU for the chat deployment')
param chatDeploymentSku string = 'GlobalStandard'
@description('Capacity for the chat deployment')
param chatDeploymentCapacity int = 20

// Embedding model
@description('Name of the embedding model to deploy')
param embeddingModelName string = 'text-embedding-ada-002'
@description('Version of the embedding model to deploy')
param embeddingModelVersion string = '2'
@description('SKU for the embedding deployment')
param embeddingDeploymentSku string = 'GlobalStandard'
@description('Capacity for the embedding deployment')
param embeddingDeploymentCapacity int = 120

param templateValidationMode bool = false
param seed string = newGuid()

var tags = { 'azd-env-name': environmentName }
var resourceToken = templateValidationMode
  ? toLower(uniqueString(resourceGroup().id, environmentName, seed))
  : toLower(uniqueString(resourceGroup().id, environmentName))
var runnerPrincipalType = templateValidationMode ? 'ServicePrincipal' : 'User'

// Storage account (required by AI Services)
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: 'st${resourceToken}'
  location: location
  tags: tags
  kind: 'StorageV2'
  sku: { name: 'Standard_LRS' }
  properties: {
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
  }
}

// AI Services account (Foundry resource)
resource aiServices 'Microsoft.CognitiveServices/accounts@2025-04-01-preview' = {
  name: 'ai-${resourceToken}'
  location: location
  tags: tags
  kind: 'AIServices'
  sku: { name: 'S0' }
  identity: { type: 'SystemAssigned' }
  properties: {
    allowProjectManagement: true
    customSubDomainName: 'ai-${resourceToken}'
    publicNetworkAccess: 'Enabled'
  }
}

// AI Project (for managing serverless endpoints)
resource aiProject 'Microsoft.CognitiveServices/accounts/projects@2025-04-01-preview' = {
  parent: aiServices
  name: 'proj-${resourceToken}'
  location: location
  tags: tags
  identity: { type: 'SystemAssigned' }
  properties: {
    displayName: 'Financial Data Load Project'
    description: 'Project for financial data workshop samples'
  }
}

// Chat model deployment (gpt-5.2)
resource chatDeployment 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
  parent: aiServices
  name: chatModelName
  properties: {
    model: {
      format: 'OpenAI'
      name: chatModelName
      version: chatModelVersion
    }
  }
  sku: {
    name: chatDeploymentSku
    capacity: chatDeploymentCapacity
  }
}

// Embedding model deployment (text-embedding-ada-002)
resource embeddingDeployment 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
  parent: aiServices
  name: embeddingModelName
  dependsOn: [chatDeployment] // Deploy sequentially to avoid conflicts
  properties: {
    model: {
      format: 'OpenAI'
      name: embeddingModelName
      version: embeddingModelVersion
    }
  }
  sku: {
    name: embeddingDeploymentSku
    capacity: embeddingDeploymentCapacity
  }
}

// Storage connection for AI Services
resource storageConnection 'Microsoft.CognitiveServices/accounts/connections@2025-04-01-preview' = {
  name: 'storage-connection'
  parent: aiServices
  properties: {
    category: 'AzureStorageAccount'
    target: storageAccount.properties.primaryEndpoints.blob
    authType: 'AAD'
    isSharedToAll: true
    metadata: {
      ApiType: 'Azure'
      ResourceId: storageAccount.id
    }
  }
}

// Role: Storage Blob Data Contributor for AI Services
resource aiStorageRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!skipRoleAssignments) {
  name: guid(resourceGroup().id, aiServices.id, 'storage-contributor')
  scope: storageAccount
  properties: {
    principalType: 'ServicePrincipal'
    principalId: aiServices.identity.principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe')
  }
}

// Role: Azure AI Developer for deploying user
resource userAIDeveloper 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!skipRoleAssignments && !empty(principalId)) {
  name: guid(resourceGroup().id, principalId, 'ai-developer')
  properties: {
    principalType: runnerPrincipalType
    principalId: principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '64702f94-c441-49e6-a78b-ef80e0188fee')
  }
}

// Role: Cognitive Services User for deploying user
resource userCognitiveServices 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!skipRoleAssignments && !empty(principalId)) {
  name: guid(resourceGroup().id, principalId, 'cognitive-services-user')
  properties: {
    principalType: runnerPrincipalType
    principalId: principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'a97b65f3-24c7-4388-baec-2e87135dc908')
  }
}

// Outputs for setup_env.py
output AZURE_RESOURCE_GROUP string = resourceGroup().name
output AZURE_TENANT_ID string = tenant().tenantId
output AZURE_AI_PROJECT_ENDPOINT string = aiProject.properties.endpoints['AI Foundry API']
output AZURE_AI_SERVICES_ENDPOINT string = aiServices.properties.endpoint

// Model deployment names
output AZURE_AI_MODEL_NAME string = chatDeployment.name
output AZURE_AI_EMBEDDING_NAME string = embeddingDeployment.name
