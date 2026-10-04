from app.extractors.text_extractor import extract_text

file_path = "test.docx"

text = extract_text(file_path)

print("----- EXTRACTED TEXT -----")
print(text)