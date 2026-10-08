import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.units import inch
from reportlab.lib import colors
import uuid

OUTPUT_DIR = "output"

def setup_output_dir():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

def generate_certificate(name: str, course_name: str) -> str:
    """
    Generates a PDF certificate and returns the file path.
    """
    setup_output_dir()
    
    filename = f"cert_{uuid.uuid4().hex}.pdf"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    # Create the PDF object, using landscape A4 size
    c = canvas.Canvas(filepath, pagesize=landscape(A4))
    width, height = landscape(A4)
    
    # Draw a border
    c.setStrokeColor(colors.darkblue)
    c.setLineWidth(5)
    c.rect(0.5*inch, 0.5*inch, width - 1*inch, height - 1*inch)
    
    # Inner border
    c.setStrokeColor(colors.gold)
    c.setLineWidth(2)
    c.rect(0.6*inch, 0.6*inch, width - 1.2*inch, height - 1.2*inch)
    
    # Title
    c.setFont("Helvetica-Bold", 40)
    c.setFillColor(colors.darkblue)
    c.drawCentredString(width / 2.0, height - 2*inch, "Certificate of Completion")
    
    # Subtitle
    c.setFont("Helvetica", 20)
    c.setFillColor(colors.black)
    c.drawCentredString(width / 2.0, height - 3.5*inch, "This is to certify that")
    
    # Name
    c.setFont("Helvetica-Bold", 35)
    c.setFillColor(colors.darkred)
    c.drawCentredString(width / 2.0, height - 4.5*inch, name)
    
    # Course
    c.setFont("Helvetica", 20)
    c.setFillColor(colors.black)
    c.drawCentredString(width / 2.0, height - 5.5*inch, "has successfully completed the course:")
    
    c.setFont("Helvetica-Oblique", 25)
    c.setFillColor(colors.darkblue)
    c.drawCentredString(width / 2.0, height - 6.5*inch, course_name)
    
    # Date
    c.setFont("Helvetica", 14)
    c.setFillColor(colors.black)
    from datetime import date
    today = date.today().strftime("%B %d, %Y")
    c.drawCentredString(width / 2.0, 1.5*inch, f"Date: {today}")
    
    # Save the PDF
    c.showPage()
    c.save()
    
    return filepath
