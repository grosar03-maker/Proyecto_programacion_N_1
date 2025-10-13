from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import List, Dict, Any
import uuid
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class InsufficientStockError(Exception):
    """Raised when there is not enough stock to fulfil the pedido."""
    pass


@dataclass
class ItemPedido:
    menu: Any  # se espera un objeto Menu con atributos: nombre, precio, ingredientes_req, etc.
    cantidad: int = 1

    def subtotal(self) -> float:
        return float(self.menu.precio) * int(self.cantidad)

    def to_dict(self) -> Dict:
        return {"menu": getattr(self.menu, "nombre", str(self.menu)), "cantidad": self.cantidad, "precio_unit": float(self.menu.precio)}


class Pedido:
    """
    Clase que representa un pedido: lista de items (menus) con cantidades.
    - Se encarga de agregar/quitar ítems.
    - Calcular totales.
    - Validar y consumir stock al confirmar el pedido (acción atómica: primero verifica, luego consume).
    """
    def __init__(self, cliente: str = "Cliente", pedido_id: str | None = None):
        self.items: List[ItemPedido] = []
        self.cliente = cliente
        self.pedido_id = pedido_id or str(uuid.uuid4())
        self.meta: Dict[str, Any] = {}  # campo libre para añadir datos (mesa, usuario, notas)

    # --- gestión de ítems ---
    def agregar_menu(self, menu, cantidad: int = 1) -> None:
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor que 0.")
        for it in self.items:
            if it.menu.nombre == menu.nombre:
                it.cantidad += cantidad
                logger.debug("Aumentado cantidad de %s a %d", menu.nombre, it.cantidad)
                return
        self.items.append(ItemPedido(menu=menu, cantidad=cantidad))
        logger.info("Agregado al pedido: %s x%d", menu.nombre, cantidad)

    def quitar_menu(self, nombre_menu: str, cantidad: int | None = None) -> None:
        nombre_menu = nombre_menu.strip()
        for it in list(self.items):
            if it.menu.nombre == nombre_menu:
                if cantidad is None or cantidad >= it.cantidad:
                    self.items.remove(it)
                    logger.info("Removido %s del pedido", nombre_menu)
                else:
                    it.cantidad -= cantidad
                    logger.info("Reducida cantidad de %s a %d", nombre_menu, it.cantidad)
                return
        logger.debug("Intentaron quitar %s pero no estaba en el pedido", nombre_menu)

    def vaciar(self) -> None:
        self.items.clear()
        logger.info("Pedido %s vaciado", self.pedido_id)

    # --- cálculos ---
    def total(self, aplicar_iva: bool = False, iva_pct: float = 0.19) -> float:
        subtotal = sum(it.subtotal() for it in self.items)
        if aplicar_iva:
            return subtotal * (1 + float(iva_pct))
        return subtotal

    def subtotal(self) -> float:
        return sum(it.subtotal() for it in self.items)

    # --- stock ---
    def validar_stock(self, stock) -> None:
        """
        Verifica que haya stock suficiente para todos los ítems del pedido.
        Lanza InsufficientStockError con mensaje detallado si falta algo.
        """
        faltantes = []
        for it in self.items:
            menu = it.menu
            if not menu.disponible_en_stock(stock, it.cantidad):
                faltantes.append((menu.nombre, it.cantidad))
        if faltantes:
            msgs = [f"{nombre} x{cant}" for (nombre, cant) in faltantes]
            msg = "Stock insuficiente para: " + ", ".join(msgs)
            logger.warning(msg)
            raise InsufficientStockError(msg)

    def aplicar_consumo_en_stock(self, stock) -> None:
        """
        Intenta consumir los ingredientes en stock de manera atómica:
        1) valida
        2) consume (llama a menu.consumir_ingredientes)
        Si falla en la validación, lanza InsufficientStockError y NO modifica el stock.
        """
        logger.debug("Validando stock para pedido %s", self.pedido_id)
        self.validar_stock(stock)  # lanzará si hay faltantes

        # si pasó validación, consumimos
        logger.debug("Consumiendo ingredientes en stock para pedido %s", self.pedido_id)
        for it in self.items:
            success = it.menu.consumir_ingredientes(stock, it.cantidad)
            if not success:
                # condición excepcional: si un menu falla al consumir (debería ya haber sido validado)
                msg = f"Error al consumir ingredientes para {it.menu.nombre}"
                logger.error(msg)
                raise InsufficientStockError(msg)
        logger.info("Stock actualizado exitosamente para pedido %s", self.pedido_id)

    # --- serialización / utilidades ---
    def to_dict(self) -> Dict:
        return {
            "pedido_id": self.pedido_id,
            "cliente": self.cliente,
            "items": [it.to_dict() for it in self.items],
            "subtotal": self.subtotal(),
        }

    @classmethod
    def from_dict(cls, d: Dict, menu_lookup) -> "Pedido":
        """
        Reconstruye un Pedido desde dict; menu_lookup(nombre)->Menu debe ser provisto para mapear nombres a objetos Menu.
        """
        p = cls(cliente=d.get("cliente", "Cliente"), pedido_id=d.get("pedido_id"))
        for it in d.get("items", []):
            menu_obj = menu_lookup(it["menu"])
            p.agregar_menu(menu_obj, int(it.get("cantidad", 1)))
        return p
