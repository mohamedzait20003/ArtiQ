# ECE 30816-Project: AI/ML Models Manager and Evaluation

This project is a web application for managing and evaluating AI/ML models. It consists of a Python backend and an Angular frontend.

## Project Structure

The project is organized into two main parts:

-   `frontend/`: Contains the Angular frontend application.
-   `backend/`: Contains the Python backend server.

## Getting Started

### Prerequisites

-   [Node.js and npm](https://nodejs.org/)
-   [Python 3](https://www.python.org/downloads/)
-   [Angular CLI](https://angular.io/cli) (`npm install -g @angular/cli`)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd <your-project-directory>
    ```

2.  **Set up Python Virtual Environment:**
    It is recommended to use a virtual environment to manage Python dependencies.

    - Create a virtual environment (e.g., named `.venv`):
      ```bash
      python -m venv .venv
      ```

    - Activate the virtual environment:
      - On Windows:
        ```powershell
        .venv\Scripts\Activate.ps1
        ```
      - On macOS/Linux:
        ```bash
        source .venv/bin/activate
        ```

3.  **Install backend dependencies:**
    With the virtual environment activated, install the required packages:
    ```bash
    pip install -r backend/requirements.txt
    ```

4.  **Install frontend dependencies:**
    ```bash
    cd frontend
    npm install
    cd ..
    ```

### Running the Application

1.  **Start the backend server:**
    ```bash
    cd backend
    python src/main.py
    ```
    The backend server will start.

2.  **Start the frontend development server:**
    ```bash
    cd frontend
    ng serve
    ```
    Navigate to `http://localhost:4200/`. The application will automatically reload if you change any of the source files.

## Further Help

To get more help with the Angular CLI, use `ng help` or go check out the [Angular CLI Overview and Command Reference](https://angular.io/cli) page.
