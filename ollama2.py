from prompt2 import build_category_prompt
import subprocess
import re
import json

def get_category_from_ollama(description_texts: list[str]) -> list[str]:
    # build_category_prompt already expects a list of strings
    prompt = build_category_prompt(description_texts)


    # Execute ollama subprocess (wrap to surface clearer errors)
    try:
        process = subprocess.Popen(
            ["ollama", "run", "glm-4.6:cloud"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
    except FileNotFoundError as e:
        raise RuntimeError("'ollama' executable not found. Is Ollama installed and on PATH?") from e

    output, error = process.communicate(input=prompt)

    if process.returncode != 0:
        return ["Uncategorized LLM Error"]

    # The LLM is instructed to return a JSON array of strings.
    # We need to extract and parse this JSON.
    cleaned_output = output.strip()
    json_match = re.search(r'\[[\s\S]*?\]', cleaned_output, re.DOTALL)
    
    if json_match:
        json_string = json_match.group(0)
        try:
            categories = json.loads(json_string)
            if isinstance(categories, list) and all(isinstance(c, str) for c in categories):
                return categories
            else:
                print(f"Warning: LLM returned non-list or non-string categories: {json_string}")
                return ["Other"] * len(description_texts) # Fallback
        except json.JSONDecodeError:
            print(f"Warning: Failed to decode JSON from LLM for categorization: {json_string}")
            return ["Other"] * len(description_texts) # Fallback
    else:
        print(f"Warning: No JSON array found in LLM output for categorization: {cleaned_output}")
        return ["Other"] * len(description_texts) # Fallback


if __name__ == "__main__":
    sample_descriptions = ["Paying to Home rent", "Coffee at cafe", "Fuel for car"] # This is already a list
    print("Calling get_category_from_ollama...")
    # Call get_category_from_ollama once with the entire list for batch processing
    category_list = get_category_from_ollama(sample_descriptions)
    print(category_list)