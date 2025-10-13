# FinBrain (Nadav Eshed) - AWS Studies Stage 2
# (aws-infra branch on github)


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
- **Amazon EKS (Elastic Kubernetes Service) =** is a managed Kubernetes service. EKS lets me run my app in the cloud using Kubernetes - without having to install or manage Kubernetes. It gives me a **ready-made Kubernets setup** - like a "cloud computer" that know how to run containers automatically, reliably, and at scale. **I push my Docker image to ECR and then I use kubectl to tell EKS to run this image.**
- I Installed **kubectl** – Kubernetes command-line tool, **used to interact with clusters** with this command line: **kubectl version --client**
- I Installed **eksctl** – Simplified CLI tool to **create and manage AWS EKS clusters** with this command line: eksctl version.

# 2. Created EKS Cluster for FinBrain