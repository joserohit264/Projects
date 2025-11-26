# Secure Password Manager

## Problem Statement

In an era of increasing digital surveillance and frequent data breaches, relying on third-party cloud providers to store sensitive credentials poses a significant risk. Many commercial password managers are closed-source, expensive, or bloated with unnecessary features.

This project aims to solve this by providing a **lightweight, production-grade, self-hosted password manager**. It prioritizes **data sovereignty and security**, implementing a zero-knowledge architecture where encryption keys are unique to each user and derived from their master password. It offers a modern, responsive user interface without the complexity of heavy frontend build chains, making it instantly deployable and easy to audit.

## Tech Stack

### Backend
*   **Language:** Python 3.13
*   **Framework:** Flask (Lightweight WSGI web application framework)
*   **Database:** SQLite (with SQLAlchemy ORM)
*   **Cryptography:** PyCryptodome (AES-256-CBC, PBKDF2-HMAC-SHA256)
*   **Authentication:** JWT (JSON Web Tokens)

### Frontend
*   **Core:** Vanilla JavaScript (ES6+), HTML5
*   **Styling:** Tailwind CSS (via CDN)
*   **Icons:** Lucide Icons
*   **Notifications:** Toastify.js
*   **Architecture:** Single Page Application (SPA) with hash-based routing (No-Build approach)

### DevOps
*   **Containerization:** Docker

## Features

*   **Zero-Knowledge Encryption**: Passwords are encrypted using AES-256-CBC with a unique Initialization Vector (IV) for every entry. Encryption keys are derived dynamically from the user's master password and a unique salt.
*   **Security Dashboard**: Real-time analysis of your vault, providing a security score, identifying weak passwords, and detecting password reuse.
*   **Secure Vault**:
    *   Add, Edit, Delete, and View passwords.
    *   Integrated strong password generator.
    *   One-click copy to clipboard.
    *   Toggle password visibility.
*   **Modern UI**: Clean, responsive interface with automatic Dark/Light mode support.
*   **Lightweight**: No `node_modules` hell. The frontend runs directly in the browser.
*   **Docker Ready**: Fully containerized for easy deployment.

## Getting Started

### Run with Docker

You can pull the pre-built image from Docker Hub or build it locally.

**Pull from Docker Hub:**
```bash
docker run -p 5000:5000 joserohit264/secure-password-manager:latest
```

**Build Locally:**
```bash
docker build -t secure-password-manager .
docker run -p 5000:5000 secure-password-manager
```

Access the application at `http://localhost:5000`.


## Security Architecture

1.  **User Registration**: A unique 32-byte salt is generated. The master password is hashed using PBKDF2 (100,000 iterations) for authentication.
2.  **Login**: The server verifies the hash. Upon success, a *separate* encryption key is derived from the master password and salt. This key is temporarily cached in the secure session (server-side) to enable decryption of the user's vault.
3.  **Data Storage**:
    *   **Database**: Stores `IV + Ciphertext`.
    *   **Encryption**: AES-256-CBC.
    *   **Isolation**: Each user has a unique key; User A cannot decrypt User B's data even if they have access to the database.
