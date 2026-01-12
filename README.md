# AI Bill Analyzer

AI Bill Analyzer is an AI-assisted application for processing bill images and extracting structured expense data.  
It uses OCR and Large Language Models (LLMs) with a human-in-the-loop approach to ensure reliable expense tracking and analysis.

---

## Key Features

- Bill image preprocessing for better OCR accuracy  
- OCR-based text extraction using Tesseract  
- LLM-based invoice data extraction  
- LLM-based expense categorization  
- Human-in-the-loop review before saving data  
- SQLite database for expense storage  
- Natural language querying of expenses (Text-to-SQL)  
- Streamlit-based interactive dashboard  

---

## Tech Stack

- Python  
- Streamlit  
- Tesseract OCR  
- Ollama (local LLM runtime)  
- SQLite  
- OpenCV  
- Pandas  

---

## How to Run

```bash
pip install -r requirements.txt
python table_creation.py
streamlit run frontend2.py
Tesseract OCR and Ollama must be installed separately.
```

---
  
##Notes
This project uses a local LLM runtime, so it is intended to be run locally.

AI is used as an assistive component, not a fully autonomous system.

# Author
  Aman Choure
  B.Tech (AIML)
