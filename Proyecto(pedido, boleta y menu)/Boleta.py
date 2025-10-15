# Boleta.py
from fpdf import FPDF
from datetime import datetime
import os
from collections import Counter

class BoletaPDF:
    def __init__(self, pedido):
        if not pedido or not pedido.get_items():
            raise ValueError("El objeto Pedido no puede estar vacío.")
        self.pedido = pedido
        self.pdf = FPDF(orientation='P', unit='mm', format='A4')

    def _agrupar_items(self):
        """Agrupa los items del pedido por nombre y calcula cantidades y totales."""
        nombres_items = [item['nombre'] for item in self.pedido.get_items()]
        conteo_items = Counter(nombres_items)
        
        items_agrupados = {}
        for item in self.pedido.get_items():
            nombre = item['nombre']
            if nombre not in items_agrupados:
                cantidad = conteo_items[nombre]
                precio_unit = item['precio']
                items_agrupados[nombre] = {
                    'cantidad': cantidad,
                    'precio_unit': precio_unit,
                    'total': cantidad * precio_unit
                }
        return list(items_agrupados.items())

    def generar(self, filename="boleta.pdf"):
        self.pdf.add_page()
        
        # --- ENCABEZADO PROFESIONAL ---
        # Logo (opcional, si existe un 'logo.png' en la carpeta)
        if os.path.exists("logo.png"):
            self.pdf.image("logo.png", x=10, y=8, w=33)
        
        self.pdf.set_font('Arial', 'B', 20)
        self.pdf.cell(80) # Mover a la derecha del logo
        self.pdf.cell(30, 10, 'RESTAURANTE', 0, 1, 'C')

        self.pdf.set_font('Arial', '', 10)
        self.pdf.cell(80)
        self.pdf.cell(30, 5, 'RUT: 76.123.456-7', 0, 1, 'C')
        self.pdf.cell(80)
        self.pdf.cell(30, 5, 'Av. Siempre Viva 742, Temuco', 0, 1, 'C')
        self.pdf.cell(80)
        self.pdf.cell(30, 5, 'Fono: +56 9 1234 5678', 0, 1, 'C')
        self.pdf.ln(10)

        # --- DETALLES DE LA BOLETA ---
        self.pdf.set_font('Arial', 'B', 14)
        self.pdf.cell(0, 10, 'BOLETA ELECTRONICA', 'B', 1, 'C')
        self.pdf.ln(5)

        now = datetime.now()
        self.pdf.set_font('Arial', '', 12)
        self.pdf.cell(0, 6, f"Fecha de Emision: {now.strftime('%d-%m-%Y')}", 0, 1, 'L')
        self.pdf.cell(0, 6, f"Hora: {now.strftime('%H:%M:%S')}", 0, 1, 'L')
        self.pdf.ln(5)
        
        # --- TABLA DE PRODUCTOS ---
        self.pdf.set_font('Arial', 'B', 12)
        self.pdf.set_fill_color(230, 230, 230) # Gris claro para encabezado
        self.pdf.cell(20, 10, 'Cant.', 1, 0, 'C', 1)
        self.pdf.cell(90, 10, 'Detalle', 1, 0, 'C', 1)
        self.pdf.cell(40, 10, 'P. Unit.', 1, 0, 'C', 1)
        self.pdf.cell(40, 10, 'Total', 1, 1, 'C', 1)

        self.pdf.set_font('Arial', '', 12)
        items_para_boleta = self._agrupar_items()
        fill = False
        for nombre, detalles in items_para_boleta:
            self.pdf.set_fill_color(245, 245, 245) if fill else self.pdf.set_fill_color(255, 255, 255)
            self.pdf.cell(20, 10, str(detalles['cantidad']), 1, 0, 'C', 1)
            self.pdf.cell(90, 10, nombre, 1, 0, 'L', 1)
            self.pdf.cell(40, 10, f"${detalles['precio_unit']:,}".replace(",", "."), 1, 0, 'R', 1)
            self.pdf.cell(40, 10, f"${detalles['total']:,}".replace(",", "."), 1, 1, 'R', 1)
            fill = not fill

        # --- CÁLCULO Y VISUALIZACIÓN DE TOTALES ---
        total_final = self.pedido.calcular_total()
        # En Chile, el precio al consumidor incluye IVA. Para obtener el neto (subtotal), se divide por 1.19
        subtotal = int(round(total_final / 1.19))
        iva = total_final - subtotal
        
        self.pdf.ln(10)
        
        # Posicionar el cursor para alinear los totales a la derecha
        self.pdf.set_x(110)
        self.pdf.set_font('Arial', '', 12)
        self.pdf.cell(50, 8, 'SUBTOTAL:', 0, 0, 'R')
        self.pdf.cell(40, 8, f"${subtotal:,}".replace(",", "."), 0, 1, 'R')
        
        self.pdf.set_x(110)
        self.pdf.cell(50, 8, 'IVA (19%):', 0, 0, 'R')
        self.pdf.cell(40, 8, f"${iva:,}".replace(",", "."), 0, 1, 'R')
        
        self.pdf.set_x(110)
        self.pdf.set_font('Arial', 'B', 16)
        self.pdf.cell(50, 10, 'TOTAL:', 0, 0, 'R')
        self.pdf.cell(40, 10, f"${total_final:,}".replace(",", "."), 0, 1, 'R')
        
        self.pdf.ln(10)

        # --- PIE DE PÁGINA ---
        self.pdf.set_font('Arial', 'I', 10)
        self.pdf.cell(0, 10, 'Gracias por su preferencia', 'T', 1, 'C')

        # Guardar el archivo
        self.pdf.output(filename)
        return os.path.abspath(filename)