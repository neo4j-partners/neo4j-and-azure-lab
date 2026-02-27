#!/bin/bash
# Post-create script for Dev Container / Codespaces
# This runs once when the container is first created

set -e

echo "=========================================="
echo "Dev Container Post-Create Setup"
echo "=========================================="

# Install uv
echo "Installing uv..."
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"

# Sync project dependencies
echo "Installing project dependencies..."
uv sync --prerelease=allow

# Register the Jupyter kernel
echo "Registering Jupyter kernel..."
uv run python -m ipykernel install --user --name neo4j-azure-ai-workshop --display-name "Neo4j Azure AI Workshop"

# Set up nbstripout to strip notebook outputs before committing
echo "Setting up nbstripout..."
uv run nbstripout --install

echo "=========================================="
echo "Post-create setup complete!"
echo "=========================================="
