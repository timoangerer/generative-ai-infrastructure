# Generative AI Infrastructure

This projects is an example implementation of a backend cloud infrastructure designed to run open source generative AI models for image generation. It currently supports the Hugging Faces [Diffusers](https://huggingface.co/docs/diffusers/index) implementation for Stable Diffusion and runs on [AWS EKS](https://aws.amazon.com/eks/).

Significant advancements are being made daily in the development of generative AI models. However, there is a notable gap in resources and guidance on how to effectively implement and utilize these models for complex use cases and product integrations. This implementation demonstrates how to harness cloud computing features like horizontal scaling, GPU instances, and parallel processing to facilitate fast, cost-efficient, and reliable content generation.

The project serves as a starting point to incorporate generative AI model backend infrastructure into ones own cloud computing environment and products. It is not meant for direct use as-is; rather, it should be forked, modified, and integrated as necessary.

For production deployment, it is necessary to position the generation backend behind a proxy, load balancer, or API to manage service exposure and handle user authentication, etc. Also, the generation infrastructure is secured within its own Virtual Private Cloud (VPC) and requires explicit exposure as per specific needs.

# Requirements and limitations

The project currently supports deployment definitions for AWS Elastic Kubernetes Service (EKS) and local Minikube environments. Adapting these definitions for other cloud services is should be straightforward.

The worker service requires an NVIDIA GPU with a minimum of 8GB of VRAM to generate images.

For the deployment to AWS, a `g4dn.xlarge` instance is sufficient. It’s necessary to have a service quota of at least 4vCPUs for “Running On-Demand G and VT instances” to be able to request a GPU instance. This specific service quota is not enabled by default on AWS accounts and must be explicitly requested through AWS support.

For local deployment, a Linux machine equipped with an NVIDIA GPU and the appropriate drivers is necessary. Proper configuration of the GPU driver can be verified by checking the output of the **`nvidia-smi`** command.

# **Installation and Getting Started**

This guide outlines the steps to deploy the infrastructure to **AWS EKS**. For local deployment on Minikube, refer to the [“Deploy to Local Minikube Cluster”](#deploy-to-local-minikube-cluster) section.

## **Prerequisites**

Ensure you have the following tools installed:

- [Terraform](https://developer.hashicorp.com/terraform/install) for infrastructure as code management.
- [Kubectl](https://kubernetes.io/docs/tasks/tools/#kubectl) for interacting with the Kubernetes cluster.
- A configured cloud provider setup, such as AWS CLI credentials, to create resources on AWS.

## **Repository Setup**

Begin by cloning the repository and navigating to its root folder:

```bash
git clone git@github.com:timoangerer/generative-ai-infrastructure.git
cd generative-ai-infrastructure
```

## **Creating the Kubernetes Cluster**

Start by creating the Kubernetes cluster:

1. Navigate into the EKS terraform directory.
    
    ```bash
    cd infrastructure/terraform/eks
    ```
    
2. Initialize and apply the Terraform configuration:
    
    ```bash
    terraform init
    terraform apply
    ```
    
    Confirm the **`terraform apply`** command with "yes" when prompted.
    
    This process installs all necessary AWS and EKS resources. It typically takes 20 to 30 minutes. A successful deployment is indicated by the message “Apply complete!”.
    

## **Deploying Resources and Services into the Kubernetes Cluster**

With the Kubernetes cluster set up, the next step is to deploy the services into it:

1. Navigate to the production environment's Terraform project:
    
    ```bash
    cd infrastructure/terraform/environments/production
    ```
    
2. Initialize and deploy all resources and services with Terraform:
    
    ```bash
    terraform init
    terraform apply
    ```
    
    Confirm the **`terraform apply`** command with "yes" when prompted.
    
    This deployment takes around 10 minutes. A successful deployment is indicated by “Apply complete!”.
    

The infrastructure is now successfully deployed and ready for use or integration into your existing infrastructure setup.

## Verifing the installation

To ensure that the infrastructure is functioning correctly, follow these steps:

1. **Make the API Accessible Locally**:
    
    Run the following command to forward the API to your local machine on port 8000:
    
    ```bash
    kubectl port-forward $(kubectl get pods -l app=genai-api -o jsonpath='{.items[0].metadata.name}') 8000:8000
    ```
    
2. **Check API Accessibility**:
    
    Verify if the API is accessible and operational. The expected response should indicate **`status: ok`**.
    
    ```bash
    curl http://localhost:8000/health/
    ```
    
    The API documentation, detailing available endpoints and parameters, can be accessed at **`http://localhost:8000/docs`**.
    
3. **Send a Generation Request to the API**:
    
    Use the following command to send an image generation request:
    
    ```bash
    curl -v -X POST http://localhost:8000/images/ \
    -H "Content-Type: application/json" \
    -d '{
      "generation_settings": {
        "prompt": "A dog",
        "negative_prompt": "",
        "seed": 42,
        "sampler_name": "euler",
        "batch_size": "1",
        "n_iters": 1,
        "steps": 5,
        "cfg_scale": 7.0,
        "width": 512,
        "height": 512,
        "model": "DreamShaper_6"
      },
      "metadata": {
        "grouping": "test/grouping"
      }
    }'
    ```
    
    This request will return a response containing the ID of the generation job.
    
    **Example response**:
    
    ```json
    {
      "message": "Request is being processed",
      "id": "54e72518-c85a-4780-95ae-d46ee6879a15"
    }
    ```
    
4. **Poll the Generation Job**:
    
    Continuously poll the generation job using the job’s ID until the **`image_url`** and **`completion_time`** properties are populated.
    
    ```bash
    curl http://localhost:8000/images/<job-id>/
    ```
    
    **Example response**:
    
    ```json
    {
        "id": "f9da8db5-1451-4535-b3d7-05600d450c30",
        "metadata": {
          "grouping": "test/grouping"
        },
        "request_time": "2024-02-03T15:35:05.294000",
        "complete_time": "2024-02-03T15:35:33.285000",
        "generation_settings": {
          "prompt": "A dog",
          "negative_prompt": "",
          "seed": 42,
          "sampler_name": "asdf",
          "batch_size": 1,
          "n_iters": 1,
          "steps": 5,
          "cfg_scale": 7.0,
          "width": 512,
          "height": 512,
          "model": "DreamShaper_6"
        },
        "image_url": "genai-generated-images-1.s3.eu-central-1.amazonaws.com/f9da8db5-1451-4535-b3d7-05600d450c30.jpg"
      }
    ```
    

By following these steps, you can effectively test and confirm the proper functioning of your deployed infrastructure.

# Configuration

You can locate and modify most configuration variables in the **`variables.tf`** and **`terraform.tfvars`** files within the respective environment directory, located at **`infrastructure/terraform/environments/<env>/variables.tf`**.

### Configuring Apache Pulsar

The deployment settings for Apache Pulsar are managed through a **`config.yaml`** file. Specify your preferred configuration file in the **`pulsar_cluster_config_file`** parameter within the **`terraform.tfvars`** file. For a comprehensive list of configuration options, refer to the [official Apache Pulsar documentation](https://github.com/apache/pulsar-helm-chart?tab=readme-ov-file#customize-the-deployment).

### Compute Resources and Replicas

The configuration for compute resources and the number of replicas for each service are defined in their respective Kubernetes deployment/service configurations. For production environments, implementing an autoscaling solution such as [Karpenter](https://karpenter.sh/) is recommended for optimal scaling and management of compute resources.

### **Adding Stable Diffusion Model Checkpoints**

To add new stable diffusion model checkpoints:

1. Insert a new entry into the **`model_links`** array within the **`terraform.tfvars`** file. This will enable the download of the model.
    
    Example:
    
    ```bash
    model_links = [
    	...
      {
        url       = "https://link/to/model.safetensors"
        rename_to = "some_model.safetensors"
      }
    ]
    ```
    
2. Run **`terraform apply`** to initiate the download process. Note that existing models in the list will not be re-downloaded.

# Testing

This section covers the automated tests for the API service to verify the operational status of the deployed infrastructure.

## **Automated API Tests**

1. **Navigate to the Tests Directory**:
    
    ```bash
    cd infrastructure/infra_tests
    ```
    
2. **Install Dependencies**:
    
    ```bash
    pdm install
    ```
    
    Post-installation, the correct Python virtual environment should activate automatically.
    
3. **Set the API URL**:
    
    Ensure the API is accessible by setting the **`BASE_URL`** environment variable to the service's exposed URL. The default is **`http://localhost:8000`**.
    
4. **Run the tests:**
    
    ```bash
    BASE_URL="http://127.0.0.1:8000" pytest
    ```
    

## Load testing

The project includes a simple load testing setup to simulate multiple users sending requests to the API.

1. **Prepare for Load Testing**:
    
    Within the **`infrastructure/infra_tests`** directory and with the virtual environment activated, execute:
    
    ```bash
    BASE_URL="http://127.0.0.1:8000" locust -f locust/load_test.py
    ```
    
2. **Access the Locust Dashboard**:
    
    This command will open the Locust dashboard in your default web browser, where you can initiate the load test.
    

# Monitoring, observability, logging.

The project incorporates Prometheus, Grafana, and Signoz deployments with OpenTelemetry instrumentations for monitoring, logging, and observability.

## Access the Grafana Dashboard

1. **Forward Grafana Service to your local machine:**
    
    ```bash
    kubectl port-forward $(kubectl get pods -l app.kubernetes.io/name=grafana -o jsonpath='{.items[0].metadata.name}') 3000:3000
    ```
    
2. **Retrieve Grafana Password**:
    
    Use the following command to obtain the Grafana password:
    
    ```bash
    kubectl get secret -l app.kubernetes.io/name=grafana -o=jsonpath="{.items[0].data.admin-password}" | base64 --decode
    ```
    
3. **Access Grafana Dashboard:**
    
    Visit [http://localhost:3000](http://localhost:3000/). The default username is **`admin`.** Use the password from the previous step.
    

## Access the Signoz Dashboard

1. **Forward Signoz Frontend Service to your local machine**:
    
    ```bash
    kubectl port-forward $(kubectl get pods -l app.kubernetes.io/name=signoz -l app.kubernetes.io/component=frontend -o jsonpath='{.items[0].metadata.name}') 3301:3301
    ```
    
2. **Access Signoz Dashboard**:
    
    Visit [http://localhost:3301](http://localhost:3301/).
    

# Architecture

The architecture of this project is designed to run entirely within a Kubernetes cluster, configured and managed using Terraform. It leverages a combination of various technologies and patterns to ensure efficient, scalable, and reliable operations. Below is a detailed breakdown of the architecture:

![Diagram of the infrastructure.](Genai%20AI%20documentation%201988212a9bb2490ca8c9d16a3710f3bd/Untitled.png)

Diagram of the infrastructure.

## **Core Components**

1. **Kubernetes and Terraform**: The backbone of the infrastructure, providing a scalable and manageable environment for the deployment of services and resources.
2. **Apache Pulsar**: Utilized for event streams and message queues, facilitating communication between different services within the infrastructure.
3. **Trino and Apache Pulsar’s BookKeeper**: These technologies are used in place of a traditional database for data persistence and retrieval.
4. **REST API Service**: Serves as the primary interface for interacting with the infrastructure, processing requests and managing responses.
5. **Worker Nodes**: These are responsible for processing image generation jobs. They operate using an open-source implementation of the Stable Diffusion algorithm.
6. **Stable Diffusion Checkpoints**: Model checkpoints are stored on central volume and made accessible to the worker nodes.

The following paragraphs explain some select aspects in more detail.

## **Architecture Design**

The system is built following the principles of Event-Driven or Event Sourcing Architecture, where services communicate asynchronously through message streams/queues, either by publishing or subscribing to specific topics.

## **Messaging and Queue Management**

In the system, two key topics are employed. The **`requested_txt2img_generation`** topic manages image generation and processing jobs. It operates as a queue where each message is consumed only once, irrespective of the number of consumers. Accompanying this is the **`dlq_requested_txt2img_generation`**, a "dead letter queue" for error handling. Messages failing to process are retried up to three times before being moved to this dead letter queue, ensuring faulty messages do not clog the system by being retried indefinitely.

The second key topic, **`completed_txt2img_generation`**, is used for messages that include the job ID and the URL of the generated image. This topic facilitates tracking and accessing successfully completed image generation tasks.

## **Data Management**

All data is stored within the event sourcing system, specifically in the messages and their respective topics, eliminating the need for a traditional database. Messages are thus persisted indefinitely. For querying this data, Trino, a distributed SQL query engine, is used. It interacts with the data in the Pulsar cluster, especially with the Apache Bookkeeper ledger. Once set up for Bookkeeper, Trino SDK facilitates the execution of SQL queries, aggregating data from all topics.

## **Worker Service Design**

The worker service, tasked with processing image generation requests, operates by consuming messages from the queue and generating images as per the settings specified in each message. Deployed as a single unit (pod), it internally comprises two distinct containers.

One container, the “sidecar”, manages interactions with the message queues and the storage of images. The other container is dedicated to actual image generation, employing the stable diffusion algorithm. It processes the generation settings and outputs the final image. These containers communicate via RPC/HTTP.

The dual-container setup offers several benefits. It segregates the bulky and complex dependencies of machine learning algorithms, simplifying management and troubleshooting. This structure also allows for the flexible swapping and updating of the stable diffusion algorithm implementation without modifying the sidecar container. Additionally, it facilitates the incremental addition of new stable diffusion implementations, each in its own container.

## **Static Resources**

Pre-trained machine learning models are stored on an AWS EFS drive and accessed by worker nodes via PV and PVC in ReadOnlyMany mode. These models are listed in a config file and downloaded during cluster setup or when adding new models.

Static Apache Pulsar resources, including tenants, namespaces, and topics, are defined using Terraform and automatically created in the initial cluster setup through a Kubernetes job.

# **How to contribute**

Thank you for taking interest in contributing to the project. Every contribution, no matter how small, is immensely valuable.

### **Prerequisites**

For local development, make sure you have Python3, [Python PDM](https://pdm-project.org/latest/#installation) and [Docker](https://docs.docker.com/engine/install/) installed, in addition to the deployment tools mentioned in the [“Installation and getting started”](#installation-and-getting-started) section. 

### **Setting Up the Development Environment**

1. **Fork the Repository**: Click on the 'Fork' button at the top right of this page to create a copy of this repository in your GitHub account.
2. **Clone Your Fork**: Run `**git clone https://github.com/timoangerer/generative-ai-infrastructure.git`** to clone your fork to your local machine.
3. **Create a New Branch**: Before making changes, create a new branch by running **`git checkout -b your-branch-name`**.
4. **Install Dependencies**: Navigate to the specific sub-project you would like to work on and run **`pdm install`** to install necessary dependencies.
5. Check the sub-project specific `README` file for additional information, such as on how to build the docker image, etc.

### Deploy to local minikube cluster

Deploying the infrastructure locally to minikube requires a linux machine (tested with Ubuntu 22.04) with a NVIDIA GPU with a minimum of 8GB VRAM.

Install [minikube](https://minikube.sigs.k8s.io/docs/start/) version v1.32.0 or above. This is essential for GPU support.

Follow the [minikube docs instructions for enabling GPU support](https://minikube.sigs.k8s.io/docs/start/). Create a cluster as instructed:

```bash
minikube start --driver docker --container-runtime docker --gpus all
```

From the project root folder, navigate to the development terraform definition:

```bash
cd terraform/environments/development
```

Initialize the terraform project and deploy all resources and services. Answer the `terraform apply` command with “yes” as instructed.

```bash
terraform init
terraform apply
```

If prompted for AWS credentials, add key and secret that have permission to write to the specified S3 bucket.

This should take around 15-20 minutes to deploy. Once terraform completes successfully, the infrastructure is deployed locally.

Follow the instructions under "Verify your installation” to test the infrastructure.

### **Finding Issues to Work On**

Looking for something to contribute to? Check out the issues labeled as **`good first issue`** or **`help wanted`**. These are great starting points for your first contribution.

### **Making a Contribution**

1. **Make Your Changes**: Work on the issue or improvement in your local environment.
2. **Test Your Changes**: Ensure your changes don't break any existing functionality.
3. **Commit Your Changes**: Commit your changes with a clear and descriptive commit message.
4. **Push Your Changes**: Push your changes to your fork with **`git push origin your-branch-name`**.
5. **Submit a Pull Request**: Go to your fork on GitHub and click **`New Pull Request`**. Fill in the PR template with information about your changes.

### **Style Guide and Conventions**

To maintain code quality and consistency, we follow the Python [PEP 8](https://peps.python.org/pep-0008/) style guide. Please ensure your contributions adhere to these guidelines. Consider using the [autopep8](https://github.com/hhatto/autopep8) formatter in your IDE of choice, as it’s installed as development dependency already.

### **Review Process**

Once you submit a pull request:

- Project maintainers will review your submission, providing feedback or suggestions.
- If everything looks good, a maintainer will merge your changes into the main codebase.

### **Getting Help**

If you have any questions or need help, feel free to reach out in github issues or via comments or mentions on github.

### **Acknowledgments**

Your contributions will be publicly acknowledged in our [Contributors List/Release Notes].