from docx import Document
from docx.oxml.text.paragraph import CT_P
from docx.oxml.table import CT_Tbl
from docx.table import _Cell, Table
from docx.text.paragraph import Paragraph
import re

docx_path = 'ethicsinnovation/Speakers.docx'
doc = Document(docx_path)

print("Extracting speaker names and website links:\n")

for para in doc.paragraphs:
    text = para.text.strip()
    if not text or text == "Speakers":
        continue
    
    # Check for hyperlinks in the paragraph
    hyperlinks = []
    for run in para.runs:
        # Check if the run has a hyperlink
        if run._element.rPr is not None:
            # Look for hyperlink relationships
            parent = run._element.getparent()
            if parent.tag.endswith('hyperlink'):
                # Get the link
                rId = parent.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
                if rId:
                    rel = doc.part.rels[rId]
                    hyperlinks.append(rel.target_ref)
    
    # Alternative method: check if paragraph contains hyperlinks
    for element in para._element.iterchildren():
        if element.tag.endswith('hyperlink'):
            rId = element.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
            if rId:
                rel = doc.part.rels[rId]
                hyperlinks.append(rel.target_ref)
    
    if text and (', ' in text):
        print(f"Name: {text}")
        if hyperlinks:
            print(f"Link: {hyperlinks[0]}")
        else:
            print("Link: No hyperlink found")
        print()
