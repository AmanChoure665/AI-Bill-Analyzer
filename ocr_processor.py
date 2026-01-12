import pytesseract
import os

# set the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


input_folder = "image_cleaning_one_folder"
output_file = "extracted_text.txt"

def perform_ocr(input_folder,output_file):
    all_extracted_text = ""
    for filename in os.listdir(input_folder):
        if filename.endswith((".jpeg",".jpg",".png")):
            image_path = os.path.join(input_folder,filename)
            try:
                text = pytesseract.image_to_string(image_path)
                print("-"*20)
                print(text.strip())
                print("-"*20)
                all_extracted_text += f"\n--Text from {filename}--\n{text}\n"
            except Exception as err:
                print(f"Error in {filename}, {err}")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(all_extracted_text)
    
    print(f"Complete OCR done")

def perform_ocr_on_image_path(image_path: str) -> str:
    """
    Performs OCR on a single image file and returns the extracted text.
    """
    try:
        text = pytesseract.image_to_string(image_path)
        return text
    except Exception as err:
        print(f"Error performing OCR on {image_path}: {err}")
        return ""

if __name__== "__main__":
    perform_ocr(input_folder,output_file)
