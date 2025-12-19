# Enterprise Organization Management System

> **Production-Ready Multi-Tenant Backend Service**  
> Built with **FastAPI**, **MongoDB**, and **Enterprise Best Practices**

[![Deploy with Vercel](https://vercel.com/button)](https://enterprise-organization-management.vercel.app/docs)

---

## Table of Contents
1. [Overview](#overview)
2. [Key Enterprise Features](#key-enterprise-features)
3. [Technology Stack](#technology-stack)
4. [Architecture](#architecture)
5. [Installation & Setup](#installation--setup)
6. [API Documentation & Examples](#api-documentation--examples)
7. [Project Structure](#project-structure)
8. [Troubleshooting](#troubleshooting)

---

## Overview

This is a robust, enterprise-grade backend service designed for managing organizations in a multi-tenant environment. Unlike simple CRUD applications, this system implements advanced architectural patterns used in real-world SaaS platforms.

It features a **Master Database** for metadata and **Dynamic Collections** for tenant data isolation, ensuring scalability and security.

---

## Key Enterprise Features

### 1. **Multi-Tenant Architecture**
-   **Isolation**: Each organization gets its own dynamic MongoDB collection (e.g., `org_google`, `org_amazon`).
-   **Scalability**: Prevents a single massive collection from slowing down queries.
-   **Security**: Data leakage between tenants is architecturally minimized.

### 2. **Soft-Delete with Audit Trail**
-   **Metadata Retention**: Deleted organizations are flagged (`is_deleted=True`) in the master DB.
-   **Resource Cleanup**: The actual dynamic collection is **hard-deleted** to free space.
-   **Audit**: Records `deleted_at` and `deleted_by` (Admin ID) for regulatory compliance.

### 3. **Organization-Level Rate Limiting**
-   **Fairness**: Rate limits are applied **per organization** (via JWT context), not just per IP.
-   **Impact**: One abusive tenant cannot degrade performance for other tenants on the same network.
-   **Configurable**: Limits (e.g., 100 req/min) are adjustable via environment variables.

### 4. **Secure Authentication & Authorization**
-   **JWT**: Stateless authentication with organization-scoped tokens.
-   **Bcrypt**: Industry-standard password hashing.
-   **Role-Based**: Admins can only modify their own organization's data.

---

## Technology Stack

-   **Language**: Python 3.9+
-   **Framework**: FastAPI (High performance, async)
-   **Database**: MongoDB (v4.6+ driver, Async Motorola)
-   **Validation**: Pydantic v2
-   **Auth**: Python-JOSE (JWT), Passlib (Bcrypt)
-   **Middleware**: SlowAPI (Rate limiting)

---

## Architecture

### Database Schema Design

1.  **Master Collection (`organizations`)**:
    -   Stores metadata: `name`, `admin_email`, `collection_name`, `is_deleted`.
    -   Acts as the directory for all tenants.

2.  **Dynamic Collections (`org_<name>`)**:
    -   Created automatically when an organization is registered.
    -   Stores tenant-specific data (e.g., Admin users, and future tenant entities).

### Safe Data Migration
-   When an organization name is updated, the system **automatically renames** the collection and migrates all data safely in a transaction-like sequence.

---

## Installation & Setup

### Prerequisites
-   **Python 3.9+** installed/added to PATH (`python --version`)
-   **MongoDB** installed and running (`net start MongoDB` or `mongod`)

### Quick Start

1.  **Clone the Repository**
    ```powershell
    cd Enterprise_Organization_Management_System
    ```

2.  **Run the Setup Script (Windows)**
    ```powershell
    .\setup.ps1
    ```
    *Alternatively, manually create venv and pip install -r requirements.txt*

3.  **Start the Server**
    ```powershell
    .\start.bat
    ```
    *Or manually:* `uvicorn app.main:app --reload`

### Configuration (`.env`)
The setup script creates this automatically. Key variables:
```env
MONGODB_URL=mongodb://localhost:27017
SECRET_KEY=<your_generated_secret_key>
RATE_LIMIT_PER_ORG=100
```

---

## API Documentation & Examples

**Interactive Docs**: Visit [http://localhost:8000/docs](http://localhost:8000/docs) for Swagger UI.

### 1. Create Organization
**POST** `/organizations/`
```json
// Request
{
  "name": "Tesla Inc",
  "description": "Electric Vehicles",
  "admin_email": "elon@tesla.com",
  "admin_name": "Elon Musk",
  "admin_password": "SecurePassword123!"
}
```

### 2. Admin Login
**POST** `/auth/login`
```json
// Request
{
  "email": "elon@tesla.com",
  "password": "SecurePassword123!"
}

// Response
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1Ni...",
    "admin_id": "...",
    "organization_id": "..."
  }
}
```

### 3. Update Organization
**PUT** `/organizations/{id}` (Requires Auth Header)
-   **Header**: `Authorization: Bearer <access_token>`
-   **Body**:
    ```json
    { "name": "Tesla Motors", "description": "Updated Description" }
    ```
    *Note: Changing the name will trigger a Safe Data Migration.*

### 4. Delete Organization
**DELETE** `/organizations/{id}` (Requires Auth Header)
-   **Header**: `Authorization: Bearer <access_token>`
-   **Effect**: Soft-deletes metadata, hard-deletes collection, logs action.

---

## Project Structure

```
Enterprise_Organization_Management_System/
├── app/
│   ├── main.py              # App Entry Point
│   ├── core/                # Config, Security, JWT
│   ├── db/                  # MongoDB Connection & Repositories
│   ├── models/              # Pydantic Schemas
│   ├── routers/             # API Endpoints
│   ├── services/            # Business Logic (Atomic Ops, Migrations)
│   └── middleware/          # Rate Limiting
├── .env                     # Secrets
├── requirements.txt         # Dependencies
├── start.bat                # Startup Script
└── README.md                # This file
```

---

## Troubleshooting

**Q: "Connection Refused" / WinError 10061**
A: MongoDB is not running. Run `net start MongoDB` in Administrator PowerShell.

**Q: Import Errors**
A: Ensure your virtual environment is active (`.\venv\Scripts\activate`) and you have installed dependencies (`pip install -r requirements.txt`).

**Q: Password validation error**
A: Passwords must be at least 8 chars. We use `bcrypt` for secure hashing.

---

**Built by Arvind Pandey** | *Enterprise Grade. Production Ready.*
