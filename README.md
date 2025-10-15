# Agentic Graph RAG - Lyzr Hackathon

**Production-grade multimodal database architecture for intelligent knowledge graph construction and retrieval.**

[![Documentation](https://img.shields.io/badge/docs-GitBook-blue)](https://contactingharshit.gitbook.io/lyzr-hack/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📚 Documentation

**For a complete guide to this project, including setup, architecture, and contribution guidelines, please see our documentation on GitBook:**

## ➡️ [**contactingharshit.gitbook.io/lyzr-hack/**](https://contactingharshit.gitbook.io/lyzr-hack/)

---

## 🚀 Quick Start

For detailed setup instructions, see the [**Getting Started**](https://contactingharshit.gitbook.io/lyzr-hack/getting-started) guide in our documentation.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/harshit-codes/lyzr-hackathon.git
    cd lyzr-hackathon
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure your environment:**
    ```bash
    cp .env.example .env
    # Edit .env with your credentials
    ```

4.  **Run the demo:**
    ```bash
    streamlit run code/streamlit_app.py
    ```

---

## 🏗️ Project Structure

*   `code/`: The core source code for the project, organized by component:
    *   `graph_rag/`: Core data models and database functionality.
    *   `superscan/`: Document ingestion and schema creation.
    *   `superkb/`: Knowledge base construction.
    *   `superchat/`: Conversational AI and agentic retrieval.
*   `docs/`: The source for our GitBook documentation.
*   `notes/`: Internal development notes and archived documents.

---

## 🚀 Deployment

### CI/CD Pipeline

This project includes automated deployment to Snowflake using GitHub Actions. The CI/CD pipeline automatically deploys the Streamlit application on every push to the main branch.

**Pipeline Features:**
- Automated testing and deployment
- Secure credential management via GitHub secrets
- File upload to Snowflake stages
- Production deployment to Snowflake Streamlit

**For detailed information about the CI/CD setup, challenges faced, and solutions implemented, see:**
- [CI/CD Challenges and Solutions](docs/CI_CD_CHALLENGES.md)

### Manual Deployment

For manual deployment or troubleshooting, see the [Deployment Guide](https://contactingharshit.gitbook.io/lyzr-hack/deployment) in our documentation.

---

## 🤝 Contributing