from prompt3 import user_query
import subprocess
import re

def response_to_user_query(user_input:str) -> str:
    prompt = user_query(user_input)
    process = subprocess.Popen(
        ["ollama", "run", "glm-4.6:cloud"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding='utf-8'
    )
    
    output, error = process.communicate(input=prompt)
    
    #cleaning the output from llm  (ollama)

    if process.returncode != 0:
        raise RuntimeError(f"Ollama failed: {error}")

    cleaned_output = output.strip()

    # Attempt to extract content from the last SQL markdown block
    # This regex looks for ```sql or ```sqlite followed by content, then ```
    sql_blocks = re.findall(r"```(?:sql|sqlite)?\n(.*?)\n```", cleaned_output, re.DOTALL)
    if sql_blocks:
        # Take the last found SQL block, as the LLM might put explanations before it
        extracted_query = sql_blocks[-1].strip()
    else:
        # If no markdown block, try to find a line that starts with SELECT or PRAGMA
        # This handles cases where the LLM doesn't wrap the SQL in markdown
        lines = cleaned_output.split('\n')
        potential_queries = [line.strip() for line in lines if line.strip().upper().startswith(('SELECT', 'PRAGMA'))]
        if potential_queries:
            # Take the last one, assuming it's the final query
            extracted_query = potential_queries[-1]
        else:
            # Fallback: if no clear SQL is found, return the whole cleaned output
            # This might still lead to errors if the LLM is completely off-topic
            extracted_query = cleaned_output

    # Ensure the query ends with a semicolon if it's a SELECT/PRAGMA and doesn't already
    if extracted_query.upper().startswith(('SELECT', 'PRAGMA')) and not extracted_query.endswith(';'):
        extracted_query += ';'

    return extracted_query
