# Menupdf.py
from fpdf import FPDF
import os

class MenuPDF:
    def __init__(self, menu_items):
        self.menu_items = menu_items
        self.pdf = FPDF()

    def generar(self, filename="carta_restaurante.pdf"):
        try:
            self.pdf.add_page()
            
            # Título
            self.pdf.set_font('Arial', 'B', 24)
            self.pdf.cell(0, 15, 'Menu del Restaurante', 0, 1, 'C')
            self.pdf.ln(10)

            # Encabezados de la tabla
            self.pdf.set_font('Arial', 'B', 12)
            self.pdf.set_fill_color(70, 130, 180)
            self.pdf.set_text_color(255, 255, 255)
            self.pdf.cell(140, 10, 'Plato / Bebida', 1, 0, 'C', 1)
            self.pdf.cell(50, 10, 'Precio', 1, 1, 'C', 1)

            # Contenido de la tabla
            self.pdf.set_font('Arial', '', 12)
            self.pdf.set_text_color(0, 0, 0)
            
            for item in self.menu_items:
                # Se asegura de que el texto sea compatible
                nombre_compatible = item["nombre"].encode('latin-1', 'replace').decode('latin-1')
                precio_compatible = item["precio"].encode('latin-1', 'replace').decode('latin-1')
                
                self.pdf.cell(140, 10, nombre_compatible, 1, 0, 'L')
                self.pdf.cell(50, 10, precio_compatible, 1, 1, 'R')

            # Guardar el archivo PDF
            self.pdf.output(filename)
            
            # Devolver la ruta completa si todo fue exitoso
            return os.path.abspath(filename)
        
        except Exception as e:
            print(f"ERROR CRÍTICO en Menupdf.py al generar el PDF: {e}")
            return None # Devuelve None si hubo algún error