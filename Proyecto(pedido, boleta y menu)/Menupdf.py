# Menupdf.py
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import os

def generar_menu_pdf(menu_items, filename="carta_restaurante.pdf"):
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Menú del Restaurante", styles['h1']))
    story.append(Spacer(1, 24))

    data = [['Plato / Bebida', 'Precio']]
    for item in menu_items:
        data.append([item["nombre"], item["precio"]])

    table = Table(data, colWidths=[300, 100])
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.royalblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
    table.setStyle(style)
    story.append(table)
    doc.build(story)
    return os.path.abspath(filename)