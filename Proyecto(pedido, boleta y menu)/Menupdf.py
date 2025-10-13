from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
import datetime
from typing import List

def generar_carta_pdf(menus: List, stock, ruta_salida: str, titulo: str = "Carta del Restaurante") -> None:
    """
    Genera un PDF con los menus que están disponibles según el stock.
    menus: lista de objetos Menu (debe tener: nombre, precio, ingredientes_req, disponible_en_stock)
    stock: objeto Stock usado para filtrar disponibilidad
    ruta_salida: ruta a archivo .pdf
    """
    doc = SimpleDocTemplate(ruta_salida, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    estilo_titulo = ParagraphStyle("Titulo", parent=styles["Heading1"], alignment=TA_CENTER, fontSize=18, spaceAfter=8)
    estilo_menu = ParagraphStyle("Menu", parent=styles["Heading2"], fontSize=12, alignment=TA_LEFT, spaceAfter=4)
    estilo_text = ParagraphStyle("Texto", parent=styles["BodyText"], fontSize=10, leading=12)

    elementos = []
    elementos.append(Paragraph(titulo, estilo_titulo))
    fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    elementos.append(Paragraph(f"Generado: {fecha}", styles["Normal"]))
    elementos.append(Spacer(1, 8))

    # Cabecera tabla resumen (opcional)
    tabla_data = [["Nombre", "Precio", "Disponible (porciones)"]]
    tabla_style = TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#dceefc")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.HexColor("#0b3954")),
        ("ALIGN", (1,0), (-1,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,0), 10),
        ("BOTTOMPADDING", (0,0), (-1,0), 6),
        ("GRID", (0,0), (-1,-1), 0.3, colors.grey),
    ])

    for m in menus:
        max_porciones = m.max_porciones_disponibles(stock) if hasattr(m, "max_porciones_disponibles") else ("N/A")
        if m.disponible_en_stock(stock, 1):
            tabla_data.append([m.nombre, f"${m.precio:.0f}", str(max_porciones)])

    if len(tabla_data) > 1:
        tabla = Table(tabla_data, colWidths=[110*mm, 35*mm, 35*mm], hAlign="LEFT")
        tabla.setStyle(tabla_style)
        elementos.append(tabla)
        elementos.append(Spacer(1, 10))

    # Detalle por menú (ingredientes)
    for m in menus:
        if not m.disponible_en_stock(stock, 1):
            continue
        elementos.append(Paragraph(f"{m.nombre} — ${m.precio:.0f}", estilo_menu))
        # ingredientes como lista
        ing_lines = []
        for ing, cant in m.ingredientes_req.items():
            ing_lines.append(f"- {ing}: {cant}")
        if ing_lines:
            for ln in ing_lines:
                elementos.append(Paragraph(ln, estilo_text))
        elementos.append(Spacer(1, 6))

    # Pie
    elementos.append(Spacer(1, 12))
    elementos.append(Paragraph("Nota: Los precios pueden cambiar. Consulte disponibilidad en cocina.", styles["Italic"]))

    doc.build(elementos)
