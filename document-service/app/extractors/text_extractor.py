from pypdf import PdfReader
from docx import Document

def extract_text(file_path: str) -> str:
    if file_path.lower().endswith(".pdf"):
        reader = PdfReader(file_path)
        text =""

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"
        return text
    elif file_path.lower().endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    elif file_path.lower().endswith(".docx"):
        document = Document(file_path)


        text = ""

        for paraggraph in document.paragraphs:
            text += paraggraph.text + "\n"
        return text
    else: 
        raise ValueError("Unsopperted file type")
    
                    

