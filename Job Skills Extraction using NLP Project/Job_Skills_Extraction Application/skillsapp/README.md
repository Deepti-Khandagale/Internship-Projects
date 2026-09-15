# 💼 AI Job Skill Extractor

## Day 19 - Build an Application/API

This project converts a job skill extraction system into a usable web application.

The application allows users to register, login, enter a job description, extract skills and map those skills to categories.

---

## Features

- User Registration
- User Login
- Personalized User Dashboard
- Displays logged-in user's Name
- Displays logged-in user's Email
- Job Description Input
- Skill Extraction
- Skill Normalization
- Category Mapping
- Dataset-based Skill Detection
- Technology Recommendation
- Streamlit Web Interface
- SQLite Authentication Database

---

## Dataset

The application uses the following dataset:

`data/clean_jobs_descriptions_combined.csv`

The dataset contains 8,785 job records and 13 columns.

Important columns include:

- Job Description
- clean_description
- skills
- extracted_skills
- categories

---

## Architecture

User
↓
Register / Login
↓
Web Interface
↓
Job Description
↓
Preprocessing
↓
Skill Extraction
↓
Skill Normalization
↓
Category Mapping
↓
Final Skills
↓
Technology Recommendation

---

## Technologies

- Python
- Streamlit
- Pandas
- SQLite
- Regular Expressions

---

## Project Structure

day19_skill_extractor/

├── app.py

├── requirements.txt

├── README.md

├── data/

│   └── clean_jobs_descriptions_combined.csv

├── model/

│   ├── __init__.py

│   └── skill_extractor.py

└── utils/

    ├── __init__.py

    ├── auth.py

    └── data_loader.py

---

## Installation

Create a virtual environment:

python -m venv venv

Activate the environment on Windows:

venv\Scripts\activate

Install the required packages:

pip install -r requirements.txt

---

## Run Application

Run:

streamlit run app.py

The application will open in a web browser.

---

## Example Input

Looking for Data Analyst with SQL, Python, Power BI and Excel experience.

---

## Expected Output

Detected Skills:

Python
SQL
Power BI
Excel

Categories:

Python → Programming

SQL → Programming / Database

Power BI → Data Analytics

Excel → Analytics

---

## Authentication

Users can register with:

- Name
- Email
- Password

After successful login, the application displays:

Name: Registered User

Email: Registered Email

The user can then access the skill extraction dashboard.

---

## Database

SQLite is used for storing user registration information.

The database file `users.db` is automatically created when the application starts.

---

## Recommended Technology

For a simple web application:

Streamlit

For exposing the system as an API:

FastAPI