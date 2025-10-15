import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import customtkinter as ctk
import csv
import os
import subprocess
from PIL import Image
import fitz  # PyMuPDF

# --- Import de las clases y funciones de los otros archivos ---
from Ingrediente import Ingrediente
from Stock import Stock
from Menu import Menu
from Pedido import Pedido
from Menupdf import MenuPDF
from Boleta import BoletaPDF

# --- Configuración de la Apariencia ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class RestauranteApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Gestión de Restaurante")
        self.geometry("900x700")

        self.stock = Stock()
        self.menu = Menu()
        self.pedido_actual = Pedido()
        self.total_pedido_var = tk.StringVar(value="Total: $0")
        
        # --- Estilo del Treeview para el tema oscuro ---
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2a2d2e", foreground="white", rowheight=25, fieldbackground="#343638", bordercolor="#343638", borderwidth=0)
        style.map('Treeview', background=[('selected', '#22559b')])
        style.configure("Treeview.Heading", background="#565b5e", foreground="white", relief="flat")
        style.map("Treeview.Heading", background=[('active', '#3484F0')])

        # --- Creación de Pestañas ---
        self.tab_view = ctk.CTkTabview(self, width=250)
        self.tab_view.pack(pady=10, padx=10, fill="both", expand=True)
        self.tab_view.add("Carga Ingredientes")
        self.tab_view.add("Stock")
        self.tab_view.add("Carta Restaurante")
        self.tab_view.add("Pedido")

        self.setup_tab1()
        self.setup_tab2()
        self.setup_tab3()
        self.setup_tab4()

    def setup_tab1(self):
        tab = self.tab_view.tab("Carga Ingredientes")
        btn_cargar_csv = ctk.CTkButton(tab, text="Cargar Archivo CSV", command=self.cargar_csv, height=40)
        btn_cargar_csv.pack(pady=15, padx=20)
        tree_frame = ctk.CTkFrame(tab, fg_color="transparent")
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)
        self.tree_ingredientes_carga = ttk.Treeview(tree_frame, columns=("nombre", "unidad", "cantidad"), show="headings")
        self.tree_ingredientes_carga.heading("nombre", text="Nombre")
        self.tree_ingredientes_carga.heading("unidad", text="Unidad")
        self.tree_ingredientes_carga.heading("cantidad", text="Cantidad")
        self.tree_ingredientes_carga.pack(side="left", fill="both", expand=True)
        scrollbar = ctk.CTkScrollbar(tree_frame, command=self.tree_ingredientes_carga.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree_ingredientes_carga.configure(yscrollcommand=scrollbar.set)
        btn_agregar_stock = ctk.CTkButton(tab, text="Agregar al Stock", command=self.agregar_a_stock, height=40)
        btn_agregar_stock.pack(pady=15, padx=20)

    def setup_tab2(self):
        tab = self.tab_view.tab("Stock")
        tab.grid_columnconfigure(0, weight=3); tab.grid_columnconfigure(1, weight=1); tab.grid_rowconfigure(0, weight=1)
        stock_frame = ctk.CTkFrame(tab)
        stock_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.tree_stock = ttk.Treeview(stock_frame, columns=("nombre", "unidad", "cantidad"), show="headings")
        self.tree_stock.heading("nombre", text="Nombre"); self.tree_stock.heading("unidad", text="Unidad"); self.tree_stock.heading("cantidad", text="Cantidad")
        self.tree_stock.pack(fill="both", expand=True, padx=10, pady=10)
        controls_frame = ctk.CTkFrame(tab)
        controls_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        add_ingredient_frame = ctk.CTkFrame(controls_frame)
        add_ingredient_frame.pack(fill="x", pady=10, padx=10)
        ctk.CTkLabel(add_ingredient_frame, text="Agregar Ingrediente", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        self.entry_nombre = ctk.CTkEntry(add_ingredient_frame, placeholder_text="Nombre")
        self.entry_nombre.pack(fill="x", padx=10, pady=5)
        self.combo_unidad = ctk.CTkComboBox(add_ingredient_frame, values=["unidad", "gramos", "cc", "porcion", "kg"])
        self.combo_unidad.set("unidad")
        self.combo_unidad.pack(fill="x", padx=10, pady=5)
        self.entry_cantidad = ctk.CTkEntry(add_ingredient_frame, placeholder_text="Cantidad")
        self.entry_cantidad.pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(add_ingredient_frame, text="Agregar", command=self.agregar_ingrediente_manual).pack(fill="x", padx=10, pady=10)
        ctk.CTkButton(controls_frame, text="Eliminar Seleccionado", command=self.eliminar_ingrediente).pack(fill="x", pady=(20, 5), padx=10)
        
        # --- BOTÓN MODIFICADO ---
        ctk.CTkButton(controls_frame, text="Generar Menú y Ver Carta", command=self.generar_menu_y_ver_carta).pack(fill="x", pady=5, padx=10)

    def setup_tab3(self):
        # --- PESTAÑA SIMPLIFICADA A SOLO VISOR ---
        tab = self.tab_view.tab("Carta Restaurante")
        tab.grid_columnconfigure(0, weight=1); tab.grid_rowconfigure(0, weight=1)
        self.pdf_view_frame = ctk.CTkScrollableFrame(tab, label_text="Vista Previa de la Carta")
        self.pdf_view_frame.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")
        self.pdf_display_label = ctk.CTkLabel(self.pdf_view_frame, text="El menú generado desde la pestaña 'Stock' aparecerá aquí.")
        self.pdf_display_label.pack(fill="both", expand=True)

    def setup_tab4(self):
        tab = self.tab_view.tab("Pedido")
        tab.grid_columnconfigure(0, weight=1); tab.grid_columnconfigure(1, weight=1); tab.grid_rowconfigure(0, weight=1)
        menu_frame = ctk.CTkFrame(tab)
        menu_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(menu_frame, text="Menú Disponible", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        scrollable_menu = ctk.CTkScrollableFrame(menu_frame, label_text="")
        scrollable_menu.pack(fill="both", expand=True, padx=10, pady=5)
        for item_nombre in self.menu.get_items().keys():
            ctk.CTkButton(scrollable_menu, text=item_nombre, command=lambda n=item_nombre: self.agregar_a_pedido(n)).pack(fill="x", padx=10, pady=4)
        pedido_frame = ctk.CTkFrame(tab)
        pedido_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(pedido_frame, text="Mi Pedido", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        ctk.CTkLabel(pedido_frame, textvariable=self.total_pedido_var, font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)
        pedido_controls_frame = ctk.CTkFrame(pedido_frame, fg_color="transparent")
        pedido_controls_frame.pack(fill="x", pady=5, padx=10)
        pedido_controls_frame.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(pedido_controls_frame, text="Eliminar Ítem", command=self.eliminar_item_pedido).grid(row=0, column=0, padx=5, sticky="ew")
        ctk.CTkButton(pedido_controls_frame, text="Reiniciar Pedido", command=self.reiniciar_pedido).grid(row=0, column=1, padx=5, sticky="ew")
        tree_pedido_frame = ctk.CTkFrame(pedido_frame, fg_color="transparent")
        tree_pedido_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree_pedido = ttk.Treeview(tree_pedido_frame, columns=("id", "item", "precio"), show="headings")
        self.tree_pedido.heading("id", text="ID"); self.tree_pedido.heading("item", text="Ítem"); self.tree_pedido.heading("precio", text="Precio")
        self.tree_pedido.column("id", width=40, anchor=tk.CENTER)
        self.tree_pedido.pack(fill="both", expand=True)
        ctk.CTkButton(pedido_frame, text="Generar Boleta", command=self.generar_boleta_final, height=40).pack(fill="x", pady=10, padx=10)

    # --- Lógica de la Aplicación ---
    
    def generar_menu_y_ver_carta(self):
        # --- TODA LA LÓGICA DE GENERACIÓN ESTÁ AHORA AQUÍ ---
        try:
            messagebox.showinfo("Procesando", "Generando el PDF del menú...")
            items_carta = [{"nombre": k, "precio": f"${v['precio']}"} for k, v in self.menu.get_items().items()]
            
            pdf_generator = MenuPDF(items_carta)
            filepath = pdf_generator.generar("carta_restaurante.pdf")

            if not filepath:
                raise Exception("El archivo PDF no se pudo crear. Revisa la consola para más detalles.")

            doc = fitz.open(filepath)
            page = doc.load_page(0)
            pix = page.get_pixmap()
            doc.close()
            
            menu_image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            ctk_image = ctk.CTkImage(light_image=menu_image, dark_image=menu_image, size=(menu_image.width, menu_image.height))
            
            self.pdf_display_label.configure(image=ctk_image, text="")
            self.pdf_display_label.image = ctk_image
            
            # Cambiar a la pestaña de la carta para ver el resultado
            self.tab_view.set("Carta Restaurante")
            messagebox.showinfo("Éxito", "La carta se ha generado y se muestra en la pestaña 'Carta Restaurante'.")
            
        except Exception as e:
            messagebox.showerror("Error al Visualizar PDF", f"No se pudo mostrar el PDF en la aplicación.\n\nError: {e}")

    # (Aquí va el resto de las funciones: cargar_csv, agregar_a_stock, agregar_ingrediente_manual, etc. No cambian, así que no se repiten aquí)
    def refrescar_stock_treeview(self):
        """Limpia y vuelve a cargar el treeview de stock desde el objeto Stock."""
        # Borra todos los items actuales de la tabla
        for i in self.tree_stock.get_children():
            self.tree_stock.delete(i)
    
        # Vuelve a insertar cada ingrediente desde el objeto stock
        for ing in self.stock.get_ingredientes():
            # --- CAMBIO IMPORTANTE AQUÍ ---
            # Se asegura de que la cantidad se muestre como un número entero
            cantidad_entera = int(ing.cantidad)
            self.tree_stock.insert("", "end", values=(ing.nombre, ing.unidad, cantidad_entera))
            
    def cargar_csv(self):
        filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not filepath: return
        try:
            with open(filepath, mode='r', encoding='utf-8') as file:
                reader = csv.reader(file)
                for i in self.tree_ingredientes_carga.get_children(): self.tree_ingredientes_carga.delete(i)
                for row in reader:
                    if len(row) == 3: self.tree_ingredientes_carga.insert("", "end", values=row)
            messagebox.showinfo("Éxito", "Archivo CSV cargado.")
        except Exception as e: messagebox.showerror("Error", f"No se pudo leer el archivo: {e}")
    def agregar_a_stock(self):
        items, agregados, errores = self.tree_ingredientes_carga.get_children(), 0, 0
        if not items: messagebox.showwarning("Vacío", "No hay ingredientes para agregar."); return
        for item_id in items:
            try:
                nombre, unidad, cantidad_str = self.tree_ingredientes_carga.item(item_id, "values")
                self.stock.agregar_ingrediente(Ingrediente(nombre, unidad, int(float(cantidad_str)))); agregados += 1
            except (ValueError, IndexError) as e: errores += 1; print(f"Error procesando fila: {e}")
        if agregados > 0:
            self.refrescar_stock_treeview(); self.tab_view.set("Stock")
            for item_id in items: self.tree_ingredientes_carga.delete(item_id)
            messagebox.showinfo("Éxito", f"{agregados} ingrediente(s) agregados al stock.")
        if errores > 0: messagebox.showwarning("Atención", f"Se omitieron {errores} fila(s) por formato incorrecto.")
    def agregar_ingrediente_manual(self):
        nombre, unidad, cantidad_str = self.entry_nombre.get(), self.combo_unidad.get(), self.entry_cantidad.get()
        if not nombre or not cantidad_str: messagebox.showerror("Error", "Nombre y cantidad son obligatorios."); return
        try:
            self.stock.agregar_ingrediente(Ingrediente(nombre, unidad, int(float(cantidad_str)))); self.refrescar_stock_treeview()
            messagebox.showinfo("Éxito", f"Ingrediente '{nombre}' agregado.")
            self.entry_nombre.delete(0, tk.END); self.entry_cantidad.delete(0, tk.END)
        except ValueError: messagebox.showerror("Error", "La cantidad debe ser un número válido.")
    def eliminar_ingrediente(self):
        selected = self.tree_stock.selection()
        if not selected: messagebox.showerror("Error", "Seleccione un ingrediente para eliminar."); return
        nombre = self.tree_stock.item(selected[0], "values")[0]
        self.stock.eliminar_ingrediente(nombre); self.refrescar_stock_treeview()
        messagebox.showinfo("Éxito", f"Ingrediente '{nombre}' eliminado.")
    def agregar_a_pedido(self, nombre_item):
        # Verifica si hay ingredientes suficientes
        if self.stock.verificar_stock_para_item(self.menu.get_item(nombre_item)['ingredientes']):
            # Si hay stock, descuenta los ingredientes
            self.stock.descontar_ingredientes(self.menu.get_item(nombre_item)['ingredientes'])
        
            # Agrega el item al pedido y actualiza las tablas
            self.pedido_actual.agregar_item(self.menu.get_item(nombre_item), nombre_item)
            self.refrescar_pedido_treeview()
            self.refrescar_stock_treeview()
        
            # --- LÍNEA DE MENSAJE ELIMINADA ---
            # Ya no se muestra el messagebox.showinfo("Éxito", ...)
        
        else:
            # Si no hay stock, SÍ se muestra el mensaje de advertencia
            messagebox.showwarning("Stock Insuficiente", f"No hay suficientes ingredientes para preparar '{nombre_item}'.")

    def eliminar_item_pedido(self):
        selected = self.tree_pedido.selection()
        if not selected: messagebox.showerror("Error", "Seleccione un ítem para eliminar."); return
        item_id_en_pedido = int(self.tree_pedido.item(selected[0], "values")[0])
        item_eliminado = self.pedido_actual.eliminar_item(item_id_en_pedido)
        if item_eliminado:
            self.stock.reponer_ingredientes(item_eliminado['ingredientes']); self.refrescar_pedido_treeview(); self.refrescar_stock_treeview()
            messagebox.showinfo("Éxito", f"Ítem eliminado. Stock repuesto.")
    def reiniciar_pedido(self):
        if not self.pedido_actual.get_items(): messagebox.showinfo("Info", "El pedido ya está vacío."); return
        if messagebox.askyesno("Confirmar", "¿Reiniciar el pedido? Se repondrá todo el stock."):
            for item in self.pedido_actual.get_items(): self.stock.reponer_ingredientes(item['ingredientes'])
            self.pedido_actual.limpiar(); self.refrescar_pedido_treeview(); self.refrescar_stock_treeview()
            messagebox.showinfo("Éxito", "Pedido reiniciado y stock restaurado.")
    def refrescar_pedido_treeview(self):
        for i in self.tree_pedido.get_children(): self.tree_pedido.delete(i)
        for item in self.pedido_actual.get_items(): self.tree_pedido.insert("", "end", values=(item['id'], item['nombre'], f"${item['precio']:,}".replace(",", ".")))
        self.total_pedido_var.set(f"Total: ${self.pedido_actual.calcular_total():,}".replace(",", "."))
    def generar_boleta_final(self):
        if not self.pedido_actual.get_items(): messagebox.showerror("Error", "No hay ítems para generar boleta."); return
        try:
            boleta_generator = BoletaPDF(self.pedido_actual); filepath = boleta_generator.generar("boleta_pedido.pdf")
            messagebox.showinfo("Boleta Generada", f"Boleta generada en '{filepath}'. Abriendo archivo...")
            if os.name == 'nt': os.startfile(filepath)
            else: subprocess.call(['open', filepath])
            self.pedido_actual.limpiar(); self.refrescar_pedido_treeview()
        except Exception as e: messagebox.showerror("Error", f"No se pudo generar la boleta: {e}")

if __name__ == "__main__":
    app = RestauranteApp()
    app.mainloop()