#  Secure Password Manager

A multi-user, AES-256 encrypted password manager with a modern Tkinter GUI, dark mode, sidebar navigation, animated transitions, CLI support, and Dockerized deployment.

---

##  Problem Statement

Managing passwords securely is a challenge for individuals and organizations.  
People often reuse passwords or store them in insecure places like text files or browsers.

This project provides a **fully encrypted, local, multi-user password manager** that ensures:

- Safe storage using AES-256 encryption  
- Unique per-user cryptographic keys  
- Local database storage secured with PBKDF2  
- User-friendly GUI and CLI modes  
- Portable Docker deployment  

---
##  Tech Stack

- **Python 3.12**  
- **Tkinter** (GUI)  
- **SQLite3** (local encrypted DB storage)  
- **cryptography** (AES encryption)  
- **hashlib / PBKDF2** (secure password hashing)  
- **pyperclip** (clipboard)  
- **Docker** (containerization)

---
##  Features

###  Security
- AES-256 encryption  
- PBKDF2 password hashing  
- Per-user encryption salt  
- Encrypted SQLite database  
- Hidden password input  

###  User Management
- New user registration  
- Login authentication  
- Per-user password vault  

###  Modern GUI (Tkinter)
- Sun Valley (Win11-inspired) theme  
- Dark Mode toggle  
- Sidebar navigation  
- Dashboard overview  
- Animated transitions  
- Profile & settings window  

###  CLI Version
- Add, view, and delete passwords  
- Encrypted storage  
- Password generator  
- Docker-safe clipboard behavior  

###  Docker
- CLI and GUI images available  
- GUI supported via X11 forwarding  
- Clipboard support inside container (xclip/xsel)

---



##  DockerHub Images

### GUI Image
``` bash 
docker pull joserohit264/secure-password-manager:gui
```
### CLI Image
```bash
docker pull joserohit264/secure-password-manager:cli
```
