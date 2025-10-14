# FinBrain (Nadav Eshed) - AWS Studies Stage 2 - EKS Cluster Setup + kubectl
# (WATCH MORE on aws-infra branch on github)


# 0. Some Definitions

## What Is Kubernetes?
- Kubernetes (often called K8s) is a system that helps you:
- Run your apps in the cloud.
- Manage your containers (like the ones I made with Docker).
- Automatically restart, scale, and organize them.
- I can think of Kubernetes like an operating system for the cloud - it helps many computers work together to run my app reliably.

## Why Use Kubernetes? (Key Benefits)
- **Self-Healing =** If my app crashes, Kubernetes automatically restarts it - I don't need to do anything.
- **Load Balancing =** It can spread traffic across multiple copies of my app, so everything runs smoothly even with many users.
- **Auto-Scaling =** It can automatically add or remove app instances based on usage **(more traffic = more pods)**.
- **High Availability =** My app keeps running even if one machine goes down - because it runs on multiple nodes.
- **Rolling Updates =** My app can update without downtime. Kubernetes replaces old pods with new ones, step by step.
- **Resource Optimization =** It uses the cluster resources (CPU, memory) efficiently and only runs what’s needed.
- **Easy Configuration =** I describe what I want in a YAML file, and Kubernetes makes it happen - and keeps it that way.

## What Is a Cluster?
- A Cluster is the basic setup in Kubernetes.
- It's made of multiple computers or virtual machines that work together to run my app.
- I can think of a Cluster like a "mini data center" just for my app.

## What Is Inside a Cluster?
- A Kubernetes Cluster has 2 main parts:
- **Control Plane =** The manager. It makes all the decisions. It watches over the system, starts or stops apps, and keeps everything running the way I asked.
- **Worker Nodes =** The workers. These are the computers or virtual machines that actually run my app.

## What Is a Pod?
- A pod is the smallest unit the Kubernetes runs.
- Usually, a Pod runs a single container (based on an image), like my Flask app or my Redis instance.
- I don't run containers directly - I run Pods.

## For Example
- I am about to tell Kubernetes to run my finbrain-backend container in the cloud - and make sure it stays up, and has 2 copies running.
- Kubernetes will:
- 1. Use the **Control Plane** to understand my request.
- 2. Find free **Worker Nodes**.
- 3. Create **Pods** on those **Nodes**.
- 4. Each **Pod** will run **Container** based on my **Docker image**, which is pulled from **Amazon ECR**.

# 1. Installed Kubernetes CLI Tools
- **Amazon EKS (Elastic Kubernetes Service) =** is a managed Kubernetes service. EKS lets me run my app in the cloud using Kubernetes - without having to install or manage Kubernetes. It gives me a **ready-made Kubernetes setup** - like a "cloud computer" that knows how to run containers automatically, reliably, and at scale. **I push my Docker image to ECR and then I use kubectl to tell EKS to run this image.**
- I Installed **kubectl** – Kubernetes command-line tool, **used to interact with clusters** with this command line: **kubectl version --client**
- I Installed **eksctl** – Simplified CLI tool to **create and manage AWS EKS clusters** with this command line: eksctl version.

# 2. Created EKS Cluster for FinBrain
- Used eksctl to create a managed Kubernetes cluster in AWS with the command line: **eksctl create cluster \ --name finbrain-cluster \ --region eu-central-1 \ --nodegroup-name finbrain-nodes \ --node-type t3.medium \ --nodes 2 \ --nodes-min 1 \ --nodes-max 3 \ --managed**

## Cluster Configuration
- eksctl create cluster = Start the process of creating a new **EKS Kubernetes cluster**.
- name = name of my cluster, this is what I will use to refer to my cluster later
- region = Choose where to create the cluster, this is the AWS region where my cluster lives.
- nodegroup-name = Name the **group of machines (nodes)** that will run my app inside the cluster.
- node-type t3.micro = Pick the machine size for my nodes, **t3.medium** is a medium machine (has more RAM then t3.small or t3.micro).
- nodes 2 = Start with 2 machines in my cluster
- nodes-min 1 = Minimum number of machines allowed = 1 (If **traffic is low**, Kubernetes can scale down).
- nodes-max 3 = Maximum number of machines allowed = 3 (If **traffic is high**, Kubernetes can scale up).
- managed = Let AWS manage the machines for me, I don’t need to worry about updates, security, or configuration. AWS takes care of it.

# 3. Checked Cluster Status
- After creating the EKS cluster, I used the following command to verify that the cluster is active and the nodes are ready: **kubectl get nodes**
- It lists all the **worker nodes** currently running in the **EKS cluster**.
- Each node is an **EC2 instance** that can run my **application's containers (Pods)**.
- If the **STATUS** is **Ready**, it means the node is **healthy** and ready to accept workloads.
- **EC2 (Elastic Compute Cloud) =** Amazon's cloud service for running **virtual machines ("instances")**. Each **instance** is like a remote computer — with its own CPU, RAM — running in the cloud. In my Kubernetes (EKS) cluster, each **Node** is actually an EC2 instance. **"Elastic"** means I can **scale** the machines up/down, stop/start them anytime.

# 4. How Auto-Scaling Works?
- **CPU usage (%) -** How much CPU each Pod actually uses compared to what was allocated.
- **Memory usage (RAM) -** How much memory is used compared to what was allocated.
- **Pending Pods -** Pods that can't start because all nodes are full (no enougth CPU or memory), the **Cluster Autoscaler** adds a **new node** to give them space (**scale up**).
- **Idle Nodes -** Machines that have little or no work to do (**few or no Pods running**), the **Cluster Autoscaler** removes **unused nodes** to save resources (**scale down**).

# 5. Summary – What I learned in AWS Stage 2
- I learned how to set up a Kubernetes environment on AWS using EKS.
- I now have a working cluster ready to deploy my FinBrain backend from ECR.
- **END OF STAGE 2!**