import random
import string
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from pathlib import Path

UPLOAD_FOLDER = Path("static/uploads")


def generate_random_string(length=8):
    letters = string.ascii_letters + string.digits
    return "".join(random.choice(letters) for _ in range(length))


def create_pdf_from_string(text):
    name = generate_random_string(8)
    pdf_path = UPLOAD_FOLDER / f"{name}.pdf"

    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    c.setFont("Helvetica", 12)
    lines = text.split("\n")
    y, x, line_height = 750, 100, 15
    max_width = 400

    for line in lines:
        words, line_to_draw = line.split(), ""
        for word in words:
            if c.stringWidth(line_to_draw + " " + word) < max_width:
                line_to_draw += " " + word if line_to_draw else word
            else:
                c.drawString(x, y, line_to_draw)
                y -= line_height
                line_to_draw = word
        if line_to_draw:
            c.drawString(x, y, line_to_draw)
            y -= line_height

    c.save()
    return str(pdf_path)
