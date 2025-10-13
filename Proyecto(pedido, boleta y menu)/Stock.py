from typing import List, Tuple, Dict
from Ingrediente import Ingrediente 

class Stock:
    """gestiona el inventario de ingredientes del restaurante"""

    def __init__(self): 
        self.inventario: Dict[str, Ingrediente] = {} 

    def agregar_ingrediente(self, nombre: str, unidad: str, cantidad: float):
        """añade o suma cantidad a un ingrediente existente, lanza ValueError si la unidad es inconsistente"""
        ingrediente_clave = nombre.strip().lower()
        
        if cantidad <= 0:
            raise ValueError("La cantidad a agregar debe ser un número positivo.")

        if ingrediente_clave in self.inventario:
            ingrediente = self.inventario[ingrediente_clave]

            #1 verificar unidad
            if ingrediente.unidad != unidad.strip().lower():
                raise ValueError(f"Unidad de medida inconsistente para '{nombre}'. Se esperaba '{ingrediente.unidad}'.")
            
            #2 sumar cantidad
            ingrediente.sumar_cantidad(cantidad) 
            
        else:
            #crea un nuevo ingrediente si no existe
            self.inventario[ingrediente_clave] = Ingrediente(nombre, unidad, cantidad)

    def eliminar_ingrediente(self, nombre: str) -> bool:
        """Elimina un ingrediente del inventario por su nombre"""
        ingrediente_clave = nombre.strip().lower()
        if ingrediente_clave in self.inventario:
            del self.inventario[ingrediente_clave]
            return True
        return False
        
    def cargar_lista_csv(self, datos_csv: List[List[str]]):
        """carga y actualiza el stock desde una lista de datos CSV"""
        for nombre, unidad, cantidad_str in datos_csv:
            try:
                #se asume que los datos vienen limpios de la lectura del CSV
                cantidad = float(cantidad_str) 
                self.agregar_ingrediente(nombre, unidad, cantidad)
            except ValueError as e:
                #maneja errores de conversión de cantidad o unidad inconsistente
                print(f"Advertencia al cargar CSV ({nombre}): {e}")


    def verificar_stock(self, receta: List[Tuple[str, float]]) -> bool:
        """
        verifica si hay suficiente stock para preparar una receta, receta: [(ingrediente_requerido, cantidad_requerida), ...]
        """
        for ingrediente_requerido, cantidad_requerida in receta:
            ingrediente_clave = ingrediente_requerido.strip().lower()

            if ingrediente_clave not in self.inventario:
                return False 
            
            ingrediente = self.inventario[ingrediente_clave]

            if ingrediente.cantidad < cantidad_requerida:
                return False 
                
        return True 


    def descontar_stock(self, receta: List[Tuple[str, float]]) -> bool:
        """
        descuenta el stock según una receta, lanza ValueError si el stock es insuficiente
        """
        if not self.verificar_stock(receta):
            raise ValueError("Stock insuficiente para completar el pedido, descuento cancelado")

        for ingrediente_requerido, cantidad_requerida in receta:
            ingrediente_clave = ingrediente_requerido.strip().lower()
            ingrediente = self.inventario[ingrediente_clave]
            ingrediente.cantidad -= cantidad_requerida
            
            if ingrediente.cantidad <= 0:
                del self.inventario[ingrediente_clave]
                
        return True


