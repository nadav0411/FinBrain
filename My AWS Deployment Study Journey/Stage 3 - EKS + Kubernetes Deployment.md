# FinBrain (Nadav Eshed) - AWS Studies Stage 3 - EKS + Kubernetes Deployment
# (WATCH MORE on aws-infra branch on github)

# 0. Some Definitions

## What is a YAML file?
- It's a simple, human-readable file format used to describe data and configuration.
- In Kubernetes, I use YAML files to tell the cluster what we want.
- It's like a recipe that Kubernetes reads and follows.

## What is a Deployment YAML?
- Tells Kubernetes "Run this app for me - keep it alive - and make sure I always have X copies.
- Key things it defines:
- **replicas =** How many copies (pods) to run.
- **image =** Which Docker image to use.
- **containerPort =** Which port your app listens on.
- **labels =** Tags to identify the app.
- **machLabels =** Conntects to the Service.

## What us a Service YAML?
- Tell Kubernetes "Give me a stable way to acess my app - even if the pods change".
- It acts like a router or load balnacer in front of my app.
- Key things it defines:
- **type =** How to expose it (for example public IP)
- **port =** The port users connect to
- **target port =** The port my app listens to inside the pod.
- **selector =** Which pods to forward the traffic to.

## Visual Analogy
- **Deployment =** The kitchen. You tell it: “Always keep 2 pizzas ready.”
- **Pods =** The pizzas.
- **Service =** The waiter. Customers don’t talk to the kitchen directly — they talk to the waiter, who brings the pizza.

# 1. YAML files
- I wrote 4 YAML files - deployment.yaml (Describes how many Pods I want and which Docker image to use), service.yaml (Creates a stable endpoint (IP) to access my app from the internet), redis-deployment.yaml (Runs one Redis container in a separate pod inside the cluster) and redis-service.yaml (Creates a private internal service so that other pods can talk to Redis).
- After that I used 2 commands:
- **kubectl apply -f redis-deployment.yaml**. Tells Kubernetes: "Run the Redis pod using the official Redis Docker image".
- **kubectl apply -f redis-service.yaml**. Tells Kubernetes: "Create an internal service called redis-service that other pods (like Flask) can connect to".
- **kubectl apply -f deployment.yaml**. Tells Kubernetes: "Create a Deployment using this file — launch the pods, and manage them for me."
- **kubectl apply -f service.yaml**. Tells Kubernetes: "Create a Service to expose my app — so users can access it using a public IP."

# 2. Checked Resources and a Problem I Faced
- I used to commands lines to check if everything work.
- **kubectl get pods**. Lists all the pods currently running (or trying to run) in my Kubernetes cluster.
- **kubectl get svc**. Lists all the Services running in my cluster — and shows how my app is exposed.
- **kubectl logs {name of the pod}**. Shows the logs (output) from inside the container.

## What Error Did I Get?
- When I ran my Deployment, the pod stayed in **Pending state**.
- It's happen because my cluter was using **t3.micro EC2 instances**. These nodes can only run 4 to 5 pods each, and Kubernetes already uses some of them for system components so there was no room left for my Flask pod.
- I deleted the old cluster and created a new one with **t3.medium nodes (larger EC2s)**. These have more RAM and allow 17 to 20 pods per node, so now there’s space.

# 3. Commands to know
- **kubectl rollout restart deployment {name of deployment}**. If I update my code - This command tells Kubernetes to restart all Pods under the deployment. It terminates old Pods and launches new ones — which automatically pull the latest image from ECR. 
- **kubectl get deployments**. Lists all deployments in the current namespace, showing how many Pods are up-to-date and running.
- I can check in AWS web about more details to search there EC2, EKS, ECR.

# 4. Accessing the Application via the Service Link
- After all Pods are running successfully, I can access my Flask application using the public link created by the Kubernetes Service.
- To find it, I run: **kubectl get services**.
- In the output, I look for the EXTERNAL-IP field of the Service (the one with TYPE = LoadBalancer).
- If the link loads successfully - my server is live and running on AWS (EKS + ECR + LoadBalancer).

# 5. Summary – What I learned in AWS Stage 3
- I learned how to deploy and manage my backend on AWS EKS using Kubernetes.
- I created and applied YAML files for Deployment, Service, and Redis.
- I used commands like kubectl get pods, kubectl get services, and kubectl rollout restart to manage and verify my cluster.
- Now my backend is live on AWS — fully containerized, scalable, and connected through a LoadBalancer.
- **END OF STAGE 3!**
