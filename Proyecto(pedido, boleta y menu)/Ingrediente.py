# Ingrediente.py
class Ingrediente:
    def __init__(self, nombre, unidad, cantidad):
        self.nombre = nombre
        self.unidad = unidad
        self.cantidad = float(cantidad)

    def __str__(self):
        return f"{self.nombre} ({self.cantidad} {self.unidad})"