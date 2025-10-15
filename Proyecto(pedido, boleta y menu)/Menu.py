# Menu.py
class Menu:
    def __init__(self):
        self._items = {
            "Papas fritas": {"precio": 500, "ingredientes": {"papas": 5}},
            "Pepsi": {"precio": 1100, "ingredientes": {"pepsi": 1}},
            "Completo": {"precio": 1800, "ingredientes": {"vienesa": 1, "pan de completo": 1, "tomate": 1, "palta": 1}},
            "Hamburguesa": {"precio": 3500, "ingredientes": {"pan de hamburguesa": 1, "lamina de queso": 1, "churrasco de carne": 1}},
            "Panqueques": {"precio": 2000, "ingredientes": {"panqueques": 2, "manjar": 1, "azucar flor": 1}},
            "Pollo frito": {"precio": 2800, "ingredientes": {"presa de pollo": 1, "porcion de harina": 1, "porcion de aceite": 1}},
            "Ensalada mixta": {"precio": 1500, "ingredientes": {"lechuga": 1, "tomate": 1, "zanahoria rallada": 1}},
        }

    def get_items(self):
        return self._items

    def get_item(self, nombre):
        return self._items.get(nombre)