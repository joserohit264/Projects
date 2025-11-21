#  ECC Encrypted Messenger (Alice & Bob)
A modern, browser-based encrypted messaging demo built using **Elliptic Curve Cryptography (ECC)**, **ECDH key exchange**, and **AES-256-GCM symmetric encryption**.  
This project visually demonstrates how two users (Alice & Bob) can securely exchange encrypted messages using elliptic curve public-key cryptography — all within a simple, elegant web interface.

---
##  Tech Stack

### **Backend Technologies**
- **Python 3.x** — Core programming language
- **Flask** — Lightweight web framework for routing and session handling
- **Cryptography Library (Python)**  
  - Elliptic Curve Cryptography (**ECC**, SECP256R1 / SECP256K1)  
  - **ECDH** (Elliptic Curve Diffie–Hellman) for shared key generation  
  - **HKDF (SHA-256)** for secure key derivation  
  - **AES-256-GCM** for authenticated encryption and decryption
- **Jinja2** — Templating engine for rendering dynamic HTML

### **Frontend Technologies**
- **HTML5** — Page structure and layout  
- **CSS3** — UI theme with responsive design  
- **Vanilla JavaScript** — UI interactions and form behavior

### **Security Techniques Implemented**
- **ECC key pair generation** for both Alice and Bob  
- **ECDH shared secret computation**  
- **Authenticated encryption** using AES-256-GCM  
- **Secure key derivation** using HKDF (HMAC-SHA256)  
- **Session-isolated cryptographic workflow** (demo-safe)

### **Development Environment**
- Runs entirely on **localhost**
- No virtual environment required (runs directly with system Python)
- No external database or services needed  


---

##  Features

###  **1. Fully Encrypted Messaging**
- Alice sends encrypted messages to Bob  
- Bob receives ciphertext  
- Bob decrypts using his private key  
- And vice-versa  

###  **2. ECC-Based Secure Communication**
- Uses **EC key pairs** (SECP256R1 or SECP256K1)
- Establishes shared secret using **ECDH**
- Encrypts messages using **AES-256-GCM**
- Secure key derivation with **HKDF (SHA-256)**

###  **3. Modern Web UI (Dark Blue Theme)**
- Two elegant side-by-side panels:
  - **Alice Panel**
  - **Bob Panel**
- Read-only encrypted message boxes
- Decrypted results highlighted in a special result box
- “Reset Keys” button to reset the key-pairs

###  **4. Runs Entirely on Localhost**
No database, no external calls — safe for demos, learning, and cryptography experiments.

-----
