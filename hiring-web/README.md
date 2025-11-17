# Hiring Web Application

This repository contains a full-stack web application designed to streamline the hiring process. It includes a backend built with Node.js, a frontend developed with Angular, and a Flask-based server for additional functionalities like CV parsing and LinkedIn scraping.

## Project Structure

- **ai-hiring-backApp/**: Backend application built with Node.js and Express.
- **ai-hiring-frontAPP/**: Frontend application built with Angular.
- **flask_server/**: Python-based server for CV parsing and LinkedIn scraping.

## Getting Started

### Prerequisites
- Node.js
- Python 3.x
- Angular CLI
- MongoDB

### Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd hiring-web
   ```

2. Install dependencies for each component:
   - Backend:
     ```bash
     cd ai-hiring-backApp
     npm install
     ```
   - Frontend:
     ```bash
     cd ai-hiring-frontAPP
     npm install
     ```
   - Flask Server:
     ```bash
     cd flask_server
     pip install -r requirements.txt
     ```

### Running the Applications
- **Backend**:
  ```bash
  cd ai-hiring-backApp
  npm start
  ```
- **Frontend**:
  ```bash
  cd ai-hiring-frontAPP
  npm start
  ```
- **Flask Server**:
  ```bash
  cd flask_server
  python main.py
  ```

## License
This project is licensed under the MIT License.