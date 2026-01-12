import cv2
import os
import numpy as np


input_folder = "bill_image"
output_folder = "image_cleaning_one_folder"


def image_cleaning(input_folder, output_folder):
    valid_extansion = (".jpg", ".jpeg", ".png")
    converted_count = 0
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(valid_extansion):
            input_path = os.path.join(input_folder,filename)
            output_path = os.path.join(output_folder,filename)
            try:
                color_image = cv2.imread(input_path)
                #converting it into grayscale/black&white image
                gray_image = cv2.cvtColor(color_image,cv2.COLOR_BGR2GRAY) # type: ignore
                #removing the noice from the image
                blur_image = cv2.GaussianBlur(gray_image,(5,5),0)
                #otsu's binarization of image 
                ret, binary_image = cv2.threshold(blur_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
                cv2.imwrite(output_path,binary_image)
                # cv2.imwrite(output_path,blur_image)
                converted_count += 1
                print(f"image converted = {converted_count} as {filename}")
            except Exception as err:
                print(f"Failed to convert {filename}, {err}")

def clean_single_image_bytes(image_bytes, output_path):
    """
    Cleans a single image from its bytes and saves the processed image.
    Args:
        image_bytes: Bytes of the input image.
        output_path: Path where the cleaned image will be saved.
    Returns:
        True if successful, False otherwise.
    """
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        color_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if color_image is None:
            print(f"Error: Could not decode image from bytes.")
            return False

        gray_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)
        blur_image = cv2.GaussianBlur(gray_image, (5, 5), 0)
        ret, binary_image = cv2.threshold(blur_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        cv2.imwrite(output_path, binary_image)
        return True
    except Exception as err:
        print(f"Failed to clean image from bytes: {err}")
        return False

if __name__ == "__main__":
    image_cleaning(input_folder,output_folder)