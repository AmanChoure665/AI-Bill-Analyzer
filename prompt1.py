import json

#Define the precise schema for the extracted invoice data
JSON_SCHEMA = {
    "invoice_no": "The unique invoice identifier.",
    "issue_date": "The datethe invoice was created (formate: MM/DD/YYYY).",
    "billed_to": "Name of the company / person to whome bill is charged.",
    "billed_by": "Name of the company who has issued the bill.",
    "description": "A list of individual service description",
    "ammount": "A list of bill ammonts for each individual servce (must be intger).",
    "grand_total": "The total amount in the bill (must be a single number, float or integer)."
}

def data_conversion(extracted_text: str) -> str:
    schema_string = json.dumps(JSON_SCHEMA, indent=2)
    
    return f"""
You are an expert in data extraction bot. Your sole task is to analyze the raw data from OCR text
from a single invoice and convert it into a valid JSON object based on the required schema.

#Required JSON SCHEMA
{schema_string}

#Extraction Instructions:
- **STRICTLY:** Return only valid JSON Object

-----
Raw Invoice text to analyze:
{extracted_text}

Return only valid JSON Object

-----
"""

# Backwards-compatible alias for existing imports using the misspelled name
data_convertion = data_conversion

