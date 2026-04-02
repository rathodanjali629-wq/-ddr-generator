import pdfplumber
import fitz
import os

def extract_text(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def extract_images(pdf_path, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    doc = fitz.open(pdf_path)
    image_paths = []
    for page_num in range(len(doc)):
        for img_index, img in enumerate(doc.get_page_images(page_num)):
            xref = img[0]
            base_image = doc.extract_image(xref)
            img_path = output_folder + "/img_" + str(page_num) + "_" + str(img_index) + ".png"
            with open(img_path, "wb") as img_file:
                img_file.write(base_image["image"])
            image_paths.append(img_path)
    return image_paths
