# Boleta.py
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
import datetime
from typing import Optional
import locale

try:
    locale.setlocale(locale.LC_ALL, "")
except Exception:
    # Algunos entornos no admiten locales; no crítico
    pass


class Boleta:
    """
    Genera una boleta (PDF) a partir de un objeto Pedido.
    Uso:
        b = Boleta(pedido)
        b.generar_pdf("salida.pdf", aplicar_iva=False, iva_pct=0.19)
    """
    def __init__(self, pedido):
        self.pedido = pedido

    def generar_pdf(self, ruta_salida: str, aplicar_iva: bool = False, iva_pct: float = 0.19, empresa_info: Optional[dict] = None) -> None:
        empresa_info = empresa_info or {"nombre": "Restaurante Demo", "direccion": "", "telefono": ""}
        doc = SimpleDocTemplate(ruta_salida, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=20*mm, bottomMargin=20*mm)
        styles = getSampleStyleSheet()
        estilo_titulo = ParagraphStyle("Titulo", parent=styles["Heading1"], alignment=TA_CENTER, fontSize=16)
        estilo_normal = styles["Normal"]
        estilo_r = ParagraphStyle("Derecha", parent=styles["Normal"], alignment=TA_RIGHT)
        estilo_small = ParagraphStyle("Small", parent=styles["BodyText"], fontSize=9)

        elementos = []
        # Encabezado: empresa + fecha + id pedido
        elementos.append(Paragraph(empresa_info.get("nombre", ""), estilo_titulo))
        elementos.append(Spacer(1, 4))
        elementos.append(Paragraph(f"Dirección: {empresa_info.get('direccion','')}", estilo_small))
        elementos.append(Paragraph(f"Tel: {empresa_info.get('telefono','')}", estilo_small))
        elementos.append(Spacer(1, 8))

        elementos.append(Paragraph(f"Boleta ID: {self.pedido.pedido_id}", estilo_normal))
        fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        elementos.append(Paragraph(f"Fecha: {fecha}", estilo_normal))
        elementos.append(Paragraph(f"Cliente: {getattr(self.pedido, 'cliente', '')}", estilo_normal))
        elementos.append(Spacer(1, 8))

        # Tabla de items
        data = [["Item", "Cantidad", "Precio unitario", "Subtotal"]]
        for it in self.pedido.items:
            data.append([
                it.menu.nombre,
                str(it.cantidad),
                f"${it.menu.precio:,.0f}",
                f"${it.subtotal():,.0f}"
            ])

        table = Table(data, colWidths=[90*mm, 25*mm, 35*mm, 35*mm])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#f0f4f8")),
            ("TEXTCOLOR", (0,0), (-1,0), colors.HexColor("#0b3954")),
            ("ALIGN", (1,1), (-1,-1), "CENTER"),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("GRID", (0,0), (-1,-1), 0.3, colors.grey),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ]))
        elementos.append(table)
        elementos.append(Spacer(1, 8))

        # Totales
        subtotal = self.pedido.subtotal()
        elementos.append(Paragraph(f"Subtotal: ${subtotal:,.0f}", estilo_r))
        if aplicar_iva:
            iva_val = subtotal * iva_pct
            total = subtotal + iva_val
            elementos.append(Paragraph(f"IVA ({iva_pct*100:.0f}%): ${iva_val:,.0f}", estilo_r))
            elementos.append(Paragraph(f"Total: ${total:,.0f}", estilo_r))
        else:
            elementos.append(Paragraph(f"Total: ${subtotal:,.0f}", estilo_r))

        elementos.append(Spacer(1, 14))
        elementos.append(Paragraph("Gracias por su compra. Presentar esta boleta para cualquier reclamo.", estilo_small))

        doc.build(elementos)
