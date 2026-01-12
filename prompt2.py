
#category bucket
categories = [
    "food", "logistic", "drinks", "Travel",  "Grocery expense","Utilities", "Other"
]

def build_category_prompt(description_texts: list[str]) -> str:
    category_list = ",".join(categories)
    descriptions_str = "\n".join([f"- {desc}" for desc in description_texts])
    return f"""

You are an expert classification agent. Your task is to analyze a list of service descriptions and assign each one to one of the predefined categories.

#predefined categories:
{category_list}

#Instructions: 
- **STRICTLY** return a JSON array of strings, where each string is the chosen category name for the corresponding service description.
- If the description is vague or doesn't fit, choose "Other".
- The output MUST match one of the categories exactly.
- DO NOT return any explanation or markdown outside the JSON array.

---
Service Descriptions to categorize:
{descriptions_str}

JSON Array of Categories:
"""