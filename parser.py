import os
import json
import re
from ollama1 import get_json_from_prompt
from ollama2 import get_category_from_ollama

ocr_output_file = "extracted_text.txt"


def parse_multiple_invoices():
    print(f"Parsing started...")

    if not os.path.exists(ocr_output_file):
        print(f"OCR file not found at {ocr_output_file}")
        return []
    
    with open(ocr_output_file, 'r', encoding='utf-8') as f:
        master_text = f.read()


     # Split using the marker you chose
    bill_section = re.split(r"--\s*Text\s+from\s+", master_text)[1:]
    total_bills = len(bill_section)
    print(f"Total bills to process: {total_bills}")

    all_structured_list = []


    for section in bill_section:
        try:
            # Splitting filename and content
            section = section.strip()
            parts = section.split("--", 1)
            filename = parts[0].strip()
            bill_text = parts[1].strip() if len(parts) > 1 else ""
            print(f" Processing: {filename}")

            # Agent 1: Extraction
            structured_data_dict = get_json_from_prompt(bill_text)


            # dscription{expense1, expense2, expense3}, amount{amount1, amount2, amount3}

            #breaking multiple descriptions into single line item id
            if structured_data_dict:
                # Note: 'description' and 'ammount' are from prompt1.py schema (lowercase)
                description_list = structured_data_dict.get('description', [])
                amount_list = structured_data_dict.get('ammount', [])
                enriched_line_items = []

                # Agent 2: Batch Categorization
                if description_list and isinstance(description_list, list):
                    print(f"   > Batch Categorizing {len(description_list)} items for {filename}...")
                    category_labels = get_category_from_ollama([str(d).strip() for d in description_list])
                    
                    # Ensure category_labels matches the length of description_list
                    if len(category_labels) != len(description_list):
                        print(f"Warning: Category labels count mismatch for {filename}. Expected {len(description_list)}, got {len(category_labels)}. Filling with 'Other'.")
                        category_labels = ["Other"] * len(description_list)
                else:
                    category_labels = ["Other"] * len(description_list) # If no descriptions, no categories

                # Combine descriptions, amounts, and categories
                # Ensure description_list and amount_list are iterable and of same length
                if isinstance(description_list, list) and isinstance(amount_list, list) and len(description_list) == len(amount_list):
                    for i, (desc_item_raw, amt) in enumerate(zip(description_list, amount_list)):
                        enriched_item = {
                            'service_description': str(desc_item_raw).strip(),
                            'Amount': amt,
                            'Category': category_labels[i] if i < len(category_labels) else 'Other'
                        }
                        enriched_line_items.append(enriched_item)
                else:
                    print(f"Warning: Description or Amount lists are not valid for {filename}. Skipping categorization.")
                    # Fallback if lists are not valid, try to use what's available
                    if description_list and amount_list:
                        enriched_line_items = [{'service_description': d, 'Amount': a, 'Category': category_labels[i] if i < len(category_labels) else 'Other'} for i, (d, a) in enumerate(zip(description_list, amount_list))]
                    elif description_list:
                        enriched_line_items = [{'service_description': d, 'Amount': None, 'Category': category_labels[i] if i < len(category_labels) else 'Other'} for i, d in enumerate(description_list)]
                    elif amount_list:
                         enriched_line_items = [{'service_description': 'Unknown', 'Amount': a, 'Category': 'Other'} for a in amount_list]


                # Prepare final structured data, mapping LLM output keys to DB schema keys
                final_structured_data = {
                    "Invoice_No": structured_data_dict.get("invoice_no"),
                    "Issue_Date": structured_data_dict.get("issue_date"),
                    "billed_to": structured_data_dict.get("billed_to"),
                    "billed_by": structured_data_dict.get("billed_by"),
                    "Grand_Total": structured_data_dict.get("grand_total"),
                    "source_file": filename, # Use the passed filename
                    "line_items": enriched_line_items # Store line items separately for easier processing
                }
                all_structured_list.append(final_structured_data)
            else:
                print(f"Failed to extract data for {filename}")

        except Exception as e:
            print(f" Error processing section for {filename}: {e}")

    return all_structured_list

def parse_single_invoice_text(raw_invoice_text: str, source_filename: str) -> dict:
    """
    Parses a single raw invoice text (OCR output) and returns structured data.
    """
    try:
        # Agent 1: Extraction
        structured_data_dict = get_json_from_prompt(raw_invoice_text)

        if structured_data_dict:
            # Note: 'description' and 'ammount' are from prompt1.py schema (lowercase)
            description_list = structured_data_dict.get('description', [])
            amount_list = structured_data_dict.get('ammount', [])
            enriched_line_items = []

            # Agent 2: Categorization
            # Ensure description_list and amount_list are iterable and of same length
            if isinstance(description_list, list) and isinstance(amount_list, list) and len(description_list) == len(amount_list):
                print(f"   > Batch Categorizing {len(description_list)} items for {source_filename}...")
                service_descriptions_for_llm = [str(d).strip() for d in description_list]
                category_labels = get_category_from_ollama(service_descriptions_for_llm)

                # Ensure category_labels matches the length of description_list
                if len(category_labels) != len(description_list):
                    print(f"Warning: Category labels count mismatch for {source_filename}. Expected {len(description_list)}, got {len(category_labels)}. Filling with 'Other'.")
                    category_labels = ["Other"] * len(description_list)

                for i, (desc_item_raw, amt) in enumerate(zip(description_list, amount_list)):
                    enriched_item = {
                        'service_description': str(desc_item_raw).strip(),
                        'Amount': amt,
                        'Category': category_labels[i] if i < len(category_labels) else 'Other'
                    }
                    enriched_line_items.append(enriched_item)
            else:
                print(f"Warning: Description or Amount lists are not valid for {source_filename}. Skipping categorization.")
                # Fallback if lists are not valid, try to use what's available
                if description_list and amount_list:
                    enriched_line_items = [{'service_description': d, 'Amount': a, 'Category': 'Other'} for d, a in zip(description_list, amount_list)]
                elif description_list:
                    enriched_line_items = [{'service_description': d, 'Amount': None, 'Category': 'Other'} for d in description_list]
                elif amount_list:
                     enriched_line_items = [{'service_description': 'Unknown', 'Amount': a, 'Category': 'Other'} for a in amount_list]


            # Prepare final structured data, mapping LLM output keys to DB schema keys
            final_structured_data = {
                "Invoice_No": structured_data_dict.get("invoice_no"),
                "Issue_Date": structured_data_dict.get("issue_date"),
                "billed_to": structured_data_dict.get("billed_to"),
                "billed_by": structured_data_dict.get("billed_by"),
                "Grand_Total": structured_data_dict.get("grand_total"),
                "source_file": source_filename, # Use the passed filename
                "line_items": enriched_line_items # Store line items separately for easier processing
            }
            return final_structured_data
        else:
            print(f"Failed to extract data for {source_filename}")
            return {}

    except Exception as e:
        print(f" Error processing single invoice text for {source_filename}: {e}")
        return {}

    return all_structured_list


if __name__ == "__main__":
    final_extracted_data = parse_multiple_invoices()
    print(" Final List of Bills Generated!")
    # Use json.dumps for pretty printing the final result
    print(json.dumps(final_extracted_data, indent=4))
