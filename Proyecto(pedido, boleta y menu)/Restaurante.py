# Restaurante.py
import customtkinter as ctk
# Workaround: some versions of customtkinter may pass float values like 300.0
# to the underlying Tk canvas which raises _tkinter.TclError: bad screen distance "300.0".
# We monkey-patch the CTkCanvas __init__ to coerce width/height kwargs to int when needed.
try:
    # locate the module where CTkCanvas is defined (path used in traceback)
    from customtkinter.windows.widgets.core_rendering import ctk_canvas as _ctk_canvas_mod
    # save the original __init__ function to avoid recursion when patching
    _Original_CTkCanvas_init = _ctk_canvas_mod.CTkCanvas.__init__

    def _patched_ctkcanvas_init(self, *args, **kwargs):
        # Coerce width/height if they look like floats or float-strings
        for k in ("width", "height", "highlightthickness", "borderwidth"):
            if k in kwargs:
                v = kwargs[k]
                # handle floats and strings like '300.0'
                try:
                    if isinstance(v, float):
                        kwargs[k] = int(v)
                    elif isinstance(v, str) and v.replace('.', '', 1).isdigit() and '.' in v:
                        # convert numeric string with decimal to int
                        kwargs[k] = int(float(v))
                except Exception:
                    # if conversion fails, leave original value
                    pass

        # Call the original __init__ implementation
        return _Original_CTkCanvas_init(self, *args, **kwargs)

    _ctk_canvas_mod.CTkCanvas.__init__ = _patched_ctkcanvas_init
except Exception:
    # If the internal path changes between customtkinter versions, skip patch silently.
    # Upgrading/downgrading customtkinter is still recommended if issues persist.
    pass
try:
    import tkinter as _tk
    # Save original configure to avoid recursion
    _tk_Canvas_configure_orig = _tk.Canvas.configure

    def _patched_canvas_configure(self, cnf=None, **kw):
        # helper to coerce float-like values to int
        def _coerce_value(v):
            try:
                if isinstance(v, float):
                    return int(v)
                if isinstance(v, str) and v.replace('.', '', 1).isdigit() and '.' in v:
                    return int(float(v))
            except Exception:
                pass
            return v

        # coerce values in cnf if it's a dict
        if isinstance(cnf, dict):
            if 'width' in cnf:
                cnf['width'] = _coerce_value(cnf['width'])
            if 'height' in cnf:
                cnf['height'] = _coerce_value(cnf['height'])

        # coerce kw args
        if 'width' in kw:
            kw['width'] = _coerce_value(kw['width'])
        if 'height' in kw:
            kw['height'] = _coerce_value(kw['height'])

        return _tk_Canvas_configure_orig(self, cnf, **kw)

    _tk.Canvas.configure = _patched_canvas_configure
except Exception:
    # Non-fatal: if tkinter layout internals differ, skip patch
    pass
from PIL import Image
import os
import logging
import copy
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as _tk_messagebox

# Importar tus clases
from Menu import generar_menus # Importamos la función para crear los objetos Menu
from Pedido import Pedido, InsufficientStockError
from Stock import Stock
from Boleta import Boleta
from Ingrediente import Ingrediente # Solo para referencias de tipo

# --- Configuración Inicial ---
ctk.set_appearance_mode("System")  # Modo "System", "Dark", "Light"
ctk.set_default_color_theme("blue") 

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class RestauranteApp(ctk.CTk):
    """Aplicación principal de CustomTkinter para el restaurante."""
    def __init__(self):
        super().__init__()

        # Helper wrappers for messageboxes (fallback to tkinter.messagebox if CTkMessagebox missing)
        def _show_message(title: str, message: str, kind: str = "info"):
            mb = getattr(ctk, 'CTkMessagebox', None)
            try:
                if mb:
                    if kind == 'info':
                        mb(title=title, message=message)
                    elif kind == 'error':
                        mb(title=title, message=message, icon='cancel')
                    elif kind == 'warning':
                        mb(title=title, message=message, icon='warning')
                else:
                    if kind == 'info':
                        _tk_messagebox.showinfo(title, message)
                    elif kind == 'error':
                        _tk_messagebox.showerror(title, message)
                    elif kind == 'warning':
                        _tk_messagebox.showwarning(title, message)
            except Exception:
                # Last-resort fallback
                try:
                    if kind == 'info':
                        _tk_messagebox.showinfo(title, message)
                    elif kind == 'error':
                        _tk_messagebox.showerror(title, message)
                    else:
                        _tk_messagebox.showwarning(title, message)
                except Exception:
                    print(f"{title}: {message}")

        def _ask_confirm(title: str, message: str) -> bool:
            mb = getattr(ctk, 'CTkMessagebox', None)
            try:
                if mb:
                    resp = mb(title=title, message=message, icon='question', option_1='Sí', option_2='No')
                    # CTkMessagebox returns an object with .get()
                    try:
                        return resp.get() == 'Sí'
                    except Exception:
                        # fallback to truthy
                        return bool(resp)
                else:
                    return _tk_messagebox.askyesno(title, message)
            except Exception:
                try:
                    return _tk_messagebox.askyesno(title, message)
                except Exception:
                    return False

        # attach to instance for use in methods
        self._show_message = _show_message
        self._ask_confirm = _ask_confirm

        # --- Inicialización de Modelos ---
        self.menus = generar_menus()
        self.stock = self._setup_stock_inicial()
        self.pedido_actual = Pedido(cliente="Mesa 1") # Pedido en curso
        
        # Opcional: enlaza Menu.disponible_en_stock al método correcto en Menu.py
        # Esto es necesario porque tu clase Menu usa un método diferente al que Pedido.py espera (disponible_en_stock vs disponible_stock)
        for menu in self.menus:
            # Monkey-patching para compatibilidad
            if not hasattr(menu, 'disponible_en_stock'):
                menu.disponible_en_stock = menu.disponible_stock

        # --- Configuración de la Ventana ---
        self.title("Restaurante POS - CustomTkinter")
        self.geometry("1200x800")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Creación de Pestañas (Tabview) ---
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # Pestañas principales
        self.tab_menu = self.tab_view.add("Menú (Toma de Pedido)")
        self.tab_pedido = self.tab_view.add("Pedido Actual")
        self.tab_admin = self.tab_view.add("Administración/Stock") # Pestaña futura

        # Configurar el grid en cada pestaña para la distribución de elementos
        self.tab_menu.grid_columnconfigure(0, weight=1)
        # permitir que la fila 0 de la pestaña del menú crezca verticalmente
        self.tab_menu.grid_rowconfigure(0, weight=1)
        self.tab_pedido.grid_columnconfigure(0, weight=1)
        self.tab_pedido.grid_rowconfigure(0, weight=1)

        # --- Construcción de la Interfaz ---
        self._crear_interfaz_menu()
        self._crear_interfaz_pedido()
        # crear la interfaz de administración/stock
        self._crear_interfaz_admin()

        # Actualizar disponibilidad al inicio
        self.actualizar_disponibilidad_menu()
    
    # --- Métodos de Setup ---
    def _setup_stock_inicial(self) -> Stock:
        """Inicializa el stock con algunos ingredientes de ejemplo."""
        stock = Stock()
        # Simulación de carga inicial de inventario
        datos_iniciales = [
            ["papas", "unidades", 50],
            ["pepsi", "unidades", 100],
            ["vienesa", "unidades", 20],
            ["pan de completo", "unidades", 20],
            ["tomate", "unidades", 10],
            ["palta", "unidades", 5],
            ["pan de hamburguesa", "unidades", 15],
            ["lámina de queso", "unidades", 15],
            ["churrasco de carne", "unidades", 15],
            ["panqueques", "unidades", 30],
            ["manjar", "unidades", 10],
            ["azúcar flor", "unidades", 10],
            ["presa de pollo", "unidades", 25],
            ["porción de harina", "unidades", 50],
            ["porción de aceite", "unidades", 50],
            ["lechuga", "unidades", 10],
            ["zanahoria rallada", "unidades", 10],
        ]
        stock.cargar_lista_csv(datos_iniciales)
        return stock
    
    # --- Interfaz Menú ---
    def _crear_interfaz_menu(self):
        """Crea el scrollable frame con los botones del menú."""
        
        # Contenedor con scroll para el menú
        self.menu_scroll_frame = ctk.CTkScrollableFrame(self.tab_menu, label_text="Platos Disponibles")
        self.menu_scroll_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.menu_scroll_frame.grid_columnconfigure(0, weight=1) # Columna central
        
        self.menu_botones: list[ctk.CTkButton] = [] # Para almacenar referencias a los botones
        
        # Crear los botones del menú en una cuadrícula (grid)
        columnas = 3
        for i, menu in enumerate(self.menus):
            row = i // columnas
            col = i % columnas
            
            # Cargar imagen (manejo básico de errores si no existe la carpeta assets)
            img_path = menu.imagen_path if os.path.exists(menu.imagen_path) else None
            ctk_image = None
            if img_path:
                try:
                    # Usamos Image.open de PIL para cargar y redimensionar
                    img_pil = Image.open(img_path).resize((100, 100))
                    ctk_image = ctk.CTkImage(light_image=img_pil, dark_image=img_pil, size=(100, 100))
                except Exception as e:
                    logger.warning(f"No se pudo cargar la imagen para {menu.nombre}: {e}")
            
            # Texto del botón
            texto = f"{menu.nombre}\n${menu.precio:,.0f}"
            
            # Crear y posicionar el botón del menú
            # Usamos una lambda para pasar el objeto 'menu' al callback
            btn = ctk.CTkButton(
                self.menu_scroll_frame, 
                text=texto, 
                image=ctk_image, 
                compound="top", # Imagen arriba, texto abajo
                command=lambda m=menu: self.agregar_al_pedido(m),
                width=150, 
                height=150
            )
            btn.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            self.menu_botones.append(btn) # Guardar referencia
            
            # Inicialmente, verificar disponibilidad (el método hace esto)
            self._actualizar_estado_boton(btn, menu)


    def _actualizar_estado_boton(self, btn: ctk.CTkButton, menu):
        """Actualiza el texto y estado del botón según la disponibilidad."""
        if not hasattr(menu, 'disponible_en_stock'): # chequeo de seguridad
             return
             
        disponible = menu.disponible_en_stock(self.stock, 1)
        
        if disponible:
            btn.configure(state="normal", text_color="white", fg_color=ctk.ThemeManager.theme['CTkButton']['fg_color'])
        else:
            btn.configure(state="disabled", text_color="gray", fg_color="red")
            
        menu.disponible = disponible # Actualiza el atributo del objeto Menu
        

    def actualizar_disponibilidad_menu(self):
        """Recorre todos los botones y actualiza su estado de stock."""
        for i, menu in enumerate(self.menus):
            btn = self.menu_botones[i]
            self._actualizar_estado_boton(btn, menu)
            
    # --- Lógica de Pedido ---
    def agregar_al_pedido(self, menu_obj):
        """Callback al presionar un botón del menú."""
        self.pedido_actual.agregar_menu(menu_obj, cantidad=1)
        self.actualizar_interfaz_pedido() # Refresca el panel del pedido

    # --- Interfaz Pedido Actual ---
    def _crear_interfaz_pedido(self):
        """Crea el panel lateral o la pestaña para ver y gestionar el pedido actual."""
        
        # Frame superior para los ítems del pedido (scrollable)
        self.pedido_items_frame = ctk.CTkScrollableFrame(self.tab_pedido, label_text="Ítems del Pedido")
        self.pedido_items_frame.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")
        self.pedido_items_frame.grid_columnconfigure(0, weight=1)

        # Frame inferior para totales y acciones
        self.pedido_acciones_frame = ctk.CTkFrame(self.tab_pedido, fg_color="transparent")
        self.pedido_acciones_frame.grid(row=1, column=0, padx=20, pady=10, sticky="sew")
        self.pedido_acciones_frame.grid_columnconfigure((0, 1, 2), weight=1) # 3 columnas para botones
        
        # Labels de totales
        self.label_subtotal = ctk.CTkLabel(self.pedido_acciones_frame, text="Subtotal: $0", font=ctk.CTkFont(size=16, weight="bold"))
        self.label_subtotal.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.label_total = ctk.CTkLabel(self.pedido_acciones_frame, text="Total: $0", font=ctk.CTkFont(size=20, weight="bold"))
        self.label_total.grid(row=0, column=2, padx=10, pady=5, sticky="e")
        
        # Botones de acción
        self.btn_pagar = ctk.CTkButton(self.pedido_acciones_frame, text="Pagar y Generar Boleta (Falta IVA)", command=self.procesar_pago)
        self.btn_pagar.grid(row=1, column=2, padx=10, pady=10, sticky="e")
        
        self.btn_cancelar = ctk.CTkButton(self.pedido_acciones_frame, text="Cancelar Pedido", fg_color="red", hover_color="darkred", command=self.cancelar_pedido)
        self.btn_cancelar.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        
        # Inicializar la vista del pedido
        self.actualizar_interfaz_pedido()


    def _crear_interfaz_admin(self):
        """Crea la vista de administración / stock en la pestaña correspondiente."""
        # Clear tab_admin if needed
        for w in self.tab_admin.winfo_children():
            w.destroy()

        # Frame contenedor
        admin_frame = ctk.CTkFrame(self.tab_admin)
        admin_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.tab_admin.grid_rowconfigure(0, weight=1)
        self.tab_admin.grid_columnconfigure(0, weight=1)

        # Top controls
        controls = ctk.CTkFrame(admin_frame, fg_color="transparent")
        controls.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        controls.grid_columnconfigure(0, weight=1)

        btn_refresh = ctk.CTkButton(controls, text="Refrescar Stock", command=self.actualizar_vista_stock)
        btn_refresh.grid(row=0, column=0, sticky="w", padx=5)

        # Treeview area inside a normal tk.Frame so ttk.Treeview can be used
        tree_container = tk.Frame(admin_frame)
        tree_container.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        admin_frame.grid_rowconfigure(1, weight=1)

        cols = ("nombre", "unidad", "cantidad")
        self.stock_tree = ttk.Treeview(tree_container, columns=cols, show="headings", selectmode="browse")
        self.stock_tree.heading("nombre", text="Nombre")
        self.stock_tree.heading("unidad", text="Unidad")
        self.stock_tree.heading("cantidad", text="Cantidad")
        self.stock_tree.column("nombre", width=200, anchor="w")
        self.stock_tree.column("unidad", width=100, anchor="center")
        self.stock_tree.column("cantidad", width=100, anchor="e")
        self.stock_tree.pack(fill="both", expand=True, side="left")

        # Add vertical scrollbar
        vsb = ttk.Scrollbar(tree_container, orient="vertical", command=self.stock_tree.yview)
        self.stock_tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")

        # Inicial populate
        self.actualizar_vista_stock()

    def actualizar_vista_stock(self):
        """Actualiza la tabla de stock desde self.stock.inventario."""
        try:
            # limpiar rows existentes
            for r in self.stock_tree.get_children():
                self.stock_tree.delete(r)

            # insertar filas desde el inventario
            for clave, ing in self.stock.inventario.items():
                nombre = getattr(ing, 'nombre', clave)
                unidad = getattr(ing, 'unidad', '')
                cantidad = getattr(ing, 'cantidad', 0)
                # mostrar cantidad sin demasiados decimales si es entero
                if float(cantidad).is_integer():
                    cantidad_display = f"{int(cantidad)}"
                else:
                    cantidad_display = f"{cantidad:.2f}"
                self.stock_tree.insert("", "end", values=(nombre, unidad, cantidad_display))
        except Exception as e:
            logger.error("Error al refrescar vista de stock: %s", e)


    def actualizar_interfaz_pedido(self):
        """Redibuja la lista de items y los totales del pedido actual."""
        
        # 1. Eliminar widgets anteriores
        for widget in self.pedido_items_frame.winfo_children():
            widget.destroy()

        # 2. Re-dibujar los ítems
        if not self.pedido_actual.items:
            ctk.CTkLabel(self.pedido_items_frame, text="No hay ítems en el pedido.", text_color="gray").pack(padx=20, pady=20)
            self.label_subtotal.configure(text="Subtotal: $0")
            self.label_total.configure(text="Total: $0")
            return

        # Cabecera de la lista
        header_frame = ctk.CTkFrame(self.pedido_items_frame, fg_color="#444")
        header_frame.pack(fill="x", padx=5, pady=(0, 5))
        header_frame.grid_columnconfigure(0, weight=4) # Nombre
        header_frame.grid_columnconfigure(1, weight=1) # Cantidad
        header_frame.grid_columnconfigure(2, weight=1) # Precio Unitario
        header_frame.grid_columnconfigure(3, weight=2) # Subtotal
        header_frame.grid_columnconfigure(4, weight=1) # Botón

        ctk.CTkLabel(header_frame, text="Nombre", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(header_frame, text="Cant.", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=5, pady=5)
        ctk.CTkLabel(header_frame, text="P. Unit.", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=5, pady=5)
        ctk.CTkLabel(header_frame, text="Subtotal", font=ctk.CTkFont(weight="bold")).grid(row=0, column=3, padx=5, pady=5, sticky="e")
        ctk.CTkLabel(header_frame, text="", font=ctk.CTkFont(weight="bold")).grid(row=0, column=4, padx=5, pady=5) # Espacio para el botón de quitar

        # Lista de ítems
        for i, item in enumerate(self.pedido_actual.items):
            item_frame = ctk.CTkFrame(self.pedido_items_frame)
            item_frame.pack(fill="x", padx=5, pady=2)
            item_frame.grid_columnconfigure(0, weight=4)
            item_frame.grid_columnconfigure(1, weight=1)
            item_frame.grid_columnconfigure(2, weight=1)
            item_frame.grid_columnconfigure(3, weight=2)
            item_frame.grid_columnconfigure(4, weight=1)

            # Nombre
            ctk.CTkLabel(item_frame, text=item.menu.nombre, anchor="w").grid(row=0, column=0, padx=5, pady=2, sticky="w")
            # Cantidad
            ctk.CTkLabel(item_frame, text=f"x{item.cantidad}", anchor="center").grid(row=0, column=1, padx=5, pady=2)
            # Precio Unitario
            ctk.CTkLabel(item_frame, text=f"${item.menu.precio:,.0f}", anchor="center").grid(row=0, column=2, padx=5, pady=2)
            # Subtotal
            ctk.CTkLabel(item_frame, text=f"${item.subtotal():,.0f}", anchor="e").grid(row=0, column=3, padx=5, pady=2, sticky="e")
            # Botón Quitar 
            btn_quitar = ctk.CTkButton(
                item_frame, 
                text="🗑️", 
                width=30, 
                height=30, 
                fg_color="red", 
                hover_color="darkred", 
                command=lambda nombre=item.menu.nombre: self.quitar_del_pedido(nombre)
            )
            btn_quitar.grid(row=0, column=4, padx=5, pady=2, sticky="e")
            
        # 3. Actualizar Totales
        subtotal_val = self.pedido_actual.subtotal()
        total_val = self.pedido_actual.total(aplicar_iva=False) # Se podría cambiar a True para incluir IVA
        
        self.label_subtotal.configure(text=f"Subtotal: ${subtotal_val:,.0f}")
        self.label_total.configure(text=f"Total: ${total_val:,.0f}")

    def quitar_del_pedido(self, nombre_menu: str):
        """Quita un ítem completo (todas las cantidades) del pedido."""
        self.pedido_actual.quitar_menu(nombre_menu) # Usará el valor por defecto, quitando todos
        self.actualizar_interfaz_pedido()

    # --- Acciones Finales ---
    def procesar_pago(self):
        """Intenta finalizar el pedido, consumir stock y generar boleta."""
        try:
            # 1. Validar y Consumir Stock
            self.pedido_actual.aplicar_consumo_en_stock(self.stock)
            
            # 2. Copiar el pedido para generar la boleta y reiniciar el pedido actual
            pedido_para_boleta = copy.deepcopy(self.pedido_actual)

            # Reiniciar el pedido actual inmediatamente (UI se actualiza)
            self.iniciar_nuevo_pedido()

            # 3. Generar Boleta (PDF) a partir de la copia (no bloquea el pedido actual)
            ruta_boleta = f"boleta_{pedido_para_boleta.pedido_id[:8]}.pdf"
            boleta = Boleta(pedido_para_boleta)
            boleta.generar_pdf(ruta_boleta)

            # 4. Mostrar Mensaje de Éxito
            self._show_message("Pago Exitoso", f"Pago procesado. Stock descontado. Boleta generada en:\n{ruta_boleta}", kind='info')

        except InsufficientStockError as e:
            # 1. Mostrar Error
            self._show_message("Error de Stock", str(e), kind='error')
            
        except Exception as e:
            # 2. Mostrar Error genérico
            logger.error("Error inesperado al procesar el pago: %s", e)
            self._show_message("Error", f"Ocurrió un error inesperado: {e}", kind='error')
            
        # 5. Actualizar interfaz del menú y disponibilidad
        self.actualizar_disponibilidad_menu()


    def cancelar_pedido(self):
        """Cancela el pedido actual y lo vacía sin modificar stock."""
        if self._ask_confirm("Confirmar Cancelación", "¿Estás seguro de que quieres cancelar el pedido actual?"):
            self.pedido_actual.vaciar()
            self.actualizar_interfaz_pedido()
            self._show_message("Cancelado", "El pedido ha sido cancelado y vaciado.")


    def iniciar_nuevo_pedido(self):
        """Crea una nueva instancia de pedido para la siguiente mesa/cliente."""
        self.pedido_actual = Pedido(cliente="Mesa X") # Puedes hacer que pida el nombre de la mesa
        # Opcional: limpiar la pestaña "Pedido Actual"
        self.actualizar_interfaz_pedido()


if __name__ == "__main__":
    # Asegúrate de que exista la carpeta 'assets' para las imágenes, si no, fallará la carga de imágenes.
    if not os.path.exists("assets"):
        print("Advertencia: No existe la carpeta 'assets'. El código de imágenes será ignorado.")
        
    app = RestauranteApp()
    app.mainloop()











































