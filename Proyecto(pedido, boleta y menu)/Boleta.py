# Boleta.py
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from datetime import datetime
import os

def generar_boleta_pdf(pedido, filename="boleta.pdf"):
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Boleta de Venta", styles['h1']))
    story.append(Paragraph(f"Fecha: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}", styles['Normal']))
    story.append(Spacer(1, 24))

    data = [['ID', 'Ítem', 'Precio']]
    for item in pedido.get_items():
        data.append([item['id'], item['nombre'], f"${item['precio']:,}".replace(",", ".")])
    
    story.append(Spacer(1, 12))
    
    # Línea para el total
    total = pedido.calcular_total()
    data.append(['', Paragraph('<b>TOTAL</b>', styles['Normal']), Paragraph(f"<b>${total:,}</b>".replace(",", "."), styles['Normal'])])

    table = Table(data, colWidths=[50, 250, 100])
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (-2, -1), (-1, -1), colors.lightgrey),
    ])
    table.setStyle(style)
    story.append(table)
    
    doc.build(story)
    return os.path.abspath(filename)