# Three-Tier Cloud Lab Application

A cloud-neutral sample application for the GCP, AWS and Azure three-tier lab.

## Architecture

Browser
  -> Frontend (React/Vite + Nginx)
  -> Backend (FastAPI)
  -> MySQL

The frontend is designed to proxy `/api/*` to the backend, so the browser does not need direct access to the private backend.

## Local development

Requirements:
- Docker Desktop
- Docker Compose

Run:

```bash
docker compose up --build
```

Open:
- http://localhost:8080

Default lab user:
- Username: admin
- Password: ChangeMe123!

Change the password/secret before any real deployment.

## Project structure

```text
frontend/       React/Vite UI + Nginx reverse proxy
backend/        FastAPI REST API
db/             MySQL initialization
docker-compose.yml
.env.example
```

## Application flow

1. User opens the React login page.
2. React calls `POST /api/login`.
3. Nginx proxies `/api/*` to the FastAPI backend.
4. FastAPI validates the user against MySQL.
5. FastAPI returns a JWT.
6. React uses the JWT for protected API calls.
7. FastAPI talks to MySQL over the private database network.

## Cloud deployment model

The same application containers can be used in all three clouds.

### GCP
- Frontend: Cloud Run
- Backend: Compute Engine VM
- Database: Cloud SQL for MySQL
- Frontend-to-backend: private VPC connectivity / reverse proxy
- VM administration: IAP
- VM outbound access: Cloud NAT

### AWS
- Frontend: App Runner/ECS/Fargate (or another selected web PaaS)
- Backend: EC2 private subnet
- Database: RDS for MySQL
- Frontend-to-backend: private networking/reverse proxy pattern
- VM administration: SSM Session Manager
- VM outbound access: NAT Gateway

### Azure
- Frontend: Azure App Service
- Backend: Azure VM
- Database: Azure Database for MySQL Flexible Server
- Frontend-to-backend: VNet/private networking pattern
- VM administration: Azure Bastion
- VM outbound access: NAT Gateway

The cloud-specific networking and identity configuration belongs in the infrastructure layer; the application code remains the same.

## Important security note

This is a lab application. Before production use:
- Replace the demo credentials.
- Store JWT secrets in the cloud secret manager.
- Use HTTPS everywhere.
- Use a proper migration system such as Alembic.
- Use managed identity/workload identity where possible.
- Add rate limiting, audit logging, CSRF protection where applicable, and stronger authorization.
