import customtkinter as ctk
from tkinter import messagebox
from functools import partial
from modelo import (catalogo_inicial, agregar, confirmar, total_carrito, sugerir_pares)


# ---------- PALETA MINIMALISTA (estilo Apple) ----------
BG_MAIN = "#f5f5f7"        # fondo general, gris muy claro
BG_PANEL = "#ffffff"       # paneles blancos
BORDER = "#e5e5ea"         # bordes finos y sutiles
TEXT_PRIMARY = "#1d1d1f"   # texto principal, casi negro
TEXT_SECONDARY = "#86868b" # texto secundario, gris medio
ACCENT = "#007aff"         # azul de acento (único color fuerte)
ACCENT_HOVER = "#3395ff"
GREEN = "#34c759"
ORANGE = "#ff9f0a"
GRAY_DISABLED = "#c7c7cc"
FONT = "Segoe UI"


class Aplicacion:
    def __init__(self):
        self.productos = catalogo_inicial()
        self.carrito = []
        self.ventas = []
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.ventana = ctk.CTk()
        self.ventana.configure(fg_color=BG_MAIN)
        self.ventana.title("RecreoLab | Demostración escolar")
        self.ventana.geometry("1000x650")
        self.ventana.minsize(900, 600)
        self.ventana.grid_columnconfigure(0, weight=1)
        self.ventana.grid_rowconfigure(2, weight=1)

        self.crear_header()

        divisor = ctk.CTkFrame(self.ventana, fg_color=BORDER, height=1)
        divisor.grid(row=1, column=0, sticky="ew", padx=32, pady=(4, 0))

        self.tabs = ctk.CTkTabview(
            self.ventana,
            fg_color=BG_MAIN,
            segmented_button_fg_color=BG_MAIN,
            segmented_button_selected_color=BG_PANEL,
            segmented_button_selected_hover_color=BG_PANEL,
            segmented_button_unselected_color=BG_MAIN,
            segmented_button_unselected_hover_color=BG_MAIN,
            text_color=TEXT_SECONDARY,
            corner_radius=10,
        )
        self.tabs.grid(row=2, column=0, padx=32, pady=16, sticky="nsew")
        self.tabs.add("Kiosco")
        self.tabs.add("Presupuesto")
        self.crear_kiosco()
        self.crear_presupuesto()

        self.resumen = ctk.CTkLabel(
            self.ventana, text="",
            font=(FONT, 13), text_color=TEXT_SECONDARY,
        )
        self.resumen.grid(row=3, column=0, pady=(0, 14))
        self.refrescar()

    def crear_header(self):
        header = ctk.CTkFrame(self.ventana, fg_color=BG_MAIN)
        header.grid(row=0, column=0, sticky="ew", padx=32, pady=(28, 12))
        header.grid_columnconfigure(0, weight=1)

        titulo = ctk.CTkLabel(
            header, text="RecreoLab",
            font=(FONT, 30, "bold"), text_color=TEXT_PRIMARY,
        )
        titulo.grid(row=0, column=0, sticky="w")

        subtitulo = ctk.CTkLabel(
            header, text="¿Qué comprás con tu presupuesto?",
            font=(FONT, 15), text_color=TEXT_SECONDARY,
        )
        subtitulo.grid(row=1, column=0, sticky="w", pady=(2, 0))

    def crear_kiosco(self):
        panel = self.tabs.tab("Kiosco")
        panel.grid_columnconfigure((0, 1), weight=1)
        panel.grid_rowconfigure(0, weight=1)

        self.catalogo = ctk.CTkScrollableFrame(
            panel, label_text="Productos",
            fg_color=BG_PANEL,
            label_text_color=TEXT_PRIMARY,
            label_fg_color=BG_PANEL,
            corner_radius=14,
            border_width=1,
            border_color=BORDER,
        )
        self.catalogo.grid(row=0, column=0, padx=(0, 8), pady=8, sticky="nsew")
        self.catalogo.grid_columnconfigure(0, weight=1)

        compra = ctk.CTkFrame(
            panel, fg_color=BG_PANEL, corner_radius=14,
            border_width=1, border_color=BORDER,
        )
        compra.grid(row=0, column=1, padx=(8, 0), pady=8, sticky="nsew")
        compra.grid_columnconfigure(0, weight=1)
        compra.grid_rowconfigure(0, weight=1)

        self.detalle = ctk.CTkTextbox(
            compra, font=(FONT, 14),
            fg_color=BG_PANEL, text_color=TEXT_PRIMARY,
            corner_radius=10, border_width=1, border_color=BORDER,
        )
        self.detalle.grid(row=0, column=0, padx=16, pady=16, sticky="nsew")

        self.total = ctk.CTkLabel(
            compra, text="", font=(FONT, 22, "bold"), text_color=TEXT_PRIMARY
        )
        self.total.grid(row=1, column=0, pady=6)

        acciones = [
            ("Quitar última unidad", self.quitar, False),
            ("Vaciar carrito", self.vaciar, False),
            ("Confirmar venta simulada", self.vender, True),
        ]
        for fila, (texto, accion, es_principal) in enumerate(acciones, start=2):
            if es_principal:
                boton = ctk.CTkButton(
                    compra, text=texto, command=accion, height=38,
                    fg_color=ACCENT, hover_color=ACCENT_HOVER,
                    text_color="#ffffff", corner_radius=10,
                    font=(FONT, 13, "bold"),
                )
            else:
                boton = ctk.CTkButton(
                    compra, text=texto, command=accion, height=38,
                    fg_color=BG_PANEL, hover_color=BG_MAIN,
                    text_color=TEXT_PRIMARY, corner_radius=10,
                    border_width=1, border_color=BORDER,
                    font=(FONT, 13),
                )
            boton.grid(row=fila, column=0, padx=16, pady=5, sticky="ew")
        compra.grid_rowconfigure(4, minsize=10)

    def crear_presupuesto(self):
        panel = self.tabs.tab("Presupuesto")
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(3, weight=1)

        aviso = ctk.CTkLabel(
            panel,
            text="Pares distintos: una unidad de cada producto.\n"
            "Consulta independiente; no reserva stock.",
            text_color=TEXT_SECONDARY, font=(FONT, 13), justify="left",
        )
        aviso.grid(row=0, column=0, padx=4, pady=(4, 10), sticky="w")

        self.presupuesto = ctk.CTkEntry(
            panel, placeholder_text="Pesos enteros, sin puntos: 2000",
            fg_color=BG_PANEL, text_color=TEXT_PRIMARY,
            border_color=BORDER, border_width=1,
            placeholder_text_color=TEXT_SECONDARY,
            corner_radius=10, height=38,
            font=(FONT, 13),
        )
        self.presupuesto.grid(row=1, column=0, padx=4, pady=8, sticky="ew")

        boton = ctk.CTkButton(
            panel, text="Buscar combinaciones", command=self.sugerir,
            fg_color=ACCENT, hover_color=ACCENT_HOVER,
            text_color="#ffffff", corner_radius=10, height=38,
            font=(FONT, 13, "bold"),
        )
        boton.grid(row=2, column=0, padx=4, pady=(4, 12), sticky="w")

        self.opciones = ctk.CTkTextbox(
            panel, font=(FONT, 14),
            fg_color=BG_PANEL, text_color=TEXT_PRIMARY,
            corner_radius=14, border_width=1, border_color=BORDER,
        )
        self.opciones.grid(row=3, column=0, padx=4, pady=(0, 4), sticky="nsew")
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
            color_estado = GREEN
            if producto.stock == 0:
                estado = "Agotado"
                color_estado = GRAY_DISABLED
            elif producto.stock <= 2:
                estado = "Reponer"
                color_estado = ORANGE

            tarjeta = ctk.CTkFrame(
                self.catalogo, fg_color=BG_MAIN, corner_radius=10,
                border_width=1, border_color=BORDER,
            )
            tarjeta.grid(row=fila, column=0, padx=6, pady=5, sticky="ew")
            tarjeta.grid_columnconfigure(0, weight=1)

            nombre = ctk.CTkLabel(
                tarjeta, text=f"{producto.nombre}  ·  ${producto.precio}",
                font=(FONT, 14, "bold"), text_color=TEXT_PRIMARY, anchor="w",
            )
            nombre.grid(row=0, column=0, padx=14, pady=(10, 0), sticky="w")

            detalle_fila = ctk.CTkFrame(tarjeta, fg_color=BG_MAIN)
            detalle_fila.grid(row=1, column=0, padx=14, pady=(0, 4), sticky="ew")

            punto = ctk.CTkLabel(
                detalle_fila, text="●", text_color=color_estado, font=(FONT, 11),
            )
            punto.grid(row=0, column=0, sticky="w")

            estado_label = ctk.CTkLabel(
                detalle_fila, text=f" {estado}  ·  Stock: {producto.stock}",
                font=(FONT, 12), text_color=TEXT_SECONDARY,
            )
            estado_label.grid(row=0, column=1, sticky="w")

            boton = ctk.CTkButton(
                tarjeta, text="+1", width=44, height=44,
                command=partial(self.agregar_uno, producto.codigo),
                fg_color=ACCENT, hover_color=ACCENT_HOVER,
                text_color="#ffffff", corner_radius=22,
                font=(FONT, 14, "bold"),
            )
            boton.grid(row=0, column=1, rowspan=2, padx=14, pady=10)
            tarjeta.grid_columnconfigure(1, weight=0)

            if producto.stock == 0:
                boton.configure(state="disabled", fg_color=GRAY_DISABLED)

        lineas = ["Carrito", ""]
        for producto in self.carrito:
            lineas.append(f"{producto.nombre}   ${producto.precio}")
        self.escribir(self.detalle, "\n".join(lineas))
        self.total.configure(text=f"Total: ${total_carrito(self.carrito)}")
        importe = sum(self.ventas)
        self.resumen.configure(
            text=f"Ventas de esta sesión: {len(self.ventas)}   ·   Importe vendido: ${importe}"
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
            lineas.append(f"{primero} + {segundo}: ${total}   ·   Sobran ${sobra}")
        resultado = "\n".join(lineas) or "No hay pares disponibles."
        self.escribir(self.opciones, resultado)

    def ejecutar(self):
        self.ventana.mainloop()


if __name__ == "__main__":
    Aplicacion().ejecutar()
