# Menu.py
from typing import TYPE_CHECKING, List, Tuple

if TYPE_CHECKING:
    from Stock import Stock 

class Menu:
    """representa un menu ofrecido por el restaurante, con su precio, receta 
    y la ruta opcional a una imagen"""

    def __init__(self, nombre: str, precio: float, receta: List[Tuple[str, float]], imagen_path: str = ""):
        self.nombre = nombre.strip().capitalize()
        self.precio = precio
        #La receta se guarda con nombres normalizados
        self.ingredientes_requeridos = [(n.strip().lower(), float(c)) for n, c in receta]
        #atributo necesario para la GUI 
        self.imagen_path = imagen_path
        #atributo que la GUI espera para saber si se puede o no presionar el boton
        self.disponible = True 

    def puede_prepararse(self, stock_obj: 'Stock') -> bool:
        """verifica si el menu puede prepararse con el stock actual"""
        self.disponible = self.disponible_stock(stock_obj, 1)
        return self.disponible
    
    def disponible_stock(self, stock_obj: 'Stock', cantidad: int = 1) -> bool:
        """verifica si hay suficiente stock para preparar una "cantidad" de este menu"""
        # calcular los requerimientos totales:
        receta_total = [
            (nombre, cantidad_por_menu * cantidad) 
            for nombre, cantidad_por_menu in self.ingredientes_requeridos
        ]
        
        # llamar al metodo de verificación del Stock con el total requerido
        return stock_obj.verificar_stock(receta_total)

    def consumir_ingredientes(self, stock_obj: 'Stock', cantidad: int = 1) -> bool:
        """descuenta los ingredientes del stock para una 'cantidad' de este menu"""
        # calcular los requerimientos totales:
        receta_total = [
            (nombre, cantidad_por_menu * cantidad) 
            for nombre, cantidad_por_menu in self.ingredientes_requeridos
        ]

        try:
            stock_obj.descontar_stock(receta_total)
            return True
        except ValueError:
            return False

# funcion para generar los menus
def generar_menus() -> List[Menu]:
    """genera la lista de menus predefinidos"""
    menus = [
        Menu("Papas fritas", 500, [("papas", 5)], imagen_path="assets/papas.png"),
        Menu("Pepsi", 1100, [("pepsi", 1)], imagen_path="assets/pepsi.png"),
        Menu("Completo", 1800, [
            ("vienesa", 1), 
            ("pan de completo", 1), 
            ("tomate", 1), 
            ("palta", 1)
        ], imagen_path="assets/completo.png"),
        Menu("Hamburguesa", 3500, [
            ("pan de hamburguesa", 1), 
            ("lámina de queso", 1), 
            ("churrasco de carne", 1)
        ], imagen_path="assets/hamburguesa.png"),
        Menu("Panqueques", 2000, [
            ("panqueques", 2), 
            ("manjar", 1), 
            ("azúcar flor", 1)
        ], imagen_path="assets/panqueques.png"),
        Menu("Pollo frito", 2800, [
            ("presa de pollo", 1), 
            ("porción de harina", 1), 
            ("porción de aceite", 1)
        ], imagen_path="assets/pollo.png"),
        Menu("Ensalada mixta", 1500, [
            ("lechuga", 1), 
            ("tomate", 1), 
            ("zanahoria rallada", 1)
        ], imagen_path="assets/ensalada.png"),
    ]
    return menus
