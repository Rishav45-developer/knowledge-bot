from reportlab.pdfgen import canvas
pdf = canvas.Canvas("test.pdf")

pdf.drawString(100, 750, "KnowledgeBot Document Test")
pdf.drawString(100, 720, "This is a test PDF document.")
pdf.drawString(100, 690, "We are testing PDF text extraction.")
pdf.drawString(100, 660, "The document service should extract this text.")

pdf.save()

print("test.pdf created succesfully")

