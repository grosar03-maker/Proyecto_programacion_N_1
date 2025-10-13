from typing import Dict, Any

class Ingrediente:
    """representa un unico ingrediente en el inventario, con su cantidad
    y unidad de medida"""
    def __init__(self, nombre: str, unidad: str, cantidad: float):
        # dejamos en minusculas para comparaciones consistentes
        self.nombre = nombre.strip().lower() 
        self.unidad = unidad.strip().lower()
        self.cantidad = cantidad

    def sumar_cantidad(self, cantidad_a_sumar: float):
        """suma una cantidad al stock existente"""
        if cantidad_a_sumar < 0:
            raise ValueError("La cantidad a sumar debe ser positiva.")
        self.cantidad += cantidad_a_sumar
        
    def __str__(self) -> str:
        # muestra el nombre con la primera letra en mayuscula
        return f"{self.nombre.capitalize()} ({self.cantidad} {self.unidad})"

    def to_dict(self) -> Dict[str, Any]:
        """retorna un diccionario para facilitar la visualizacion en la GUI"""
        return {
            "nombre": self.nombre.capitalize(),
            "unidad": self.unidad,
            "cantidad": self.cantidad
        }

