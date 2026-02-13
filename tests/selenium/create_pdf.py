from reportlab.pdfgen import canvas
import os

def create_dummy_pdf(filename="test_doc.pdf", pages=5):
    c = canvas.Canvas(filename)
    for i in range(pages):
        c.drawString(100, 750, f"Page {i+1}")
        c.drawString(100, 700, "This is a test PDF document for Selenium testing.")
        c.showPage()
    c.save()
    print(f"Created {filename}")

if __name__ == "__main__":
    create_dummy_pdf()
