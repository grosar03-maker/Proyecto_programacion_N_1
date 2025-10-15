# Stock.py
class Stock:
    def __init__(self):
        self.ingredientes = {}

    def agregar_ingrediente(self, ingrediente):
        nombre = ingrediente.nombre.lower()
        if nombre in self.ingredientes:
            self.ingredientes[nombre].cantidad += ingrediente.cantidad
        else:
            self.ingredientes[nombre] = ingrediente

    def eliminar_ingrediente(self, nombre):
        if nombre.lower() in self.ingredientes:
            del self.ingredientes[nombre.lower()]

    def get_ingredientes(self):
        return list(self.ingredientes.values())

    def verificar_stock_para_item(self, ingredientes_requeridos):
        for ing, cant_req in ingredientes_requeridos.items():
            ing_nombre = ing.lower()
            if ing_nombre not in self.ingredientes or self.ingredientes[ing_nombre].cantidad < cant_req:
                return False
        return True

    def descontar_ingredientes(self, ingredientes_requeridos):
        for ing, cant_req in ingredientes_requeridos.items():
            self.ingredientes[ing.lower()].cantidad -= cant_req

    def reponer_ingredientes(self, ingredientes_devueltos):
        for ing, cant_dev in ingredientes_devueltos.items():
            self.ingredientes[ing.lower()].cantidad += cant_dev