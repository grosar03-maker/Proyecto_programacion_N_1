# Pedido.py
class Pedido:
    def __init__(self):
        self.items = []
        self._next_id = 1

    def agregar_item(self, item_info, nombre_item):
        item_con_id = {
            'id': self._next_id,
            'nombre': nombre_item,
            'precio': item_info['precio'],
            'ingredientes': item_info['ingredientes']
        }
        self.items.append(item_con_id)
        self._next_id += 1
        return item_con_id

    def eliminar_item(self, item_id):
        item_a_eliminar = None
        for item in self.items:
            if item['id'] == item_id:
                item_a_eliminar = item
                break
        if item_a_eliminar:
            self.items.remove(item_a_eliminar)
            return item_a_eliminar
        return None

    def get_items(self):
        return self.items

    def calcular_total(self):
        return sum(item['precio'] for item in self.items)
    
    def limpiar(self):
        self.items.clear()