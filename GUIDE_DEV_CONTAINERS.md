# Dev Containers & Codespaces Quick Start Guide

> **Warning:** It may take several minutes for the Codespace to start. After it starts, please wait an additional couple of minutes for all post-install scripts to finish running.  You can tell when it is finished initalizing because the .env will be created in the root directory.
> 
> ![Wait for Environment to Finish Initializing](Lab_4_Start_Codespace/images/wait_finish_env.png)

> **Note:** The Codespace/Dev Container prepopulates the `.env` file in the project root with Neo4j connection settings. Review these values to ensure they are accurate for your environment. If running outside of a Codespace or Dev Container, you must manually set the Neo4j environment variables (`NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`) in your `.env` file.

### Setup Steps

1. **Run in terminal:**
   ```bash
   # Authenticate with Azure
   az login --use-device-code
   azd auth login --use-device-code

   # Select Azure region and initialize environment
   ./scripts/setup_azure.sh
  
   azd env set SKIP_ROLE_ASSIGNMENTS true
   
   # Deploy
   azd up
   ```

   > **Note:** The setup script clears the `.azure/` directory and Azure-related settings from `.env` to ensure a fresh deployment. Neo4j settings in `.env` are preserved. See [docs/AZ_CLI_GUIDE.md](docs/AZ_CLI_GUIDE.md) for details.
   
2. **Follow the prompts:**
   - **Resource group:** Select the resource group from the setup in Lab 0 and is the same as your Azure Username. 

3. ```
   ? Select an Azure Subscription: 1. Your Subscription
   ? Pick a resource group to use:
     1. Create a new resource group
   > 2. your-existing-resource-group
   ```

3. **View Deployed Models in Microsoft Foundry Portal:**

   This creates a Microsoft Foundry project with two model deployments: **gpt-5.2** (for chat completions) and **text-embedding-ada-002** (for vector embeddings). Open [ai.azure.com](https://ai.azure.com/) in the same browser where you're logged into Azure to view your project.

   Click **Models** in the left sidebar to see your deployments:

   ![Models Section](images/models_section.png)

4. **Setup environment:**
   ```bash
   uv run setup_env.py
   ```

6. Move on to Lab 5 - Building a Knowledge Graph: [Lab_5_Knowledge_Graph/README.md](Lab_5_Knowledge_Graph/README.md)