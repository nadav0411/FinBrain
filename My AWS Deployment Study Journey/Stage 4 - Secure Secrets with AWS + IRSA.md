# FinBrain (Nadav Eshed) - AWS Studies Stage 4 - Secure Secrets with AWS + IRSA
# (WATCH MORE on aws-infra branch on github)

# 0. To Know Before

## Why Secrets Management Matters
- In a real-world production system, secrets like MONGO_URI, REDIS_URL and more should never be stored directly inside Kubernetes YAML files or .env files.
- Instead, secrets must be: 
- **Encrypted =** The secret is safely scrambled using strong encryption so that no one can read it — even if they access the storage.
- **Centrally Managed =** All secrets are stored and controlled in one secure place (like AWS Secrets Manager), instead of being spread across many files or servers.
- **Easily Rotated =** Secrets can be changed (rotated) regularly or automatically — for example, changing database passwords every 30 days — without breaking the app.
- **Accessible Only to Authorized Pods =** Only the right applications (pods) that you trust and that have permission — can access specific secrets. Others cannot "see" or use secrets they weren’t approved for.

## What Is the Secrets Store CSI (Container Storage Interface) Driver?
- It’s a plugin that helps Kubernetes pods safely get secrets (like passwords, URIs) from external cloud tools like AWS Secrets Manager.
- Instead of writing secrets inside my YAML files, this plugin "mounts" them into my pods — like adding a secret file inside the container at runtime.
- It runs a helper component (called a DaemonSet) on each node in my cluster. That component is like a translator — it talks to AWS and brings back the secrets.

### Simple analogy
- CSI Driver as a waiter in a restaurant.
- My app (the customer) asks for a secret (e.g., MONGO_URI).
- The waiter (CSI Driver) goes to AWS (the kitchen) and brings the secret securely — only if the customer has permission.

## What Is a Volume in Kubernetes?
- In Kubernetes, a volume is like a folder that my container can access. It's a place to store files that my app can read or write.
- But unlike normal files inside the container, which disappear when the container restarts - volumes are persistent.

# 1. Stored secret in AWS Secrets Manager
- Using AWS Console, I stored a secret called finbrain-secrets that have the keys of MONGO_URI and REDIS_URL.

# 2. Install the Secrets Store CSI Driver
- **helm repo add aws-secrets-manager https://aws.github.io/secrets-store-csi-driver-provider-aws**. Adds the Helm chart repository for the AWS Secrets Provider (so Helm knows where to find it).
- **helm repo add secrets-store-csi-driver https://kubernetes-sigs.github.io/secrets-store-csi-driver/charts**. Adds the Helm chart repository for the base Secrets Store CSI Driver (this is the main plugin that runs in Kubernetes).
- **helm repo update**. Refreshes the list of available charts from both repos.
- **helm install csi-secrets-store secrets-store-csi-driver/secrets-store-csi-driver \ --namespace kube-system**. Installs the main Secrets Store CSI Driver into the kube-system namespace of my cluster. This driver runs a small component on every Kubernetes node and allows pods to access cloud secrets securely.

# 3. Install the AWS Provider using kubectl
- **curl -o aws-provider.yaml https://raw.githubusercontent.com/aws/secrets-store-csi-driver-provider-aws/main/deployment/aws-provider-installer.yaml**. Downloads a pre-made Kubernetes YAML file that contains the configuration to install the AWS-specific provider. This provider knows how to talk to AWS Secrets Manager.
- **kubectl apply -f aws-provider.yaml**. Applies the downloaded YAML file to the cluster. This creates the necessary DaemonSet, ServiceAccount, and permissions for the AWS provider to work.

# 4. Verify That Everything Is Running
- **kubectl get pods -n kube-system | grep secrets-store**. Lists all pods in the kube-system namespace and filters only those related to secrets-store.

# 5. Create IAM Policy to allow pods to access AWS Secrets 
- Before pods can read secrets from Secrets Manager, they must be authorized. I created an IAM Policy that grants permission to retrieve specific secrets. I used this command: **aws iam create-policy \ --policy-name FinbrainSecretsAccessPolicy \ --description "Allow FinBrain pods to read secrets from AWS Secrets Manager" \ --policy-document '{ "Version": "2012-10-17", "Statement": [ { "Effect": "Allow", "Action": [    "secretsmanager:GetSecretValue" ], "Resource": "arn:aws:secretsmanager:eu-central-1:832871077677:secret:finbrain-secrets-*" } ] }'**
- Grants access to call secretsmanager:GetSecretValue, Only for secrets that start with finbrain-secrets, Region = eu-central-1, Account = 832871077677 (I can get my account number with the command: **aws sts get-caller-identity**),

# 6. Enable IAM OIDC Provider on the cluster 
- I used this command: **eksctl utils associate-iam-oidc-provider \ --region eu-central-1 \ --cluster finbrain-cluster \ --approve**.
- This command connects my Kubernetes cluster to AWS IAM using a trusted identity system (OIDC). It tells AWS: "Pods from this cluster can prove who they are, so IAM Roles can trust them".
- Without this step, AWS won’t trust my pods — even if they have the right IAM Role. With this step, AWS says: "OK, I recognize these Kubernetes identities and will let them assume roles."
- **REMINDER OF IAM ROLE =** An IAM Role in AWS is like a temporary identity with specific permissions. Unlike an IAM user (which is a permanent identity with login credentials), a role is meant to be assumed by applications, services, or other AWS resources — for example, a Kubernetes pod inside EKS.

# 7. Create IAM Role & ServiceAccount via IRSA (IRSA = IAM Roles for Service Accounts)
- To let a pod in Kubernetes access an AWS service (like Secrets Manager), I need to connect two things: An IAM Role that says: "what permissions are allowed" and a Kubernetes ServiceAccount that used by the pod.
- Then I link them using something called IRSA: IAM Roles for Service Accounts.
- **IAM Roles for Service Account =** I created a Kubernetes ServiceAccount called finbrain-sa and then create an IAM Role in AWS that: trusts that ServiceAccount and has permission to access secrets. When a pod uses finbrain-sa, AWS gives it temporary credentials to access the secret.
- I used that command to do that: **eksctl create iamserviceaccount \ --name finbrain-sa \ --namespace default \ --cluster finbrain-cluster \
  --attach-policy-arn arn:aws:iam::832871077677:policy/FinbrainSecretsAccessPolicy \
  --approve \ --override-existing-serviceaccounts

# 8. Update the deployment.yaml of Flask backend
- To make the Flask pod use the new ServiceAccount (and gain permission to read secrets), I add under the "spec" line: **serviceAccountName: finbrain-sa**.

# 9. Created SecretProviderClass YAML (finbrain-secretprovider.yaml)
- I wrote a Kubernetes manifest that tells the CSI driver where to fetch secrets from.
- This tells the CSI (Container Storage Interface) driver to go to AWS Secrets Manager and mount the secret named **finbrain-secrets** into the pod.
- It only works because the pod is using the **finbrain-sa** service account, which has permission via **IAM Role (IRSA)**.
- To update it I ran the command: **kubectl apply -f finbrain-secretprovider.yaml**.

# 10. Updated deployment.yaml to Mount Secrets as Volume
- I added a volume that mounts the secrets from Secrets Manager using the CSI driver.
- The container now "sees" a file inside /mnt/secrets-store/mongo_uri and /mnt/secrets-store/redis_url at runtime.
- These files are automatically created by the CSI driver when the pod starts.
- They contain the real values from AWS Secrets Manager.
- - To update it I ran the command: **kubectl apply -f deployment.yaml**.

# 11. Updated cache.py and db.py to Support "File-based Secrets"
- I modified the code so that if REDIS_URL or MONGO_URI is actually a file path (not a URL), it reads the contents of the file.
- This ensures the code works both in local .env files and inside EKS where secrets are mounted as files.

# 12. Verified Application Works in Kubernetes
- I ran: **kubectl get pods** to check pod status and **kubectl logs <pod-name>** to debug any errors.
- The app successfully connected to: MongoDB Atlas using the mounted **mongo_uri** secret and Redis using the mounted **redis_url** secret.

# 13. Summary – What I learned in AWS Stage 4
- I learned how to securely manage secrets like MONGO_URI and REDIS_URL in a real-world Kubernetes environment.
- Instead of storing secrets in YAML files or .env, I used AWS Secrets Manager to store them safely in the cloud.
- I installed the Secrets Store CSI Driver, which lets Kubernetes pods get secrets securely from AWS at runtime.
- I learned about IAM Roles for Service Accounts (IRSA) — a powerful way to give specific pods permission to access only the secrets they need.
- I created a ServiceAccount in Kubernetes and linked it to an IAM Role with permission to read my secrets.
- I updated my Flask deployment.yaml to mount the secrets into the container as files using a volume.
- I changed my backend code (db.py, cache.py) to read the secrets from file paths inside the container.
- Finally, I tested that everything works: my app connected to MongoDB and Redis using the mounted secrets from AWS.
- **END OF STAGE 4!**