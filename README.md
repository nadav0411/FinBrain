<p align="center">
  <img src="https://github.com/nadav0411/FinBrain/blob/main/assets/FinBrain%20Logo.png?raw=true" alt="FinBrain Logo" width="600"/>
</p>

<h1 align="center">FinBrain – Smart Expense Tracker</h1>

---

**FinBrain is an Independent Full-Stack Client-Server expense tracking application (self-initiated)** that helps you manage your budget, visualize spending, and leverage **AI-powered categorization** to automatically classify expenses.  
Built with **React (Frontend)** and **Flask (Backend)**, with **MongoDB** and **Redis** for data management and performance.

---

## Motivation & Inspiration

As someone passionate about both **finance** and **backend/cloud development**, I was curious to understand what truly powers large-scale applications in the real world.  
What makes cloud systems so scalable?  
What are the **fundamental building blocks** that allow platforms to handle **thousands or even millions of users** without collapsing under pressure?

Through FinBrain, I wanted to explore these concepts more deeply, it was an opportunity to move beyond tutorials and build something that not only works, but is also **designed to scale, adapt, and feel production-ready**.

This project became an opportunity to experiment with **real engineering trade-offs**, explore **cloud architecture best practices**, and build a system that doesn’t just *work* — but is **designed to scale and evolve**.

I treated FinBrain as a real-world product, not just a student app — and that mindset guided every decision I made.

---

## Tech Stack

**Frontend**
- **React** – responsive and fast SPA frontend.  
- **CSS** – interactive, user-friendly UI for expense visualization.  

**Backend**
- **Flask** – lightweight backend framework for REST APIs.  
- **Gunicorn** – production-grade WSGI server for handling concurrent requests.  

**Database & Caching**
- **MongoDB** – primary database for storing users and expenses.  
- **Redis** – in-memory cache for sessions, heartbeats (TTL), currency and expenses data.  

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

---

## Beyond the Code – Thought Process