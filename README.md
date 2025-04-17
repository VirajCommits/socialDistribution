markdown
[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/zUKWOP3z)  
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)  
[![Languages: Python & JavaScript](https://img.shields.io/badge/Languages-Python%20%7C%20JavaScript-blue.svg)]  
[![Deployment: Heroku](https://img.shields.io/badge/Deployment-Heroku-green.svg)]

# CMPUT404‑project‑socialdistribution

A **decentralized social blogging platform** for CMPUT404’s “Distributed Social Networks” assignment.  
Host your own Django node, follow peers on other servers, and share/aggregate posts, likes, and comments—all via a simple RESTful inbox API.

Project spec ➡️ https://uofa-cmput404.github.io/general/project.html

---

## 🌟 Features

| Feature                   | Description                                                                                     |
|---------------------------|-------------------------------------------------------------------------------------------------|
| **Autonomous Nodes**      | Each instance runs independently—keep full control of user data, moderation, and uptime.        |
| **RESTful Inbox Model**   | Standardized inbox endpoints for sending/receiving posts, comments, and likes.                 |
| **Flexible Privacy**      | Choose per-post visibility: **public**, **unlisted**, or **friends‑only**.                      |
| **Real‑Time Aggregation** | Follow authors across any node; see a live, unified feed that updates with new content.         |
| **Modular & Scalable**    | Built on Django and Tailwind; designed for horizontal scaling, containerization, and caching.   |
| **Clean UI**              | Responsive interface with Tailwind CSS, minimal JS, and accessibility-friendly design.          |

---

## 🏛 Architecture

```text
+-------------+          +--------------------+          +-------------+
|             |  POST    |                    |  PUSH    |             |
|   Client    +--------->+  Node A (Django)   +--------->+  Node B     |
| (Browser)   |  FETCH   |   Inbox & Storage  |  FETCH   |  (Django)   |
+------+------+\        +----+---------------+         +------^------+
       |        \ GET           |                                |
       |         \ GET          v                                |
       |          +--------------------+                         |
       |          |  Aggregation Feed  |<------------------------+
       |          +--------------------+
       |
       v
+-------------+
| API / Redoc |
+-------------+
```
*(Simplified request flow between federated nodes and clients.)*

---

## 🚀 Demo & Spec

- **Live Sample Nodes:**  
  - https://social-distribution-tqyoung.herokuapp.com/  
  - https://transparent-jwan.herokuapp.com/  
- **Assignment Details:**  
  https://uofa-cmput404.github.io/general/project.html

---

## 🛠️ Requirements

- **Python** ≥ 3.11  
- **Node.js** ≥ 20 (for separate frontend)  
- **Database**: PostgreSQL (production) or SQLite (dev)  
- **Git**  

---

## ⚙️ Installation & Setup

```bash
# 1. Clone this repository
git clone https://github.com/VirajCommits/social-distribution.git
cd social-distribution

# 2. Create & activate a Python virtual environment
python -m venv .venv
source .venv/bin/activate       # macOS/Linux
.venv\Scripts\activate          # Windows

# 3. Install backend dependencies
pip install -r requirements.txt

# 4. (Optional) Build frontend assets
cd frontend
npm install
npm run build
cd ..

# 5. Copy & edit environment config
cp .env.example .env
# Open .env and set:
#   SECRET_KEY=your_django_secret_key
#   DATABASE_URL=postgres://user:pass@host:port/dbname

# 6. Run database migrations and start
python manage.py migrate
python manage.py runserver
```

Browse to `http://localhost:8000` to see your node in action.

---

## 📚 API Documentation

Interactive OpenAPI docs powered by ReDoc:

```
http://localhost:8000/redoc/
```

---

## 🔍 Usage Examples

- **Create a Post**  
  ```bash
  curl -X POST http://localhost:8000/api/inbox/ \
    -H "Content-Type: application/json" \
    -d '{"type":"post","author":"http://nodeA/users/alice/","content":"Hello federated world!"}'
  ```
- **Fetch Aggregated Feed**  
  ```bash
  curl http://localhost:8000/api/following/posts/
  ```

---

## 🧪 Testing

Run the full test suite covering models, views, and API endpoints:

```bash
python manage.py test
```

---

## 📦 Deployment

### Heroku

```bash
heroku create your-app-name
git push heroku main
```
Heroku will detect Python, install dependencies, run migrations, and launch your server automatically.

### Docker (optional)

```bash
docker build -t social-distribution .
docker-compose up
```
Containerized setup for local or production use.

---

## 🤝 Contributing

We welcome contributions! Please:

1. **Fork** the repo  
2. **Branch**: `git checkout -b feature/YourFeature`  
3. **Commit**: `git commit -m "Add YourFeature description"`  
4. **Push**: `git push origin feature/YourFeature`  
5. **PR**: Open a Pull Request and describe your changes

Refer to `CONTRIBUTING.md` for coding standards and commit guidelines.

---

## 📜 License

This project is licensed under the **Apache License 2.0**.  
See the full text in [LICENSE](LICENSE).

---

## 👩‍💻 Authors & Acknowledgments

- Sanket Lamba  
- Gordon Chiang  
- Pranav Mehra  
- Viraj Murab  
- Rakshit  
- Darren Krzyczkowski  

*Built for CMPUT404: Distributed Social Networks*  
Enjoy exploring decentralized social blogging!
