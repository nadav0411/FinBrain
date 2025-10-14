# FinBrain (Nadav Eshed) - AWS Studies Stage 1 - AWS Foundations + Docker Registry (ECR)
# (WATCH MORE on aws-infra branch on github)


## 0. AWS Introduction
- **AWS (Amazon Web Services)** is a cloud platform that provides services like virtual servers, storage, databases, and more.  
- It allows developers to run applications without managing physical hardware.

## 1. Created an AWS account 
- Signed up and access to the free tier.

## 2. Created an IAM user
- **IAM user =** a user inside my AWS account, with its own permissions
- I created a **user** named 'finbrain-manager'.
- I gave permissions that allow using AWS via terminal, scripts, or code.
- I added it to a new **group** called 'FinBrainAdmins'.
- That group has the **AdministratorAccess** policy (full permissions).

## 3. Created access keys
- I generated an **Access Key ID** and **Secret Access Key**.
- These are used to connect my computer to AWS using the terminal (CLI)

## 4. Installed and configured AWS CLI
- I installed the **AWS CLI** tool on my computer
- Then I ran: **aws configure** 
- Then entered my Access Key ID, Secret Access Key, Default region and output format.
- I ran: **aws sts get-caller-identity** to check that the AWS CLI is connected to my IAM user.

## 5. Created an ECR repository
- **ECR (Elastic container Registry) =** AWS's private **Docker image storage service**. It works like private "Docker Hub" in the cloud (I can think of it as my place to store ready-made containers). Later, services like **Kubernetes** can **pull images** from this place and run them.
- I created a private repository named 'finbrain-backend' using the CLI: **aws ecr create-repository --repository-name finbrain-backend --region eu-central-1**
- This repository is where I will push my container image.

## 6. Logged in to ECR from Docker
- I authenticated my Docker client (Logged in and proved I have permission to push to my private AWS ECR registry).
- I used this CLI: **aws ecr get-login-password --region {region} | docker login --username AWS --password-stdin {ecr-domain}**
- **ecr-domain =** My AWS ECR address (like a destination)

## 7. Tagged my local Docker image:
- Before I can upload a Docker image to AWS ECR, I need to "tag" it.
- **Tagging** means giving the image a **label** that tells Docker which cloud repository to push to.
- I already had a built image of my Flask backed called 'finbrain-backend'.
- I used this command to tag it: **docker tag finbrain-backend {ecr-domain}/finbrain-backend:latest**
- **latest** is the version tag - means this is the newest version of the image.
- Docker needs to know where to send it - and tagging tells it exactly that.

## 8. Updating the Image (If I Did Code Changes)
- After modifying my backend code, I rebuilt the Docker image locally with the command line: **docker build -t finbrain-backend .**
- I need to make sure that my Docker Desktop app in my PC is open.

## 9. Pushed image to ECR
- I pushed my image to the cloud (ECR) using: **docker push {ecr-domain}/{repository-name}:{tag}**
- Each layer was uploaded, and I received a digest confirming the push was successful.
- **digest =** A unique, permanent fingerprint of the Docker image.

## 10. Verified the image in AWS Console
- I opened the **ECR service** in **AWS web console** and I saw there my repository and image there (after switching to the correct region).

## 11. Summary – What I learned in AWS Stage 1
- I learned the basics of AWS and how to work with the AWS CLI.
- I created a secure IAM user, configured access from my computer, and used ECR to store my Docker container in the cloud.
- Now my backend image is uploaded and ready to be used by AWS services.
- **END OF STAGE 1!**