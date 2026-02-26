from docx import Document
import os

docx_path = 'ethicsinnovation/Speakers.docx'
doc = Document(docx_path)

print("Document content with paragraphs and images:\n")
image_counter = 0

for i, para in enumerate(doc.paragraphs):
    # Check if paragraph contains an image
    if 'graphicData' in para._element.xml or 'blip' in para._element.xml:
        image_counter += 1
        print(f"\n[IMAGE {image_counter} HERE]\n")
    
    if para.text.strip():
        print(f"{para.text.strip()}")
