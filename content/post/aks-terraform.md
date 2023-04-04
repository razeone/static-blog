---
title: "Deploying an Azure Kubernetes cluster with Terraform"
date: 2023-04-03T17:56:40-06:00
Description: "I'll show you how to deploy an Azure Kubernetes cluster for testing with Terraform"
Tags: ["kubernetes", "terraform", "azure"]
Categories: ["kubernetes", "terraform", "azure"]
Thumbnail: "images/aks.png"
DisableComments: true
---

Hello reader, Jorge here. In this post I will be showing you how to deploy an Azure Kubernetes cluster with Terraform. I will be using the following technology stack so you better be prepared with the tools installed and working properly:

Terraform is an awesome open source tool that helps developers automate the provisioning of cloud infrastructure and objects, such as virtual machines, storage, networks, and more. It is a tool that allows you to define your infrastructure as code and deploy it to the cloud provider of your choice

I like a lot to use IaC since provides an alternative to manually deploying infrastructure, automation of the creation and destruction of resources, and the ability to version control your infrastructure. It also allows you to easily share your infrastructure with your team and collaborate on it.

Drawbacks of using IaC tools like Terraform is that it requires a lot of knowledge about the cloud provider's API and the tool itself. It also requires a lot of time to learn how to use it properly. However, once you get the hang of it, it is a very powerful tool that can help you automate your infrastructure and save you a lot of time.

Azure, AWS and GCP provide IaC tools as well, however, they use JSON as the configuration language. Terraform uses a configuration language called HCL (HashiCorp Configuration Language). HCL is a declarative language that is easy to read and write. It is also very similar to JSON, so if you have experience with JSON, you will be able to pick up HCL very quickly.

## Prerequisites

Before we start, we need to make sure that we have the following tools installed and working properly:

- Terraform
- Azure CLI
- Azure account

## Terraform

Terraform is an open-source infrastructure as code software tool created by HashiCorp. Users define and provide data center infrastructure using a declarative configuration language known as HashiCorp Configuration Language, or optionally JSON. Terraform can manage existing and popular service providers as well as custom in-house solutions.

Install terraform instructions can be found [here](https://learn.hashicorp.com/tutorials/terraform/install-cli).

## Azure CLI

The Azure CLI is a set of commands used to create and manage Azure resources. The Azure CLI is available across many platforms including Windows, macOS, and Linux. It is available as a downloadable standalone binary for Windows, macOS, and Linux, and as a package for many Linux distributions.

Install Azure CLI instructions can be found [here](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli).

## Azure account

You will need an Azure account to deploy the resources. If you don't have one, you can create a free account [here](https://azure.microsoft.com/en-us/free/).

## Deploying the cluster

Now that we have all the tools installed and working properly, we can start deploying the cluster. First, we need to create a service principal that will be used by Terraform to deploy the resources. We can do this by running the following command:

```bash
az ad sp create-for-rbac --name "terraform" --role="Contributor" --scopes="/subscriptions/<SUBSCRIPTION_ID>"
```

This command will create a service principal with the name "terraform" and assign the "Contributor" role to it. The output of the command will look like this:

```json
{
  "appId": "00000000-0000-0000-0000-000000000000",
  "displayName": "terraform",
  "name": "http://terraform",
  "password": "00000000-0000-0000-0000-000000000000",
  "tenant": "00000000-0000-0000-0000-000000000000"
}
```

We will need the values of the "appId" and "password" keys to configure Terraform. We can also get the subscription ID by running the following command:

```bash

az account show --query id --output tsv

```

Now that we have the service principal created, we can start deploying the cluster. First, we need to create a file called "terraform.tfvars" and add the following variables:

```hcl
aks_service_principal_app_id = "00000000-0000-0000-0000-000000000000"
aks_service_principal_client_secret = "00000000-0000-0000-0000-000000000000"
```

The values of these variables are the "appId" and "password" values of the service principal that we created earlier.

First, we need to create a file called "providers.tf" and add the following variables:

```hcl
terraform {
  required_version = ">=1.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~>3.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~>3.0"
    }
  }
}

provider "azurerm" {
  features {}
}
```

Now we can create a file called "main.tf" and add the following code:

```hcl
# Generate random resource group name
resource "random_pet" "rg_name" {
  prefix = var.resource_group_name_prefix
}

resource "azurerm_resource_group" "rg" {
  location = var.resource_group_location
  name     = random_pet.rg_name.id
}

resource "random_id" "log_analytics_workspace_name_suffix" {
  byte_length = 8
}

resource "azurerm_log_analytics_workspace" "log_analytics_workspace" {
  location = var.log_analytics_workspace_location
  # The WorkSpace name has to be unique across the whole of azure;
  # not just the current subscription/tenant.
  name                = "${var.log_analytics_workspace_name}-${random_id.log_analytics_workspace_name_suffix.dec}"
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = var.log_analytics_workspace_sku
}

resource "azurerm_log_analytics_solution" "log_analytics_solution" {
  location              = azurerm_log_analytics_workspace.log_analytics_workspace.location
  resource_group_name   = azurerm_resource_group.rg.name
  solution_name         = "ContainerInsights"
  workspace_name        = azurerm_log_analytics_workspace.log_analytics_workspace.name
  workspace_resource_id = azurerm_log_analytics_workspace.log_analytics_workspace.id

  plan {
    product   = "OMSGallery/ContainerInsights"
    publisher = "Microsoft"
  }
}

resource "azurerm_kubernetes_cluster" "k8s" {
  location            = azurerm_resource_group.rg.location
  name                = var.cluster_name
  resource_group_name = azurerm_resource_group.rg.name
  dns_prefix          = var.dns_prefix
  tags = {
    Environment = "Development"
  }

  default_node_pool {
    name       = "agentpool"
    vm_size    = "Standard_D2_v2"
    node_count = var.agent_count
  }
  linux_profile {
    admin_username = "ubuntu"

    ssh_key {
      key_data = file(var.ssh_public_key)
    }
  }
  network_profile {
    network_plugin    = "kubenet"
    load_balancer_sku = "standard"
  }
  service_principal {
    client_id     = var.aks_service_principal_app_id
    client_secret = var.aks_service_principal_client_secret
  }
}
```

Now let's create a file called "variables.tf" and add the following code:

```hcl
variable "agent_count" {
  default = 3
}

# The following two variable declarations are placeholder references.
# Set the values for these variable in terraform.tfvars
variable "aks_service_principal_app_id" {
  default = ""
}

variable "aks_service_principal_client_secret" {
  default = ""
}

variable "cluster_name" {
  default = "k8stest"
}

variable "dns_prefix" {
  default = "k8stest"
}

# Refer to https://azure.microsoft.com/global-infrastructure/services/?products=monitor for available Log Analytics regions.
variable "log_analytics_workspace_location" {
  default = "eastus"
}

variable "log_analytics_workspace_name" {
  default = "testLogAnalyticsWorkspaceName"
}

# Refer to https://azure.microsoft.com/pricing/details/monitor/ for Log Analytics pricing
variable "log_analytics_workspace_sku" {
  default = "PerGB2018"
}

variable "resource_group_location" {
  default     = "eastus"
  description = "Location of the resource group."
}

variable "resource_group_name_prefix" {
  default     = "rg"
  description = "Prefix of the resource group name that's combined with a random ID so name is unique in your Azure subscription."
}

variable "ssh_public_key" {
  default = "~/.ssh/id_rsa.pub"
}
```

Now, we can create a file called "outputs.tf" and add the following code:

```hcl
output "client_certificate" {
  value     = azurerm_kubernetes_cluster.k8s.kube_config[0].client_certificate
  sensitive = true
}

output "client_key" {
  value     = azurerm_kubernetes_cluster.k8s.kube_config[0].client_key
  sensitive = true
}

output "cluster_ca_certificate" {
  value     = azurerm_kubernetes_cluster.k8s.kube_config[0].cluster_ca_certificate
  sensitive = true
}

output "cluster_password" {
  value     = azurerm_kubernetes_cluster.k8s.kube_config[0].password
  sensitive = true
}

output "cluster_username" {
  value     = azurerm_kubernetes_cluster.k8s.kube_config[0].username
  sensitive = true
}

output "host" {
  value     = azurerm_kubernetes_cluster.k8s.kube_config[0].host
  sensitive = true
}

output "kube_config" {
  value     = azurerm_kubernetes_cluster.k8s.kube_config_raw
  sensitive = true
}

output "resource_group_name" {
  value = azurerm_resource_group.rg.name
}
```


This code will create a resource group, a log analytics workspace, a log analytics solution and an AKS cluster. We can now run the following command to firs validate the files, give them some format, validate the plan and deploy the cluster:

```bash
# Initialize the Terraform working directory
terraform init
# Validate the Terraform files
terraform validate
# Format the Terraform files
terraform fmt *.tf
# Create an execution plan
terraform plan -out=plan.out
# Deploy the cluster
terraform apply plan.out
```

You can now destroy your cluster if is not needed anymore:

```bash
terraform destroy
```

## Conclusion

In this article, we have seen how to create an AKS cluster using Terraform. We have also seen how to create a log analytics workspace and a log analytics solution to monitor the cluster. We have also seen how to create a service principal to be used by the cluster. We have also seen how to create a resource group to host the cluster and the log analytics workspace. We have also seen how to create a random name for the resource group and the log analytics workspace. We have also seen how to create a random suffix for the log analytics workspace name. We have also seen how to create a random pet name for the resource group.

