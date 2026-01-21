# Online Shop Activity Analysis

This project implements an end-to-end data pipeline for analyzing online shopping behavior. It uses **Terraform** to provision Azure infrastructure and **Databricks** for ETL processing and visualization.

## Prerequisites

Before running the project, ensure you have the following installed locally:

- [Git](https://git-scm.com/downloads)
- [Terraform](https://developer.hashicorp.com/terraform/downloads)
- [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli) (required for authentication)

## How to Run

### 1. Provision Infrastructure

Clone the repository and use Terraform to set up the required Azure resources.

```bash
# Clone the repository
git clone https://github.com/mrowki35/Online-shop-activity-analysis.git

# Navigate to the infrastructure directory
cd Online-shop-activity-analysis/iac

# Login to Azure (required for Terraform to access your subscription)
az login

# Initialize and apply Terraform configuration
terraform init
terraform plan
terraform apply
```

### 2. Generate Real-time Data

Once the infrastructure is ready, start the Python script to send mock clickstream data.

- Install Dependencies
The script requires external libraries to connect to Azure Event Hub and manage environment variables.

```bash
# Install required Python packages
pip install azure-eventhub python-dotenv
```

- Run the Generator

```bash
# Navigate to the data generator directory (relative to the 'iac' folder)
cd ../data_generator

python mock_data.py
```

## Run Data Pipelines
Once the infrastructure is deployed, execute the pipelines in the Azure Databricks workspace:

- Go to the Azure Portal and open the Azure Databricks resource created by Terraform.

- Launch the Databricks Workspace.

- Ingest and Process Data: Open the medallion_pipeline notebook. Click Run All to ingest and process the data through Bronze, Silver, and Gold layers.

## Analytics & Visualization
To view the results:

* Open the `dashboard_visualization` notebook in Databricks.
* Run the cells to view key metrics, including:
  * Total Sessions & Revenue
  * Cart Abandonment Rates
  * Top Users by Lifetime Value
