<p align="center">
  <img src="https://github.com/nadav0411/FinBrain/blob/main/assets/FinBrain%20Logo.png?raw=true" alt="FinBrain Logo" width="600"/>
</p>

<h1 align="center">FinBrain – Smart Expense Tracker</h1>

---

**FinBrain is an Independent Full-Stack Client-Server expense tracking application (self-initiated)** that helps you manage your budget, visualize spending, and leverage **AI-powered categorization** to automatically classify expenses.  
Built with **React (Frontend)** and **Flask (Backend)**, with **MongoDB** and **Redis** for data management and performance.

---

## Table of Contents

- [Motivation & Inspiration](#motivation--inspiration)
- [Architecture Diagram](#architecture-diagram)
- [Tech Stack](#tech-stack)
- [Beyond the Code – Thought Process](#beyond-the-code--thought-process)
- [Project Structure](#project-structure)
- [Quick Start Guide](#quick-start-guide)
- [Running Tests (300+ Tests)](#running-tests-300-tests)
- [Screenshots](#screenshots)
- [In Progress / Roadmap](#in-progress--roadmap)
- [License](#license)
- [Author](#author)

---

## Motivation & Inspiration

As someone passionate about both **finance** and **backend/cloud development**, I was curious to understand what truly powers large-scale applications in the real world.  
What makes cloud systems so scalable?  
What are the **fundamental building blocks** that allow platforms to handle **thousands or even millions of users** without collapsing under pressure?

Through FinBrain, I wanted to explore these concepts more deeply, it was an opportunity to move beyond tutorials and build something that not only works, but is also **designed to scale, adapt, and feel production-ready**.

This project became an opportunity to experiment with **real engineering trade-offs**, explore **cloud architecture best practices**, and build a system that doesn’t just work — but is **designed to scale and evolve**.

I treated FinBrain as a real-world product, not just an app to explore concepts — and that mindset guided every decision I made.

---

## Architecture Diagram

![FinBrain System Architecture](https://github.com/nadav0411/FinBrain/blob/main/assets/FinBrain%20System%20Architecture.png?raw=true)

---

## Tech Stack

**Frontend**
- **React** – responsive and fast SPA frontend.  
- **CSS** – interactive, user-friendly UI for expense visualization.  

**Backend**
- **Flask** – lightweight backend framework serving structured RESTful APIs to the frontend.
- **Gunicorn** – production-grade WSGI server for handling concurrent requests.
- **Modular architecture** – clear separation of logic, data access, and testing layers for flexibility and maintainability.

**Database & Caching**
- **MongoDB** – primary database for storing users and expenses.  
- **Redis** – in-memory cache handling sessions, TTL heartbeats, and frequently accessed expense and currency data.

**Authentication & Security**
- **Argon2 hashing** – secure password storage.  
- **Redis TTL sessions** – scalable session management without thread locks.  

**Machine Learning**
- **Scikit-learn (TF-IDF + Logistic Regression)** – AI-powered expense classification.  
- **Feedback loop** – continuously improves model accuracy from user input.  

**Integrations**
- **Frankfurter API** – real-time USD ⇄ ILS currency conversion.  

**DevOps / Reliability**
- **Docker + Docker Compose** – containerized backend, DB, and cache with volumes + health checks.  
- **GitHub Actions (CI/CD)** – automated testing and deployment.  
- **pytest + mocking/patching** – full API coverage, simulated DB interactions.  
- **Structured logging + exception handling** – better debugging and observability. 
- **Multi-environment configuration** – separate `.env` files for development, testing, and production ensure clean isolation and reproducible behavior across environments.
- **Render (Backend)** – hosts the Flask API and Redis cache using Docker containers for reliable performance.  
- **Vercel (Frontend)** – serves the React client with optimized builds and automatic redeploys from GitHub.  
- **Uptime Monitoring** – automated periodic pings verify backend availability and alert on potential downtime.
- **Helm** – simplified deployment and upgrade of Prometheus, Grafana, and Ingress controllers.
- **Grafana + Prometheus** – real-time monitoring stack visualizing CPU, memory, restarts, and uptime trends.
- **Custom Grafana Dashboards** – tailored panels for FinBrain (CPU rate, restart rate, uptime, request load).
- **Load Simulation Script** – Python-based concurrent request test (ThreadPoolExecutor) to verify performance under heavy load.

**Cloud & Infrastructure (AWS)**
- **Amazon ECR (Elastic Container Registry) –** private registry storing Docker images.
- **Amazon EKS (Elastic Kubernetes Service) –** managed Kubernetes cluster hosting FinBrain backend + Redis.
- **Kubernetes Deployments & Services –** YAML-based definitions for replicas, load balancing, and self-healing.
- **Ingress + NGINX Controller –** routes incoming traffic to the correct service inside the cluster.
- **Cloudflare DNS –** custom domain (api.finbrain.uk) connecting to the AWS LoadBalancer.
- **TLS + cert-manager (Let’s Encrypt)** – automatic HTTPS certificates for secure communication.
- **AWS Secrets Manager + CSI Driver + IRSA** – encrypted, role-based secret injection directly into pods.
- **Cluster Autoscaler –** scales EC2 nodes based on CPU/memory usage.
- **EC2 Worker Nodes –** t3.medium instances running pods efficiently.
- **AWS CLI + eksctl + kubectl –** full CLI-based cluster and resource management.
- **AWS IAM (Roles & Policies) –** granular access for human and service accounts.
- **Monitoring Namespace –** dedicated Kubernetes namespace isolating monitoring tools for reliability and performance.

---

## Beyond the Code – Thought Process

With FinBrain, I challenged myself to think beyond "getting it to work" — and instead focused on building a backend that follows real engineering practices:  
- Modular, testable, and clean architecture  
- Stateless sessions with Redis TTL  
- Data caching for performance  
- Multi-environment configuration  
- Secure authentication by design  
- Observability through logging  
- Docker-based orchestration with health checks  
- AI lifecycle that learns from users

My goal was to simulate a **miniature production system** — not just to demonstrate technical implementation, but to explore how engineers think, how cloud systems scale, and how architecture supports **efficient, concurrent access by a large number of users**.  
I wanted to build something that could realistically serve real users — reliably, securely, and at scale.

---

## Project Structure

FinBrain is organized into a **clean client-server architecture**, separating the React frontend and Flask backend, while also including assets, ML models, tests, and infrastructure files.


```plaintext

FinBrain/
├── assets/                          # Screenshots & visual assets for README
│   ├── Add Expense Modal.png
│   ├── Categorized Expenses Table.png
│   ├── Change Category.png
│   ├── Dashboard Overview (Category Breakdown).png
│   ├── Dashboard Overview (Monthly Comparison).png
│   ├── FinBrain Logo.png
│   ├── Inactive detection.png
│   ├── Month Picker Modal.png
│   ├── User Login.png
│   └── User Registration.png
│
├── client/                          # React frontend application
│   ├── src/
│   │   ├── components/              # React Components
│   │   │   ├── AddExpenseModal.jsx/.css
│   │   │   ├── AllExpenses.jsx/.css
│   │   │   ├── AuthSwitcher.jsx
│   │   │   ├── CalendarModal.jsx/.css
│   │   │   ├── DashBoard.jsx/.css
│   │   │   ├── LoginModal.jsx/.css
│   │   │   ├── MainScreen.jsx/.css
│   │   │   ├── MonthPickerModal.jsx/.css
│   │   │   ├── Settings.jsx/.css
│   │   │   └── SignupModal.jsx/.css
│   │   ├── App.jsx/.css
│   │   ├── main.jsx
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
│
├── server/                          # Flask backend including API, ML, DB, cache & logic
│   ├── src/
│   │   ├── app.py                   # Main Flask application
│   │   ├── db/                      # Database layer
│   │   │   ├── db.py                # MongoDB connection
│   │   │   └── cache.py             # Redis caching
│   │   ├── models/                  # ML Models
│   │   │   ├── predictmodelloader.py
│   │   │   └── finbrain_model/
│   │   │       ├── model.pkl
│   │   │       ├── vectorizer.pkl
│   │   │       └── training_data.csv
│   │   ├── services/                # Business Logic
│   │   │   ├── logicconnection.py   # Auth & sessions
│   │   │   ├── logicexpenses.py     # Expense management
│   │   │   └── trainer.py           # ML model training
│   │   └── utils/
│   │       └── password_hashing.py  # Argon2 security
│   ├── tests/                       # Test Suite (300+ tests)
│   │   ├── test connections/        # Auth tests
│   │   ├── test expenses/           # Expense tests
│   │   └── test others/             # General tests
│   ├── docker-compose.yml           # Multi-container setup
│   ├── Dockerfile                   # Backend container**
│   ├── Makefile                     # Development commands
│   └── requirements.txt             # Python dependencies
│
├── aws                              # AWS CLI folder – contains binaries and dependencies for running AWS commands
├── aws-provider.yaml                # Installs AWS Secrets Manager provider for Kubernetes (CSI Driver)
├── deployment.yaml                  # Kubernetes Deployment – runs Flask backend pods from ECR image
├── service.yaml                     # Kubernetes Service – exposes Flask backend via LoadBalancer (public IP)
├── finbrain-secretprovider.yaml     # SecretProviderClass – mounts secrets from AWS Secrets Manager into pods
├── redis-deployment.yaml            # Kubernetes Deployment – runs Redis pod inside the cluster
├── redis-service.yaml               # Internal Service – allows backend pods to communicate with Redis
├── cluster-issuer.yaml              # Cert-Manager – configures Let's Encrypt for automatic HTTPS crtificates
├── ingress.yaml                     # Ingress resource – routes external traffic to backend service through NGINX
│
├── simulate_login_load.py           # Load-testing script - sends parallel login requests to test backend performance
│
├── README.md                        # Project documentation
└── LICENSE                          # MIT License
```

---

## Quick Start Guide

- **1. Download & Start Backend:**
    git clone https://github.com/nadav0411/FinBrain.git **->** cd FinBrain/server **->** docker compose up --build

- **2. Start Frontend (new terminal):**
    cd client **->** npm install **->** npm run dev

- **3. Open Browser:**
    Go to: http://localhost:5173

- **4. Done!**
    Click "Demo" to try without signing up **->** Or sign up and then login for real account

- **5. To Stop:**
    cd server **->** docker compose down **->** THATS IT!

---

## Running Tests (300+ Tests)

- cd server **->** python -m pytest
- **Note:** Make sure Redis is running locally since tests use the original Redis instance.

---

## Screenshots

![Dashboard Overview (Category Breakdown) Screenshot](https://github.com/nadav0411/FinBrain/blob/main/assets/Dashboard%20Overview%20(Category%20Breakdown).png?raw=true)
![Dashboard Overview (Monthly Comparison) Screenshot](https://github.com/nadav0411/FinBrain/blob/main/assets/Dashboard%20Overview%20(Monthly%20Comparison).png?raw=true)
![Categorized Expenses Table Screenshot](https://github.com/nadav0411/FinBrain/blob/main/assets/Categorized%20Expenses%20Table.png?raw=true)
![Add Expense Modal Screenshot](https://github.com/nadav0411/FinBrain/blob/main/assets/Add%20Expense%20Modal.png?raw=true)
![Change Category Screenshot](https://github.com/nadav0411/FinBrain/blob/main/assets/Change%20Category.png?raw=true)
![Inactive detection Screenshot](https://github.com/nadav0411/FinBrain/blob/main/assets/Inactive%20detection.png?raw=true)
![Month Picker Modal Screenshot](https://github.com/nadav0411/FinBrain/blob/main/assets/Month%20Picker%20Modal.png?raw=true)
![User Login Screenshot](https://github.com/nadav0411/FinBrain/blob/main/assets/User%20Login.png?raw=true)
![User Registration Screenshot](https://github.com/nadav0411/FinBrain/blob/main/assets/User%20Registration.png?raw=true)

---

## In Progress / Roadmap

These are the features and improvements currently being developed:

- **Advanced Cloud Infrastructure Enhancements** 
  Continuing to expand FinBrain’s AWS-based architecture — building on the existing ECR + EKS deployment with deeper Kubernetes automation, cost optimization, improved monitoring, and advanced IAM & security configurations.

- **Performance & Efficiency Improvements**
  Ongoing work to optimize the application for faster response times, reduced resource usage, and smoother overall performance as the project scales.

- **Forgot Password + Strong Password Enforcement**  
  Adding password recovery via email and enforcing strong password rules for better security.

- **Settings Page**  
  User preferences, change password, email or name, default currency selection, notification settings, and more customization options.

---

## License

This project is licensed under the MIT License – see the [LICENSE](./LICENSE) file for details.

---

## Author

**Nadav Eshed**  
I'm a Computer Science student at the Hebrew University, passionate about both technology and people, I'm driven by challenges, continuous learning, and the joy of turning complex problems into smart, useful solutions - always with a growth mindset, a collaborative spirit, and a smile!

I believe that in today's world, technology isn’t just a tool – it’s a powerful force that can improve lives and solve real-world problems across every field: health, finance, education, and beyond.
[LinkedIn](https://www.linkedin.com/in/nadav-eshed-b32792363) • [GitHub](https://github.com/nadav0411) • nadav0411@gmail.com