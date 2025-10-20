# FinBrain (Nadav Eshed) - AWS Studies Stage 5
# (WATCH MORE on aws-infra branch on github)
# Still Working On That

# 0. To Know Before

## What Is Helm?
- Helm is a tool that helps me install apps into Kubernetes easily. I can think of it like:
- An "App Store" for Kubernetes.
- Each app has a package (called a chart = ready-made package or blueprint that tells Kubernetes how to install and configure an app).
- Helm knows how to download and install that chart with one simple command.
- Without Helm, installing things on Kubernetes requires many complicated YAML files. With Helm, it's one line.
- To install Helm I entered the command: **curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash**

## What Is an Ingress Contoller?
- When my app is running inside Kubernetes, it's like having it locked inside a private city. People from the internet (like browsers) can't reach it directly.
- I need a gate at the city entrance — and someone who manages that gate. That manager is called an: Ingress Controller.
- It does two main things: First, listens to all incoming traffic (HTTP/HTTPS) and second decides where to send each request (to the correct app inside Kubernetes).
- For example: A browser sends a request to https://api.finbrain.app/api/users/login. The Ingress Controller sees this and checks the rules I wrote and sends the request to the right service (like my Flask backend)
- I control those rules with a file called ingress.yaml.

# 1. Installing the Ingress-NGINX Controller

## Command 1
- **helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx**
- This tells Helm where to find the chart (package) for installing the NGINX Ingress Controller.
- **ingress-nginx =** the name I give to this repo (so I can refer to it later).

## Command 2
- **helm repo update**
- Helm checks all the repos I added, and makes sure it has the latest versions of the charts.

## Command 3
- **helm install ingress-nginx ingress-nginx/ingress-nginx \ --namespace ingress-nginx \ --create-namespace**
- Install the Ingress Controller into Kubernetes
- **helm install =** tells Helm to install something.
- **ingress-nginx =** the name I want to give to this installation.
- **ingress-nginx/ingress-nginx =** the chart path: First is the repo name and second the chart name inside that repo.
- **--namespace ingress-nginx =** tells Kubernetes to put all the files in a separate space called ingress-nginx.
- **--create-namespace =** if the namespace doesn’t exist, create it automatically.

## Command 4
- **kubectl get pods -n ingress-nginx**
- Show all running containers (pods) in the ingress-nginx namespace.
- **kubectl =** tool to talk to Kubernetes.
- **get pods =** ask for a list of all pods (containers).
- **-n ingress-nginx =** look only inside the ingress-nginx namespace.

## Command 5
- **kubectl get svc -n ingress-nginx**
- Show all services (load balancers, etc.) in ingress-nginx namespace.
- svc = service.
- This shows me the IP addresses or load balancers that were created.
- I’ll see a LoadBalancer with an EXTERNAL-IP — this is the gateway to my cluster.

# 2.