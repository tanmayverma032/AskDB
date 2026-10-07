# 🚀 AskDB - AI Database Assistant

AskDB is a powerful, intelligent AI Database Assistant that allows you to chat with your SQL databases using natural language. Under the hood, it converts your questions into SQL queries, runs them against your database, and presents the results alongside comprehensive AI-driven analyses and visualizations.

## ✨ Features
- **🗣️ Natural Language Interface**: Query your DB without knowing SQL!
- **⚡ Fast and Reliable**: Powered by FastAPI for the backend.
- **🎨 Interactive UI**: Built with Streamlit for a chat-like, responsive experience.
- **📊 Auto-Visualizations**: Let AskDB choose the right charts for your data.
- **🔐 Secure Execution**: Read-only database access patterns recommended.

## 🛠️ Tech Stack
![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-1.25%2B-FF4B4B?logo=streamlit)
![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?logo=mysql)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)

## 🏗️ Architecture
```text
[ User ]  <--->  [ Streamlit Frontend ]  <--->  [ FastAPI Backend ]  <--->  [ LLM API ]
                                                          |
                                                          v
                                                    [ MySQL Database ]
```

## 📋 Prerequisites
- Python 3.10+
- MySQL Server (e.g., via XAMPP) running locally on port 3306, user `root`, no password, or Docker.

## 🚀 Quick Start
1. **Clone the repository**:
   ```bash
   git clone https://github.com/tanmayverma032/AskDB.git
   cd AskDB
   ```
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Set up MySQL**:
   Run the sample SQL file to populate the database:
   ```bash
   mysql -u root < database/sample_mysql.sql
   ```
4. **Configure environment variables**:
   Create a `.env` file in the root directory:
   ```env
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=
   DB_NAME=askdb_sample
   GEMINI_API_KEY=your_api_key_here
   ```
5. **Run the application**:
   ```bash
   python start.py
   ```

## 🐳 Docker Deployment
You can run the entire stack using Docker Compose:
```bash
docker-compose -f docker/docker-compose.yml up --build
```
This spins up the MySQL DB, FastAPI Backend, and Streamlit Frontend seamlessly.

## 📸 Screenshots
*(Add screenshots of your UI here!)*

## 📡 API Endpoints (Backend)
| Endpoint | Method | Description |
|---|---|---|
| `/api/chat` | POST | Submits a natural language query and returns results. |
| `/api/schema` | GET | Retrieves database schema information. |
| `/health` | GET | Health check endpoint. |

## 📁 Project Structure
```text
AskDB/
├── backend/            # FastAPI application
├── frontend/           # Streamlit application
├── database/           # SQL scripts and database setups
├── docker/             # Dockerfiles and Docker Compose
├── start.py            # Easy startup script
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## 🤝 Contributing
Contributions are welcome! Please open an issue or submit a pull request.

## 📜 License
This project is licensed under the MIT License.
