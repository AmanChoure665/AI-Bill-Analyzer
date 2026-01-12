from prompt1 import data_conversion
import subprocess
import re
import json



def get_json_from_prompt(raw_invoice_text: str) -> dict:
    prompt = data_conversion(raw_invoice_text)

     # 2. Execute Ollama subprocess
    process = subprocess.Popen(
        ["ollama", "run", "glm-4.6:cloud"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding='utf-8'
    )

    output, error = process.communicate(input=prompt)

    if process.returncode != 0:
        raise RuntimeError(f"Ollama failed: {error}")
    
    # --- Debugging: Print raw LLM output ---
    print(f"\n--- Raw Ollama Output ---\n{output}\n-------------------------\n")

    # 3. Clean the LLM output
    cleaned_output = output.strip()

    # 3. Extract the LAST JSON object (actual model output, not schema)
    json_blocks = re.findall(r"\{[\s\S]*?\}", cleaned_output)

    if not json_blocks:
        raise RuntimeError("No JSON object found in Ollama output")

    json_string = json_blocks[-1]  # take LAST JSON block only


    
    # match = re.search(r"```json\n?(.*?)\n?```", cleaned_output, re.DOTALL)
    # if match:
    #     json_string = match.group(1).strip()
    # else:
    #     json_string = cleaned_output.replace("```", "").strip()
    


    # --- Debugging: Print extracted JSON string ---
    print(f"\n--- Extracted JSON String ---\n{json_string}\n-----------------------------\n")

    # 4. converting json string back into dictionary 
    try:
        if not json_string:
            raise ValueError("Extracted JSON string is empty.")
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse JSON from Ollama output: {e}\nProblematic string: '{json_string}'") from e
    except ValueError as e:
        raise RuntimeError(f"Error in JSON extraction: {e}") from e

if __name__ == "__main__":
    SAMPLE_INVOICE_TEXT = """
    Invoice No.: 98765
    Issue Date: 12/25/2025++
    Description: Product shipment, Consulting Fee
    Amount: 500.00, 150.00
    Grand Total: $650.00
    """
    result_dict = get_json_from_prompt(SAMPLE_INVOICE_TEXT)
    print(result_dict)
