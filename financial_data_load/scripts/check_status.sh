#!/bin/bash
# Check the status of the current Azure project and resource group.
# Reports: azd environment, Azure subscription, resource group, and deployed resources.

set -euo pipefail

echo "=== Azure Project Status ==="
echo ""

# --- Azure CLI login status ---
echo "-- Azure CLI Account --"
if az account show --query '{Subscription:name, SubscriptionId:id, Tenant:tenantId}' -o table 2>/dev/null; then
    echo ""
else
    echo "  Not logged in. Run: az login --use-device-code"
    echo ""
fi

# --- azd environment ---
echo "-- azd Environment --"
AZD_ENV=$(azd env list --output json 2>/dev/null | python3 -c "
import json, sys
envs = json.load(sys.stdin)
for e in envs:
    if e.get('IsDefault'):
        print(e['Name'])
        break
" 2>/dev/null || true)

if [ -n "$AZD_ENV" ]; then
    echo "  Active environment: $AZD_ENV"

    # Get key values from the azd environment
    ENV_VALUES=$(azd env get-values -e "$AZD_ENV" 2>/dev/null || true)

    AZURE_LOCATION=$(echo "$ENV_VALUES" | grep '^AZURE_LOCATION=' | cut -d'=' -f2 | tr -d '"')
    AZURE_RG=$(echo "$ENV_VALUES" | grep '^AZURE_RESOURCE_GROUP=' | cut -d'=' -f2 | tr -d '"')
    AZURE_PROJECT_ENDPOINT=$(echo "$ENV_VALUES" | grep '^AZURE_AI_PROJECT_ENDPOINT=' | cut -d'=' -f2 | tr -d '"')

    [ -n "$AZURE_LOCATION" ] && echo "  Location: $AZURE_LOCATION"
    [ -n "$AZURE_PROJECT_ENDPOINT" ] && echo "  AI Project Endpoint: $AZURE_PROJECT_ENDPOINT"
    echo ""

    # --- Resource Group status ---
    echo "-- Resource Group --"
    if [ -n "$AZURE_RG" ]; then
        echo "  Name: $AZURE_RG"
        if az group show --name "$AZURE_RG" -o json 2>/dev/null | python3 -c "
import json, sys
rg = json.load(sys.stdin)
print(f\"  State: {rg.get('properties', {}).get('provisioningState', 'Unknown')}\")
print(f\"  Location: {rg.get('location', 'Unknown')}\")
" 2>/dev/null; then
            echo ""

            # --- Deployed resources ---
            echo "-- Deployed Resources --"
            az resource list --resource-group "$AZURE_RG" \
                --query '[].{Name:name, Type:type, Location:location}' \
                -o table 2>/dev/null || echo "  Unable to list resources."
        else
            echo "  Resource group not found in Azure (not yet deployed or already deleted)."
        fi
    else
        echo "  No resource group set (run 'azd up' to deploy)."
    fi
else
    echo "  No azd environment configured."
    echo "  Run: bash scripts/setup_azure.sh"
fi

echo ""
echo "=== End Status ==="
