# FinBrain (Nadav Eshed) - AWS Studies Stage 6 - Grafana & Prometheus
# (WATCH MORE on aws-infra branch on github)
# Still Working On That

# 0. Why Monitoring Matters

## In a real application, it's important to know:
- How much CPU and Memory my app uses?
- How many users are connected?
- Are there errors in your app?
- Is something slow or overloaded?

## Monitoring lets me:
- See live charts of what’s happening inside my app and cluster
- Detect bugs or crashes before users complain
- Scale or optimize based on real data

## Grafana:
- Grafana is a visualization tool.
- It lets me create real-time dashboards to monitor my system.
- **It connects to Prometheus and shows:**
- CPU and memory usage
- Number of running Pods
- Application performance 
- Errors or warning alerts
I can choose from built-in dashboards or create custom ones.

## Prometheus:
- Prometheus is a monitoring system and time-series database.
- It collects metrics (numbers that change over time) from my Kubernetes cluster.
- **These metrics include:**
- Resource usage (CPU, memory, network)
- Status of Pods, Nodes, Deployments
- Custom metrics from my own app
- Prometheus doesn’t display data — it just collects and stores it, Grafana is the tool that shows those numbers in graphs.

# 1. Installed Prometheus + Grafana using Helm
- I used the commands: **helm repo add prometheus-community https://prometheus-community.github.io/helm-charts** and **helm repo update**. This tells Helm where to find the charts for Prometheus & Grafana.
- I used the command **helm install finbrain-monitoring prometheus-community/kube-prometheus-stack \ --namespace monitoring \ --create-namespace**. 
- **finbrain-monitoring =** name of my installation
- **monitoring =** I created a separate namespace just for monitoring tools
- This command installed: Prometheus (collects metrics), Grafana (shows charts), AlertManager (sends alerts), Pre-built dashboards.
- I checked that everything is running with the command **kubectl get pods -n monitoring**.
- All the pods (grafana, prometheus, alertmanager, etc.) were in Running state.

# 2. Accessed Grafana via Port Forward
- Grafana runs inside Kubernetes, so I needed to open access from my laptop -> I used the command **kubectl --namespace monitoring port-forward svc/finbrain-monitoring-grafana 3000:80**.
- This opened Grafana at: **http://localhost:3000**.

# 3. Logged into Grafana
- I used the next command to get the password to log to Grafana: **kubectl --namespace monitoring get secrets finbrain-monitoring-grafana -o jsonpath="{.data.admin-password}" | base64 -d**.
- I used the user admin and copied the password and logged in.
- I changed Grafana default password.

# 4. Viewed Built-in Dashboards

## I opened a dashboard and selected:
- namespace = default (where my Flask and Redis pods run).
- I saw live charts showing: CPU and Memory for my backend, Number of Pods, Grafana Metrics, Node usage.

# **To be continued.....**