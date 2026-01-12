# AI Bill Analyzer

AI Bill Analyzer is an AI-assisted application that automates the processing of bill images to extract, categorize, store, and analyze expense data.  
The system combines OCR, Large Language Models (LLMs), and a human-in-the-loop workflow to ensure reliable and explainable expense tracking.

This project is intentionally designed as an **AI-assisted system**, not a fully autonomous one.

---

## Features

- Bill image preprocessing to improve OCR accuracy  
- OCR-based text extraction using Tesseract  
- LLM-based structured invoice data extraction  
- LLM-based expense categorization  
- Human-in-the-loop review and correction before saving data  
- SQLite database for persistent expense storage  
- Natural language querying of expenses (Text-to-SQL)  
- Interactive Streamlit dashboard  

---

## High-Level Workflow

1. Upload bill image  
2. Image preprocessing (grayscale, blur, binarization)  
3. OCR text extraction  
4. LLM-based invoice data extraction  
5. LLM-based expense categorization  
6. User review and correction  
7. Data storage in SQLite  
8. Natural language queries converted to SQL  

---

## Tech Stack

- **Language:** Python  
- **Frontend:** Streamlit  
- **OCR:** Tesseract OCR  
- **LLMs:** Ollama (local runtime)  
- **Database:** SQLite  
- **Image Processing:** OpenCV  
- **Data Handling:** Pandas  

---

## Project Structure

AI-Bill-Analyzer/
│
├── frontend2.py # Main Streamlit application
├── table_creation.py # Database schema creation
├── image_cleaning.py # Image preprocessing
├── ocr_processor.py # OCR processing
├── parser.py # Extraction & categorization orchestration
├── data_insertion.py # Database insertion logic
│
├── prompt1.py # Invoice extraction prompt
├── prompt2.py # Expense categorization prompt
├── prompt3.py # Natural language to SQL prompt
│
├── ollama1.py # LLM invoice extraction
├── ollama2.py # LLM expense categorization
├── ollama3.py # LLM Text-to-SQL
│
├── requirements.txt
├── .env.example
├── README.md
└── .gitignore

yaml
Copy code

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/AI-Bill-Analyzer.git
cd AI-Bill-Analyzer
2. Create a Virtual Environment (Recommended)
bash
Copy code
python -m venv venv
Activate the environment:

Windows

bash
Copy code
venv\Scripts\activate
Linux / macOS

bash
Copy code
source venv/bin/activate
3. Install Python Dependencies
bash
Copy code
pip install -r requirements.txt
4. Install Tesseract OCR
Tesseract must be installed separately.

Windows:
https://github.com/UB-Mannheim/tesseract/wiki

After installation, update the Tesseract path in ocr_processor.py if required:

python
Copy code
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
5. Install Ollama (Local LLM Runtime)
Download and install Ollama:

arduino
Copy code
https://ollama.com
Pull the required model:

bash
Copy code
ollama pull glm-4.6:cloud
Make sure Ollama is running before starting the application.

6. Environment Variables
Create a .env file using .env.example as reference:

bash
Copy code
cp .env.example .env
Note: .env is excluded from version control for security reasons.

7. Create the Database
bash
Copy code
python table_creation.py
This will create the SQLite database and required tables.

8. Run the Application
bash
Copy code
streamlit run frontend2.py
The Streamlit app will open automatically in your browser.

How to Use the Application
Upload a bill image (JPG / JPEG / PNG)

Review the cleaned image and OCR text

Verify and correct extracted invoice details

Save the expense data to the database

View and filter stored expenses

Ask natural language questions such as:

“Show total food expenses”

“List expenses by category”

“What is the total amount spent?”

Deployment Notes
This project uses:

A local LLM runtime (Ollama)

System-level OCR (Tesseract)

Due to these dependencies, the full system is not suitable for Streamlit Cloud deployment.

For interviews and demos:

The project is run locally

A live demo or recorded walkthrough is recommended

In production, Ollama can be replaced with an API-based LLM

Design Considerations
AI is used as an assistive component, not an autonomous decision-maker

Human-in-the-loop validation improves reliability

Modular architecture allows easy replacement of OCR or LLM components

Defensive parsing and fallback logic handle imperfect AI outputs

Future Improvements
Replace local LLM with cloud-based LLM APIs

Add authentication and multi-user support

Improve OCR accuracy for low-quality images

Add SQL safety validation for generated queries

Containerize the system using Docker

Disclaimer
This project is built for educational and demonstration purposes.
AI outputs are probabilistic and should always be reviewed before use in real-world financial systems.

Author
Aman Choure
B.Tech (AIML) | AI Enthusiast
