// Resource group scoped deployment - requires pre-existing resource group
// See RESOURCE_GROUP_SCOPED_DEPLOYMENT.md for details

@minLength(1)
@maxLength(64)
@description('Name of the the environment which is used to generate a short unique hash used in all resources.')
param environmentName string

@description('Location for all resources. Defaults to resource group location.')
param location string = resourceGroup().location

@description('The Microsoft Foundry Hub resource name. If ommited will be generated')
param aiProjectName string = ''
@description('The Microsoft Foundry Services resource name. If ommited will be generated')
param aiServicesName string = ''
@description('The Azure Storage Account resource name. If ommited will be generated')
param storageAccountName string = ''
@description('Id of the user or app to assign application roles')
param principalId string = ''

// Chat completion model
@description('Format of the chat model to deploy')
@allowed(['Microsoft', 'OpenAI'])
param agentModelFormat string = 'OpenAI'
@description('Name of agent to deploy')
param agentName string = 'arches-agent'
@description('Name of the chat model to deploy')
param agentModelName string = 'gpt-5.2'
@description('Name of the model deployment')
param agentDeploymentName string = 'gpt-5.2'

@description('Version of the chat model to deploy')
param agentModelVersion string = '2025-12-11'

@description('Sku of the chat deployment')
param agentDeploymentSku string = 'Standard'

@description('Capacity of the chat deployment (TPM in thousands)')
param agentDeploymentCapacity int = 20

// Embedding model
@description('Format of the embedding model to deploy')
@allowed(['Microsoft', 'OpenAI'])
param embeddingModelFormat string = 'OpenAI'
@description('Name of the embedding model to deploy')
param embeddingModelName string = 'text-embedding-ada-002'
@description('Name of the embedding model deployment')
param embeddingDeploymentName string = 'text-embedding-ada-002'
@description('Version of the embedding model to deploy')
param embeddingModelVersion string = '2'
@description('Sku of the embedding deployment')
param embeddingDeploymentSku string = 'Standard'
@description('Capacity of the embedding deployment')
param embeddingDeploymentCapacity int = 5

param templateValidationMode bool = false

@description('Skip role assignments (set to true on redeployment if you get RoleAssignmentExists errors)')
param skipRoleAssignments bool = false

@description('Deploy Container App infrastructure (set to true for production deployment)')
param deployContainerApp bool = false

@description('Random seed to be used during generation of new resources suffixes.')
param seed string = newGuid()

var runnerPrincipalType = templateValidationMode? 'ServicePrincipal' : 'User'

var abbrs = loadJsonContent('./abbreviations.json')

// Use resource group name + environment for uniqueness (no subscription ID needed)
var resourceToken = templateValidationMode
  ? toLower(uniqueString(resourceGroup().id, environmentName, seed))
  : toLower(uniqueString(resourceGroup().id, environmentName))

var tags = { 'azd-env-name': environmentName }

var aiChatModel = [
  {
    name: agentDeploymentName
    model: {
      format: agentModelFormat
      name: agentModelName
      version: agentModelVersion
    }
    sku: {
      name: agentDeploymentSku
      capacity: agentDeploymentCapacity
    }
  }
]

var aiEmbeddingModel = [
  {
    name: embeddingDeploymentName
    model: {
      format: embeddingModelFormat
      name: embeddingModelName
      version: embeddingModelVersion
    }
    sku: {
      name: embeddingDeploymentSku
      capacity: embeddingDeploymentCapacity
    }
  }
]

var aiDeployments = concat(aiChatModel, aiEmbeddingModel)

// AI environment (deploys within current resource group)
module ai 'core/host/ai-environment.bicep' = {
  name: 'ai'
  params: {
    location: location
    tags: tags
    storageAccountName: !empty(storageAccountName)
      ? storageAccountName
      : '${abbrs.storageStorageAccounts}${resourceToken}'
    aiServicesName: !empty(aiServicesName) ? aiServicesName : 'aoai-${resourceToken}'
    aiProjectName: !empty(aiProjectName) ? aiProjectName : 'proj-${resourceToken}'
    aiServiceModelDeployments: aiDeployments
    // Monitoring enabled
    logAnalyticsName: 'log-${resourceToken}'
    applicationInsightsName: 'appi-${resourceToken}'
    appInsightConnectionName: 'appinsights-connection'
    // No search
    searchServiceName: ''
    aoaiConnectionName: 'aoai-connection'
    skipRoleAssignments: skipRoleAssignments
  }
}

var openAIEndpoint = ai.outputs.openAIEndpoint
var aiProjectEndpoint = ai.outputs.aiProjectEndpoint

// Container apps host (including container registry)
module containerApps 'core/host/container-apps.bicep' = if (deployContainerApp) {
  name: 'container-apps'
  params: {
    name: 'app'
    location: location
    containerRegistryName: '${abbrs.containerRegistryRegistries}${resourceToken}'
    tags: tags
    containerAppsEnvironmentName: 'containerapps-env-${resourceToken}'
    logAnalyticsWorkspaceName: '' // No Log Analytics
  }
}

// API app
module api 'api.bicep' = if (deployContainerApp) {
  name: 'api'
  params: {
    name: 'ca-api-${resourceToken}'
    location: location
    tags: tags
    identityName: '${abbrs.managedIdentityUserAssignedIdentities}api-${resourceToken}'
    containerAppsEnvironmentName: containerApps.outputs.environmentName
    containerRegistryName: containerApps.outputs.registryName
    azureAIProjectEndpoint: aiProjectEndpoint
    azureOpenAIEndpoint: openAIEndpoint
    azureModelDeploymentName: agentDeploymentName
    agentName: agentName
    skipRoleAssignment: skipRoleAssignments
  }
}

// Role assignments for the deploying user (skip on redeployment if needed)
module userRoleAzureAIDeveloper 'core/security/role.bicep' = if (!skipRoleAssignments) {
  name: 'user-role-azureai-developer'
  params: {
    principalType: runnerPrincipalType
    principalId: principalId
    roleDefinitionId: '64702f94-c441-49e6-a78b-ef80e0188fee' // Microsoft Foundry Developer
  }
}

module userCognitiveServicesUser 'core/security/role.bicep' = if (!skipRoleAssignments) {
  name: 'user-role-cognitive-services-user'
  params: {
    principalType: runnerPrincipalType
    principalId: principalId
    roleDefinitionId: 'a97b65f3-24c7-4388-baec-2e87135dc908' // Cognitive Services User
  }
}

module userAzureAIUser 'core/security/role.bicep' = if (!skipRoleAssignments) {
  name: 'user-role-azure-ai-user'
  params: {
    principalType: runnerPrincipalType
    principalId: principalId
    roleDefinitionId: '53ca6127-db72-4b80-b1b0-d745d6d5456d' // Microsoft Foundry User
  }
}

// Role assignments for the API backend (managed identity)
module backendAzureAIUser 'core/security/role.bicep' = if (!skipRoleAssignments && deployContainerApp) {
  name: 'backend-role-azure-ai-user'
  params: {
    principalType: 'ServicePrincipal'
    principalId: api.outputs.SERVICE_API_IDENTITY_PRINCIPAL_ID
    roleDefinitionId: '53ca6127-db72-4b80-b1b0-d745d6d5456d' // Microsoft Foundry User
  }
}

module backendCognitiveServicesUser 'core/security/role.bicep' = if (!skipRoleAssignments && deployContainerApp) {
  name: 'backend-role-cognitive-services-user'
  params: {
    principalType: 'ServicePrincipal'
    principalId: api.outputs.SERVICE_API_IDENTITY_PRINCIPAL_ID
    roleDefinitionId: 'a97b65f3-24c7-4388-baec-2e87135dc908' // Cognitive Services User
  }
}

module backendRoleAzureAIDeveloper 'core/security/role.bicep' = if (!skipRoleAssignments && deployContainerApp) {
  name: 'backend-role-azureai-developer'
  params: {
    principalType: 'ServicePrincipal'
    principalId: api.outputs.SERVICE_API_IDENTITY_PRINCIPAL_ID
    roleDefinitionId: '64702f94-c441-49e6-a78b-ef80e0188fee' // Microsoft Foundry Developer
  }
}

output AZURE_RESOURCE_GROUP string = resourceGroup().name

// Outputs required for local development server (Agent Framework with Foundry)
output AZURE_TENANT_ID string = tenant().tenantId
output AZURE_AI_PROJECT_ENDPOINT string = aiProjectEndpoint
output AZURE_AI_MODEL_NAME string = agentDeploymentName
output AZURE_AI_EMBEDDING_NAME string = embeddingDeploymentName
output AZURE_AI_AGENT_NAME string = agentName
// Legacy endpoint (for fallback or direct OpenAI access)
output AZURE_OPENAI_ENDPOINT string = openAIEndpoint

// Outputs required by azd for ACA (empty when deployContainerApp=false)
output AZURE_CONTAINER_ENVIRONMENT_NAME string = deployContainerApp ? containerApps.outputs.environmentName : ''
output SERVICE_API_IDENTITY_PRINCIPAL_ID string = deployContainerApp ? api.outputs.SERVICE_API_IDENTITY_PRINCIPAL_ID : ''
output SERVICE_API_NAME string = deployContainerApp ? api.outputs.SERVICE_API_NAME : ''
output SERVICE_API_URI string = deployContainerApp ? api.outputs.SERVICE_API_URI : ''
output SERVICE_API_ENDPOINTS array = deployContainerApp ? ['${api.outputs.SERVICE_API_URI}'] : []
output AZURE_CONTAINER_REGISTRY_ENDPOINT string = deployContainerApp ? containerApps.outputs.registryLoginServer : ''
