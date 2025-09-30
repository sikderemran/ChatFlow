# Real-Time Chat Application

A **real-time chat application** with a **microservices architecture** built using **FastAPI**, **WebSockets**, **MySQL**, and **Next.js**. The project is fully **containerized with Docker**, 
includes **automated tests using pytest** and supports **CI/CD via GitHub Actions**.  

---

## Features

- User registration and login with JWT authentication  
- Real-time messaging using WebSockets  
- Microservices architecture:
  - **Auth Service** – handles user registration/login  
  - **Chat Service** – handles message storage and retrieval  
  - **API Gateway** – centralizes API requests, manages authentication  
- Separate MySQL databases for services and testing  
- Automated tests using **pytest**  
- CI/CD pipeline automates testing, Docker image building, and deployment  

---

## Architecture

This project follows a **microservices architecture** to ensure scalability, maintainability, and independent deployment of components. The main services include:

- Auth Service
    - Handles user registration and authentication.
    - Built with **FastAPI and MySQL** for storing user data.
    - Issues **JWT tokens** for secure communication across services.

- Chat Service
    - Manages message storage and retrieval.
    - Stores chat history in a MySQL database.
    - Provides REST APIs for message operations.

- API Gateway
    - Acts as a **single entry point** for the frontend.
    - Handles **WebSocket connections** for real-time messaging.
    - Performs **JWT validation** and routes requests to appropriate services.
- Frontend (Next.js)
    - Provides a real-time chat interface.
    - Connects to the **API Gateway** via **WebSockets** and REST APIs.
- Databases
    - Each service has its **own MySQL database** (Auth DB, Chat DB, Test DB).
    - This separation ensures **data isolation** and **service autonomy**.

- Testing
    - Each service includes **pytest tests**.
    - Tests can be run **locally** or in **CI/CD pipelines** to ensure stability.

- CI/CD
    - GitHub Actions handles automated building, testing, and deployment.
    - Docker images for each service are built and pushed automatically.

This architecture ensures **high cohesion within services, low coupling between services**, and supports **horizontal scaling** as the application grows.

---
