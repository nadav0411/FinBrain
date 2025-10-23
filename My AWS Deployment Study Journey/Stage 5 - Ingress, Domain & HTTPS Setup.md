# FinBrain (Nadav Eshed) - AWS Studies Stage 5 - Ingress, Domain & HTTPS Setup
# (WATCH MORE on aws-infra branch on github)

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

## What does Cloudflare do?
- Cloudflare is like a smart, secure front gate for my website.
- Let's assume that my website is a house (my server). I don’t want every stranger to knock on my door directly — it’s risky, slow, and I want some control.
- Cloudflare stands between visitors and my real house.
- It speeds things up (by caching copies of my site around the world).
- Adds security (blocks attackers before they reach my house).
- Helps manage traffic (e.g., choose which server to talk to, or hide my real IP)
- And most importantly in my case — it helps connect my domain (like api.finbrain.uk) to the correct backend (my Ingress → Flask backend on EKS).

## Why to use Domain and what is DNS?
- When I build an app and deploy it on the internet (like on AWS), the server usually has a long, hard-to-remember address - something like:
a7.....k8.eu-central-1.elb.amazonaws.com, That’s not friendly or professional.
- Instead, we want people to visit our app using a clean and short name like: https://api.finbrain.uk
- This short, human-friendly name is called a domain.

### But how does the internet know where to find this domain?
- That's where DNS comes in.
- **DNS = Domain Name System**
- It works like the internet’s phonebook. I type in: api.finbrain.uk and DNS translates that name into the real address (like an AWS LoadBalancer IP). And then my browser connects to it.
- Without DNS, I would need to memorize IP addresses or AWS URLs — which is painful and not scalable.
- By setting up a domain and configuring DNS (like in Cloudflare), we can:
- Control where the domain points (to my app).
- Protect it (via SSL).
- Make it look clean and trustworthy.

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

# 2. Creating the Ingress Rule 
- I created an ingress.yaml file that tekk the Kubernetes: "if someone visits /api, send them to my Flask backend".
- After writing this file I applied it with the command: **kubectl apply -f ingress.yaml**.

# 3. Buying a Domain + DNS Setup (Cloudflare)
- I bought the domain: finbrain.uk and used Cloudflare to manage it.
- I added a **DNS record** with those setting:
- **Type (The kind of DNS record) =** CNAME
- **Name (This is the subdomain part, what comes before my domain) =** api
- **Target (Where do I want this name to point) =** My LoadBalancer address.
- Then I tested with the command: **nslookup api.finbrain.uk** and saw that it correctly pointed to my Kubernetes ingress.

# 4. Small Break for More Definitions 

## What is TLS?
- TLS (Transport Layer Security) is like a lock on my website’s connection.
- It protects the data that travels between my site and the user — so no one can spy, steal passwords, or fake being me.
- I (the browser) send a letter -> TLS puts it in a sealed envelope -> Only the server can open it.

## What is HTTPS (vs HTTP)?
- **HTTP = no lock = insecure**, anyone can see the data going back and forth. 
- **HTTPS = secure version of HTTP**, uses TLS to protect the connection

## What is an HTTPS certificate?
- It’s like an ID card that proves my site is real and safe.
- Shows the browser: "Hey, I really am api.finbrain.uk — not a fake!"
- Without it, users see warnings like "My connection is not secure".

## What is Let’s Encrypt?
- Let’s Encrypt is a free service that gives HTTPS certificates.
- They’re trusted by all browsers — and don’t cost money.
- cert-manager (next point) can ask Let’s Encrypt to issue me a certificate automatically.

## What is cert-manager?
- cert-manager is a Kubernetes tool that:
- Automatically requests an HTTPS certificate (e.g., from Let’s Encrypt).
- Verifies domain ownership (using Ingress).
- Saves the certificate as a Kubernetes Secret.
- Renews it before it expires — all automatically.
- I tell it: "Here’s my domain: api.finbrain.uk. Get me a certificate from Let’s Encrypt." and it does the rest.

# 5. Installing cert-manager for HTTPS
- I installed it with the command: **kubectl apply -f https://github.com/cert-manager/cert-manager/releases/latest/download/cert-manager.yaml**.
- I created a file called cluster-issuer.yaml. 
- A Cluster Issuer is a Kubernetes object that tells cert-manager how to get HTTPS certificates. Once it’s created, cert-manager uses it to request certificates for my domains (like api.finbrain.uk).
- Applied the file with the command: **kubectl apply -f cluster-issuer.yaml**.

# 6. Verifying the HTTPS Certificate
- After everything was connected, cert-manager automatically requested a TLS certificate for: https://api.finbrain.uk
- I checked the certificate status with the command **kubectl describe certificate finbrain-tls**. It showed: Ready = True

# 7. Connecting Frontend to the API
- I updated my Vercel project’s environment variable: **VITE_API_URL=https://api.finbrain.uk/api**
- Now my React frontend communicates securely with the backend running inside AWS EKS.

# 8. Summary – What I learned in AWS Stage 5
- In this stage, I connected my backend running in Kubernetes (EKS) to the internet using a real domain and HTTPS encryption.
- I installed an NGINX Ingress Controller to route traffic into the cluster, and used Cloudflare DNS to point a custom domain (api.finbrain.uk) to my backend.
- Then, I installed cert-manager and used Let's Encrypt to automatically generate a valid HTTPS certificate, making my API secure.
- Finally, I updated the frontend (on Vercel) to call the API using the new secure domain.
- **END OF STAGE 5!**