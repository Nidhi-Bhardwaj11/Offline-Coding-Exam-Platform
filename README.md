Offline Coding Exam Platform 🐈
Overview
The Offline Coding Exam Platform is a secure and reliable tool designed to conduct coding exams in an offline environment. It ensures minimal chances of cheating while providing a seamless user experience for candidates to attempt coding problems. The platform supports multiple programming languages, real-time feedback, and code persistence across sessions.

Features
Secure Login System: User authentication via a dedicated login page.
Multi-language Support: Supports Python, C, C++, Java, and JavaScript.
Interactive Code Editor:
Real-time feedback with test case evaluation.
Code persistence for previously written solutions.
Offline Functionality: Designed to work in isolated environments to prevent unauthorized access and ensure reliability.
Problem Management: Dynamic problem display and constraint explanations.
Technologies Used
Frontend
Streamlit: For creating the interactive and user-friendly interface.
Extra Streamlit Components: For managing cookies and enhancing UI/UX.
Backend
Flask: For handling API requests and managing user data.
CSV Storage: To securely store and retrieve user credentials and problem data.
How It Works
Login:
Users log in using a secure login page. Authentication is managed via cookies to track user sessions.

Problem Selection:
Problems are fetched dynamically and displayed in the sidebar for selection.

Coding Environment:

The app features an integrated code editor with syntax highlighting and language-specific support.
Code persistence ensures users can resume their work without losing progress.
Submission & Evaluation:

Users submit solutions via the platform.
The backend evaluates the code and provides real-time feedback on test cases.
Secure & Offline:

The platform operates offline to prevent external interference.
Exam data is securely stored and accessed locally.
Installation & Setup
Prerequisites
Python 3.8 or higher
Flask
Streamlit
Required Python libraries:
Copy code
pip install streamlit flask pandas requests extra-streamlit-components
Steps
Clone this repository:
bash
Copy code
git clone https://github.com/Nidhi-Bhardwaj11/offline-coding-exam-platform
Navigate to the project directory:
bash
Copy code
cd offline-coding-exam-platform
Start the backend server:
bash
Copy code
python backend/server.py
Run the Streamlit frontend:
bash
Copy code
streamlit run app.py
Access the platform in your browser at http://localhost:8501.
Project Structure
bash
Copy code
offline-coding-exam-platform/
│
├── backend/
│   ├── server.py          # Flask backend logic
│   └── data/
│       ├── users.csv      # User credentials
│       └── problems.csv   # Problem statements
│
├── app.py                 # Streamlit frontend logic
├── code_editor.py         # Code editor component
├── README.md              # Project documentation
└── requirements.txt       # Python dependencies
