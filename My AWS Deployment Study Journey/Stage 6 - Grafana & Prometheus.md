# FinBrain (Nadav Eshed) - AWS Studies Stage 6 - Grafana & Prometheus
# (WATCH MORE on aws-infra branch on github)

# 0. Why Monitoring Matters

## In a real application, it's important to know:
- How much CPU and Memory my app uses?
- How many users are connected?
- Are there errors in my app?
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
- **I opened a dashboard and selected:**
- namespace = default (where my Flask and Redis pods run).
- I saw live charts showing: CPU and Memory for my backend, Number of Pods, Grafana Metrics, Node usage.

# 5. I Built My Own Basic Dashboard
- I clicked the '+' button in Grafana and selected "New Dashboard".
- Then I clicked "Add Visualization" to start creating my own dashboard with a new panel.
- I created a dashboard with 3 basics panels to monitor my backend container.

## Panel 1: FinBrain Backend - CPU RATE
- I used the query: **rate(container_cpu_usage_seconds_total{namespace="default", container="finbrain-backend"}[5m])**.
- First, **CPU (Central Processing Unit)** is the "brain" of the server. It performs all calculations and runs the code of my app. When CPU usage is high, it means my app is busy or working hard.
- **The rate(...)** function calculates how fast something is changing over time.
- **container_cpu_usage_seconds_total** counts how many seconds the CPU was used by my container.
- So overall, this panel shows: how much CPU the Finbrain backend is using every second, based on the last 5 minutes.
- It helps me know if the app is under heavy load or if something is wrong (like an infinite loop or a spike in usage).

## Panel 2: Finbrain Backend - Container Restarts Rate
- I used the query: **rate(kube_pod_container_status_restarts_total{container="finbrain-backend"}[5m])**.
- This query tells me if my container is crashing or restarting often.
- **kube_pod_container_status_restarts_total** is a counter — it goes up every time the container restarts.
- **rate(...)** here checks how many times per second (on average) the container restarted over the last 5 minutes.
- So this panel shows: "Is my Finbrain backend crashing or restarting frequently?"
- If I see this number above 0, it means something is wrong — maybe the app crashed, or there was a bug or misconfiguration.

## Panel 3: Finbrain Backend - Uptime (Pod Running Duration)
- In this panel, I used a Math Expression Panel with 3 parts:
- A = time()
- B = container_start_time_seconds{container="finbrain-backend"}
- C = Expression: $A - $B
- Uptime = current time - container start time
- The container start time stays the same (it’s fixed — the moment the container was started).
- The current time keeps increasing - every second that passes, time() goes up and the result is a straight diagonal line going up in the graph.
- If the line suddenly drops back to zero (or a low number), it means: The container restarted or redeployed - it got a new start time.

# 6. Testing Dashboard Graph Reactions to Load
- To test if my dashboard reacts when there is real traffic on the server, I created a short Python script that sends hundreds of login requests to the app in parallel.
- While the requests were running, I watched the dashboard and saw that:
- The CPU graph increased sharply.
- The restart rate and other metrics stayed stable.
- It confirmed that the monitoring works correctly.
- This helped me simulate real load, like many users using the app at the same time, and made sure my panels respond in real-time.
- I attached screenshots below to show what the graphs looked like during the test.

## Screenshots
![Before Test](https://github.com/nadav0411/FinBrain/blob/main/assets/Grafana%20-%20My%20Dashboard%20(Start).png?raw=true)
![After Test](https://github.com/nadav0411/FinBrain/blob/main/assets/Grafana%20-%20My%20Dashboard%20(End).png?raw=true)

# 7. Summary – What I learned in AWS Stage 6
- In this stage, I added monitoring to my Kubernetes (EKS) cluster using Prometheus and Grafana.
- I installed everything using Helm, in a separate namespace called monitoring.
- I accessed Grafana locally using port-forward and logged in with the admin password from Kubernetes.
- I explored built-in dashboards to monitor CPU, memory, pod usage, and node activity.
- Then, I created my own custom dashboard with 3 panels:
- CPU Rate – shows how hard my app is working.
- Container Restart Rate – tells me if my app is crashing.
- Uptime – shows how long the backend has been running.
- I wrote a Python script to simulate heavy traffic by sending hundreds of login requests.
- During the test, I saw the CPU panel spike, confirming that my monitoring works in real time.
- Now I can detect issues, crashes, or high usage — before they impact users.
- **END OF STAGE 6!**