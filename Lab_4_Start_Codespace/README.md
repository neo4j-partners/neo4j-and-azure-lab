# Lab 4 - Start Codespace

In this lab, you will spin up a GitHub Codespace instance to use as your development environment for the coding labs in Part 2 of the workshop.

## Prerequisites

Before starting, make sure you have:
- Your **Azure Resource Group name** from Lab 0
- Your **Neo4j Aura credentials** (URI, username, password) from Lab 1

## Launch the Codespace

Click the buttons below to start your development environment:

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/neo4j-partners/neo4j-and-azure-lab)

## What is a GitHub Codespace?

A GitHub Codespace is a cloud-hosted development environment that runs in your browser. When you launch a Codespace, GitHub provisions a virtual machine with:

- A pre-configured VS Code editor
- All required tools and dependencies already installed (Python, Azure CLI, GitHub CLI)
- Extensions for Azure development, Python, and Jupyter notebooks
- A terminal with access to run commands

This means you don't need to install anything on your local machine—everything is ready to go in the cloud.

## Setup

Once your Codespace has started, it should open a file with setup instructions. You will be prompted to enter your secrets (Resource Group name, Neo4j credentials). After that, run the setup commands provided in the terminal to configure the Azure infrastructure for the remaining labs.

For reference, you can also view the complete setup instructions in [GUIDE_DEV_CONTAINERS.md](../GUIDE_DEV_CONTAINERS.md).

## Viewing Your Microsoft Foundry Project

After running the `azd up` commands in the codespace, it created a Microsoft Foundry project for you.

To view your Foundry project:

1. Go to https://ai.azure.com/

   ![Foundry Home Page](images/Foundry_Home_Page.png)

2. The deployment created two models:
   - **gpt-5.2** - for text generation
   - **text-embedding-ada-002** - for creating embeddings

   ![Foundry Models](images/Foundry_Models.png)

## Running the Notebooks

To run the Jupyter notebooks in the labs, you need to select the correct Python kernel:

1. Click **Select Kernel** in the top right of the notebook, then select **Python Environments...**

   ![Select Kernel](images/select%20kernel.png)

2. Select the **neo4j-azure-ai-workshop** environment (marked as Recommended)

   ![Select neo4j-azure-ai-workshop](images/neo4j-azure-ai-workshop.png)

## Alternative: Run GitHub Codespace in VS Code

If you are unable to run the Codespace in your browser (due to network restrictions, browser compatibility issues, or preference), you can open and run the Codespace directly in VS Code on your local machine.

**Quick Steps:**
1. Install [Visual Studio Code](https://code.visualstudio.com/)
2. Install the [GitHub Codespaces extension](https://marketplace.visualstudio.com/items?itemName=GitHub.codespaces): Open VS Code, click the Extensions icon in the sidebar (or press `Ctrl+Shift+X` / `Cmd+Shift+X`), search for "GitHub Codespaces", and click Install
3. Sign in to GitHub from VS Code (click the Accounts icon in the sidebar)
4. Open the Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`) and run "Codespaces: Connect to Codespace"
5. Select your running Codespace or create a new one

For detailed instructions, see GitHub's official documentation: [Using GitHub Codespaces in Visual Studio Code](https://docs.github.com/en/codespaces/developing-in-a-codespace/using-github-codespaces-in-visual-studio-code)

## Running Locally (Without a Codespace)

If you prefer to run the workshop on your local machine instead of using a Codespace, follow these steps:

### Prerequisites

Before starting, ensure you have:
- Windows 10/11, macOS, or Linux
- Administrator access on your machine
- An active Azure subscription
- Neo4j Aura credentials from Lab 1

### Step 1: Download the Project

1. Go to https://github.com/neo4j-partners/neo4j-and-azure-lab
2. Click the green "Code" button
3. Select "Download ZIP" (or clone with `git clone`)
4. Extract the ZIP file to a location on your computer

### Step 2: Install Python 3.12

This project requires Python 3.12 (not 3.13 or later).

1. Download Python 3.12 from https://www.python.org/downloads/
   - Select a **3.12.x** version (e.g., 3.12.7)
2. Run the installer:
   - **Windows**: Check "Add Python 3.12 to PATH", then click "Install Now"
   - **macOS/Linux**: Follow the installer prompts
3. Verify installation:
   ```bash
   python --version
   # Should output: Python 3.12.x
   ```

### Step 3: Install uv (Python Package Manager)

uv is a fast Python package installer used by this project.

```bash
pip install uv
uv --version
```

### Step 4: Install Azure CLI

The Azure CLI is required for authenticating with Azure.

- **Windows**: Download from https://aka.ms/installazurecliwindows
- **macOS**: `brew install azure-cli`
- **Linux**: See https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-linux

After installation, sign in:
```bash
az login
```

### Step 5: Install Azure Developer CLI (azd)

- **Windows**: `winget install microsoft.azd`
- **macOS**: `brew install azure/azd/azd`
- **Linux**: `curl -fsSL https://aka.ms/install-azd.sh | bash`

After installation, sign in:
```bash
azd auth login
```

### Step 6: Install Visual Studio Code

1. Download VS Code from https://code.visualstudio.com/
2. Install the **Python** and **Jupyter** extensions from the Extensions marketplace

### Step 7: Set Up the Project

1. Open the project folder in VS Code
2. Open a terminal and create the Python environment:
   ```bash
   uv sync
   ```
3. Select the Python interpreter:
   - Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on macOS)
   - Type "Python: Select Interpreter"
   - Choose the interpreter from the `.venv` folder

### Step 8: Configure Environment Variables

1. Copy the sample environment file:
   ```bash
   cp .env.sample .env
   ```
2. Edit `.env` and add your Neo4j credentials:
   ```
   NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
   NEO4J_USERNAME=neo4j
   NEO4J_PASSWORD=your-password-here
   ```

### Step 9: Deploy Azure Infrastructure

1. Initialize the Azure Developer environment:
   ```bash
   azd env new
   # Enter an environment name (e.g., "dev")
   ```

2. Set your Azure location and resource group:
   ```bash
   azd env set AZURE_LOCATION eastus2
   azd env set AZURE_RESOURCE_GROUP your-resource-group-name
   ```

3. Deploy the infrastructure:
   ```bash
   azd up
   ```

4. Sync Azure configuration to your `.env` file:
   ```bash
   uv run setup_env.py
   ```

### Step 10: Run the Notebooks

1. Navigate to a lab folder (e.g., `Lab_5_Knowledge_Graph`)
2. Open a notebook file (e.g., `01_data_loading.ipynb`)
3. Select the **neo4j-azure-ai-workshop** kernel when prompted
4. Run the notebook cells using `Shift+Enter`

### Troubleshooting

| Problem | Solution |
|---------|----------|
| Python version is not 3.12 | Ensure Python 3.12.x is installed and in your PATH |
| `uv` command not found | Close and reopen your terminal |
| Azure CLI authentication fails | Run `az logout` then `az login` again |
| `azd up` fails with region error | Use a supported region: eastus2, swedencentral, or westus2 |
| Jupyter kernel not found | Run `uv sync` again and restart VS Code |
| Import errors in notebooks | Ensure you've selected the correct Python interpreter from `.venv` |

## Next Steps

After completing this lab, continue to [Lab 5 - Building a Knowledge Graph](../Lab_5_Knowledge_Graph) to build your knowledge graph from SEC filings using entity extraction and embeddings.
