import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from functools import partial
from modelo import (catalogo_inicial, agregar, confirmar, total_carrito, sugerir_pares)


# ---------- PALETA RETRO 80s / SYNTHWAVE ----------
BG_DARK = "#1a0b2e"        # fondo principal (violeta noche)
BG_PANEL = "#241b38"       # fondo de paneles
NEON_PINK = "#ff2e97"
NEON_CYAN = "#00fff5"
NEON_PURPLE = "#b967ff"
NEON_YELLOW = "#ffe66d"
TEXT_LIGHT = "#f5f0ff"
FONT_MONO = "Courier New"


class Aplicacion:
    def __init__(self):
        self.productos = catalogo_inicial()
        self.carrito = []
        self.ventas = []
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.ventana = ctk.CTk()
        self.ventana.configure(fg_color=BG_DARK)
        self.ventana.title("RecreoLab | Demostración escolar")
        self.ventana.geometry("1000x650")
        self.ventana.minsize(900, 600)
        self.ventana.grid_columnconfigure(0, weight=1)
        self.ventana.grid_rowconfigure(2, weight=1)

        self.crear_header()

        separador = ctk.CTkLabel(
            self.ventana,
            text="▓" * 60,
            font=(FONT_MONO, 12),
            text_color=NEON_PURPLE,
        )
        separador.grid(row=1, column=0, pady=(0, 6))

        self.tabs = ctk.CTkTabview(
            self.ventana,
            fg_color=BG_PANEL,
            segmented_button_fg_color=BG_DARK,
            segmented_button_selected_color=NEON_PINK,
            segmented_button_selected_hover_color=NEON_PURPLE,
            segmented_button_unselected_color=BG_DARK,
            segmented_button_unselected_hover_color=BG_PANEL,
            text_color=TEXT_LIGHT,
        )
        self.tabs.grid(row=2, column=0, padx=16, pady=8, sticky="nsew")
        self.tabs.add("Kiosco")
        self.tabs.add("Presupuesto")
        self.crear_kiosco()
        self.crear_presupuesto()

        self.resumen = ctk.CTkLabel(
            self.ventana, text="",
            font=(FONT_MONO, 14, "bold"),
            text_color=NEON_YELLOW,
        )
        self.resumen.grid(row=3, column=0, pady=10)
        self.refrescar()

    def crear_header(self):
        header = ctk.CTkFrame(self.ventana, fg_color=BG_DARK)
        header.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 4))
        header.grid_columnconfigure(0, weight=1)

        # Título con efecto de "sombra" neón (dos labels superpuestos)
        contenedor_titulo = ctk.CTkFrame(header, fg_color=BG_DARK)
        contenedor_titulo.grid(row=0, column=0, sticky="w")
        
        # Placeholder invisible para reservar el espacio del título superpuesto
        placeholder = ctk.CTkLabel(
            contenedor_titulo,
            text="RecreoLab · ¿Qué comprás con tu presupuesto?",
            font=(FONT_MONO, 24, "bold"),
            text_color=BG_DARK,
        )
        placeholder.grid(row=0, column=0, padx=(0, 2), pady=2)

        sombra = ctk.CTkLabel(
            contenedor_titulo,
            text="RecreoLab · ¿Qué comprás con tu presupuesto?",
            font=(FONT_MONO, 24, "bold"),
            text_color=NEON_PINK,
        )
        sombra.place(x=2, y=2)

        titulo = ctk.CTkLabel(
            contenedor_titulo,
            text="RecreoLab · ¿Qué comprás con tu presupuesto?",
            font=(FONT_MONO, 24, "bold"),
            text_color=NEON_CYAN,
        )
        titulo.place(x=0, y=0)


        # Sol retro dibujado a mano con Canvas
        sol = tk.Canvas(header, width=140, height=90, bg=BG_DARK, highlightthickness=0)
        sol.grid(row=0, column=1, padx=8)
        self.dibujar_sol(sol)

    def dibujar_sol(self, canvas):
        cx, cy, r = 70, 45, 34
        # circulo de base
        canvas.create_oval(cx - r, cy - r, cx + r, cy + r, outline=NEON_PINK, width=3)
        # franjas horizontales "cortadas" en el sol (estilo synthwave)
        for i, y in enumerate(range(cy - 5, cy + r - 5, 8)):
            ancho = int((r ** 2 - (y - cy) ** 2) ** 0.5) if abs(y - cy) < r else 0
            canvas.create_line(cx - ancho, y, cx + ancho, y, fill=BG_DARK, width=4)
        # linea de horizonte
        canvas.create_line(4, cy + r + 8, 136, cy + r + 8, fill=NEON_CYAN, width=2)

    def crear_kiosco(self):
        panel = self.tabs.tab("Kiosco")
        panel.grid_columnconfigure((0, 1), weight=1)
        panel.grid_rowconfigure(0, weight=1)

        self.catalogo = ctk.CTkScrollableFrame(
            panel, label_text="Productos",
            fg_color=BG_PANEL,
            label_text_color=NEON_CYAN,
            label_fg_color=BG_DARK,
            border_width=2,
            border_color=NEON_PURPLE,
        )
        self.catalogo.grid(row=0, column=0, padx=8, pady=8, sticky="nsew")
        self.catalogo.grid_columnconfigure(0, weight=1)

        compra = ctk.CTkFrame(panel, fg_color=BG_PANEL, border_width=2, border_color=NEON_CYAN)
        compra.grid(row=0, column=1, padx=8, pady=8, sticky="nsew")
        compra.grid_columnconfigure(0, weight=1)
        compra.grid_rowconfigure(0, weight=1)

        self.detalle = ctk.CTkTextbox(
            compra, font=(FONT_MONO, 15),
            fg_color=BG_DARK, text_color=NEON_CYAN,
            border_width=2, border_color=NEON_PINK,
        )
        self.detalle.grid(row=0, column=0, padx=12, pady=12, sticky="nsew")

        self.total = ctk.CTkLabel(
            compra, text="", font=(FONT_MONO, 22, "bold"), text_color=NEON_YELLOW
        )
        self.total.grid(row=1, column=0, pady=8)

        acciones = [
            ("Quitar última unidad", self.quitar),
            ("Vaciar carrito", self.vaciar),
            ("Confirmar venta simulada", self.vender),
        ]
        for fila, (texto, accion) in enumerate(acciones, start=2):
            boton = ctk.CTkButton(
                compra, text=texto, command=accion, height=36,
                fg_color=BG_DARK, hover_color=NEON_PINK,
                text_color=TEXT_LIGHT, border_width=2, border_color=NEON_PINK,
                font=(FONT_MONO, 13, "bold"),
            )
            boton.grid(row=fila, column=0, padx=12, pady=5, sticky="ew")

    def crear_presupuesto(self):
        panel = self.tabs.tab("Presupuesto")
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(3, weight=1)

        aviso = ctk.CTkLabel(
            panel,
            text="Pares distintos: una unidad de cada producto.\n"
            "Consulta independiente; no reserva stock.",
            text_color=NEON_PURPLE, font=(FONT_MONO, 13),
        )
        aviso.grid(row=0, column=0, padx=12, pady=8)

        self.presupuesto = ctk.CTkEntry(
            panel, placeholder_text="Pesos enteros, sin puntos: 2000",
            fg_color=BG_PANEL, text_color=TEXT_LIGHT,
            border_color=NEON_CYAN, border_width=2,
            placeholder_text_color=NEON_PURPLE,
            font=(FONT_MONO, 13),
        )
        self.presupuesto.grid(row=1, column=0, padx=12, pady=8, sticky="ew")

        boton = ctk.CTkButton(
            panel, text="Buscar combinaciones", command=self.sugerir,
            fg_color=BG_DARK, hover_color=NEON_PURPLE,
            text_color=TEXT_LIGHT, border_width=2, border_color=NEON_CYAN,
            font=(FONT_MONO, 13, "bold"),
        )
        boton.grid(row=2, column=0, padx=12, pady=8)

        self.opciones = ctk.CTkTextbox(
            panel, font=(FONT_MONO, 15),
            fg_color=BG_DARK, text_color=NEON_CYAN,
            border_width=2, border_color=NEON_PURPLE,
        )
        self.opciones.grid(row=3, column=0, padx=12, pady=8, sticky="nsew")
        self.escribir(self.opciones, "Ingresá un presupuesto.")

    def escribir(self, caja, texto):
        caja.configure(state="normal")
        caja.delete("1.0", "end")
        caja.insert("1.0", texto)
        caja.configure(state="disabled")

    def refrescar(self):
        for widget in self.catalogo.winfo_children():
            widget.destroy()
        for fila, producto in enumerate(self.productos):
            estado = "Disponible"
            color_borde = NEON_CYAN
            if producto.stock == 0:
                estado = "Agotado"
                color_borde = "#555555"
            elif producto.stock <= 2:
                estado = "Reponer"
                color_borde = NEON_YELLOW
            texto = (f"{producto.nombre} · ${producto.precio}\n"
                     f"Stock: {producto.stock} | {estado} | +1")
            boton = ctk.CTkButton(
                self.catalogo, text=texto, height=64, anchor="w",
                command=partial(self.agregar_uno, producto.codigo),
                fg_color=BG_PANEL, hover_color=NEON_PINK,
                text_color=TEXT_LIGHT, border_width=2, border_color=color_borde,
                font=(FONT_MONO, 13),
            )
            boton.grid(row=fila, column=0, padx=8, pady=5, sticky="ew")
            if producto.stock == 0:
                boton.configure(state="disabled")
        lineas = ["CARRITO · una línea por unidad", ""]
        for producto in self.carrito:
            lineas.append(f"{producto.nombre}: ${producto.precio}")
        self.escribir(self.detalle, "\n".join(lineas))
        self.total.configure(text=f"Total: ${total_carrito(self.carrito)}")
        importe = sum(self.ventas)
        self.resumen.configure(
            text=f"Ventas de esta sesión: {len(self.ventas)} | Importe vendido: ${importe}"
        )

    def agregar_uno(self, codigo):
        try:
            agregar(self.productos, self.carrito, codigo)
        except ValueError as error:
            messagebox.showwarning("Revisá la compra", str(error), parent=self.ventana)
        self.refrescar()

    def quitar(self):
        if self.carrito:
            self.carrito.pop()
        self.refrescar()

    def vaciar(self):
        self.carrito.clear()
        self.refrescar()

    def vender(self):
        if not self.carrito:
            messagebox.showwarning("Carrito vacío", "Agregá un producto.", parent=self.ventana)
            return
        acepta = messagebox.askyesno("Confirmar", "¿Registrar esta venta simulada?", parent=self.ventana)
        if not acepta:
            return
        try:
            total = confirmar(self.carrito, self.ventas)
        except ValueError as error:
            messagebox.showerror("No se registró", str(error), parent=self.ventana)
            return
        self.refrescar()
        self.escribir(self.opciones, "Cambió el stock. Volvé a buscar combinaciones.")
        messagebox.showinfo(
            "Venta simulada registrada",
            f"Total: ${total}\nComprobante sin validez fiscal.",
            parent=self.ventana,
        )

    def sugerir(self):
        try:
            texto = self.presupuesto.get().strip()
            presupuesto = int(texto)
            if presupuesto > 1000000:
                raise ValueError("Usá hasta 1000000 pesos.")
            opciones = sugerir_pares(self.productos, presupuesto)
        except ValueError:
            messagebox.showwarning(
                "Presupuesto inválido",
                "Ingresá entre 1 y 1000000, sin puntos ni decimales.",
                parent=self.ventana,
            )
            return
        lineas = []
        for primero, segundo, total, sobra in opciones:
            lineas.append(f"{primero} + {segundo}: ${total} | Sobran ${sobra}")
        resultado = "\n".join(lineas) or "No hay pares disponibles."
        self.escribir(self.opciones, resultado)

    def ejecutar(self):
        self.ventana.mainloop()


if __name__ == "__main__":
    Aplicacion().ejecutar()
