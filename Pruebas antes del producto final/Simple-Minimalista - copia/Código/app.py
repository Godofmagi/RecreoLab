import customtkinter as ctk
from tkinter import messagebox
from functools import partial
from itertools import combinations
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageOps
from pathlib import Path
from modelo import catalogo_inicial, agregar, confirmar, total_carrito, cantidad_en_carrito


#Colores para la interfaz
BG = "#F5F5F7"
CARD = "#FFFFFF"
CARD_SOFT = "#FAFAFC"
CARD_MUTED = "#F2F2F5"
TEXT = "#1D1D1F"
TEXT_SECONDARY = "#6E6E73"
BORDER = "#E5E5EA"
ACCENT = "#0071E3"
ACCENT_HOVER = "#0077ED"
SUCCESS = "#248A3D"
WARNING = "#B26A00"
DANGER = "#D70015"
DANGER_SOFT = "#FFF1F1"
DISABLED = "#D2D2D7"
BLACK_BUTTON = "#1D1D1F"
BLACK_BUTTON_HOVER = "#343437"
GREEN_SOFT = "#EEF8EE"
BLUE_SOFT = "#EAF4FF"
ORANGE_SOFT = "#FFF3E8"
PURPLE_SOFT = "#F4EFFE"
PINK_SOFT = "#FFF0F5"
BROWN_SOFT = "#F8EFE7"

FONT = "Segoe UI"

PRODUCT_STYLES = {
    "Agua SmartWater": {"bg": BLUE_SOFT, "fg": ACCENT, "category": "Bebida"},
    "Jugo": {"bg": ORANGE_SOFT, "fg": "#D96B00", "category": "Bebida"},
    "Alfajor": {"bg": BROWN_SOFT, "fg": "#8A5B33", "category": "Snack"},
    "Galletitas": {"bg": PURPLE_SOFT, "fg": "#6F42C1", "category": "Snack"},
    "Barrita": {"bg": GREEN_SOFT, "fg": "#3F8F4F", "category": "Energía"},
    "Caramelos": {"bg": PINK_SOFT, "fg": "#C03B80", "category": "Dulce"},
}


PRODUCT_IMAGE_FILES = {
    "Agua SmartWater": "agua",
    "Jugo": "jugo",
    "Alfajor": "alfajor",
    "Galletitas": "galletitas",
    "Barrita": "barrita",
    "Caramelos": "caramelos",
}


PRODUCT_IMAGE_DISPLAY_SIZE = (112, 112)
PRODUCT_IMAGE_CANVAS_SIZE = (256, 256)
PRODUCT_IMAGE_MARGIN = 18


class Aplicacion:
    def __init__(self):
        self.productos = catalogo_inicial()
        self.carrito = []
        self.ventas = []
        self.historial_ventas = []
        self.ranking_productos = {}
        self.vista_actual = "inicio"
        self.imagenes_producto = {}
        self.nav_buttons = {}
        self.preview_labels = []
        self.preview_offset = 0
        self.logo_image = None
        self.touch_widgets = {}


        self.base_dir = Path(__file__).resolve().parent
        self.assets_dir = self.base_dir / "assets" / "productos"

        print("\n================ RECREOLAB ================")
        print(f"[APP REAL] {Path(__file__).resolve()}")
        print(f"[CARPETA DE FOTOS] {self.assets_dir}")
        print("============================================\n")

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.ventana = ctk.CTk(fg_color=BG)
        self.ventana.title("RecreoLab Minimalista")
        self.ventana.geometry("1280x800")
        self.ventana.minsize(1120, 720)
        self.ventana.grid_columnconfigure(0, weight=1)
        self.ventana.grid_rowconfigure(0, weight=1)
        self.ventana.iconbitmap(self.base_dir / "assets" / "logo.ico")

        self.contenedor = ctk.CTkScrollableFrame(self.ventana, fg_color=BG, corner_radius=0)
        self.contenedor.grid(row=0, column=0, sticky="nsew")
        self.contenedor.grid_columnconfigure(0, weight=1)
        

        self.busqueda_var = ctk.StringVar(master=self.ventana, value="")
        self.categoria_var = ctk.StringVar(master=self.ventana, value="Todos")
        self.touch_var = ctk.BooleanVar(master=self.ventana, value=False)

        self.crear_imagenes_producto()
        self.crear_logo()
        self.crear_encabezado()
        self.crear_cuerpo()
        self.crear_footer()
        self.cambiar_vista("inicio")
        self.refrescar()
        self.rotar_preview()

    # Recursos visuales
    def crear_imagenes_producto(self):
    
        archivos = {
            "Agua SmartWater": "agua.png",
            "Jugo": "jugo.png",
            "Alfajor": "alfajor.png",
            "Galletitas": "galletitas.png",
            "Barrita": "barrita.png",
            "Caramelos": "caramelos.png",
            
        }

        faltantes = []
        for nombre, archivo in archivos.items():
            ruta = self.assets_dir / archivo
            if not ruta.is_file():
                faltantes.append(str(ruta))

        if faltantes:
            mensaje = "NO ENCONTRE ESTAS FOTOS:\n\n" + "\n".join(faltantes)
            print(mensaje)
            raise FileNotFoundError(mensaje)

        for producto in self.productos:
            ruta = self.assets_dir / archivos[producto.nombre]
            image = self.preparar_imagen_producto(ruta)
            self.imagenes_producto[producto.codigo] = ctk.CTkImage(
                light_image=image,
                dark_image=image,
                size=PRODUCT_IMAGE_DISPLAY_SIZE,
            )
            

    def preparar_imagen_producto(self, ruta):
        
        with Image.open(ruta) as original:
            original = ImageOps.exif_transpose(original).convert("RGBA")

            canvas_w, canvas_h = PRODUCT_IMAGE_CANVAS_SIZE
            max_w = canvas_w - (PRODUCT_IMAGE_MARGIN * 2)
            max_h = canvas_h - (PRODUCT_IMAGE_MARGIN * 2)

            ajustada = ImageOps.contain(
                original,
                (max_w, max_h),
                method=Image.Resampling.LANCZOS,
            )

            # Fondo blanco uniforme para que fotos con distintos formatos
            # mantengan exactamente el mismo cuadro visual.
            canvas = Image.new("RGBA", PRODUCT_IMAGE_CANVAS_SIZE, (255, 255, 255, 255))
            x = (canvas_w - ajustada.width) // 2
            y = (canvas_h - ajustada.height) // 2
            canvas.alpha_composite(ajustada, (x, y))
            return canvas

    def crear_logo(self):
        ruta_logo = self.base_dir / "assets" / "logo.png"

        imagen = Image.open(ruta_logo)
        imagen = ImageOps.exif_transpose(imagen).convert("RGBA")

        # Trabajamos en alta resolución
        canvas_size = 400

        imagen = ImageOps.contain(
            imagen,
            (canvas_size, canvas_size),
            method=Image.Resampling.LANCZOS,
        )

        canvas = Image.new(
            "RGBA",
            (canvas_size, canvas_size),
            (255, 255, 255, 0),
        )

        x = (canvas_size - imagen.width) // 2
        y = (canvas_size - imagen.height) // 2

        canvas.alpha_composite(imagen, (x, y))

        self.logo_image = ctk.CTkImage(
            light_image=canvas,
            dark_image=canvas,
            size=(150, 150),
        )

    # Layout principal
    def crear_encabezado(self):
        self.header = ctk.CTkFrame(
            self.contenedor,
            fg_color=CARD,
            corner_radius=24,
            border_width=1,
            border_color=BORDER,
        )
        self.header.grid(row=0, column=0, padx=24, pady=(20, 10), sticky="ew")
        self.header.grid_columnconfigure(0, weight=1)
        self.header.grid_columnconfigure(1, weight=0)

        marca_wrap = ctk.CTkFrame(self.header, fg_color="transparent")
        marca_wrap.grid(row=0, column=0, padx=24, pady=18, sticky="w")
        marca_wrap.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(marca_wrap, text="", image=self.logo_image).grid(
            row=0, column=0, rowspan=3, padx=(0, 14), sticky="w"
        )

        ctk.CTkLabel(
            marca_wrap,
            text="RECREOLAB minimalista",
            font=(FONT, 12, "bold"),
            text_color=ACCENT,
        ).grid(row=0, column=1, sticky="w")

        ctk.CTkLabel(
            marca_wrap,
            text="Kiosco virtual",
            font=(FONT, 30, "bold"),
            text_color=TEXT,
        ).grid(row=1, column=1, pady=(3, 1), sticky="w")

        ctk.CTkLabel(
            marca_wrap,
            text="Bienvenido a nuestro kiosco virtual. Explora, compra y disfruta de nuestros productos.",
            font=(FONT, 14),
            text_color=TEXT_SECONDARY,
        ).grid(row=2, column=1, sticky="w")

        nav = ctk.CTkFrame(
            self.header,
            fg_color=CARD_MUTED,
            corner_radius=18,
            border_width=1,
            border_color=BORDER,
        )
        nav.grid(row=0, column=1, padx=24, pady=20, sticky="e")

        botones = [
            ("inicio", "Inicio"),
            ("kiosco", "Kiosco"),
            ("presupuesto", "Presupuesto"),
            ("reportes", "Reportes"),
        ]
        for columna, (clave, texto) in enumerate(botones):
            boton = ctk.CTkButton(
                nav,
                text=texto,
                width=138,
                height=42,
                corner_radius=14,
                border_width=0,
                fg_color="transparent",
                hover_color="#EBEBEF",
                text_color=TEXT_SECONDARY,
                font=(FONT, 13, "bold"),
                command=partial(self.cambiar_vista, clave),
            )
            boton.grid(row=0, column=columna, padx=5, pady=5)
            self.nav_buttons[clave] = boton
            self.touch_widgets[boton] = {
                "normal": {"width": 138, "height": 42, "font": (FONT, 13, "bold")},
                "touch": {"width": 170, "height": 56, "font": (FONT, 15, "bold")},
            }

    def crear_cuerpo(self):
        self.body = ctk.CTkFrame(self.contenedor, fg_color="transparent")
        self.body.grid(row=1, column=0, padx=24, pady=(2, 8), sticky="nsew")
        self.body.grid_columnconfigure(0, weight=1)
        self.body.grid_rowconfigure(0, weight=1)

        self.frame_inicio = ctk.CTkFrame(self.body, fg_color="transparent")
        self.frame_inicio.grid(row=0, column=0, sticky="nsew")
        self.frame_inicio.grid_columnconfigure(0, weight=3)
        self.frame_inicio.grid_columnconfigure(1, weight=2)
        self.frame_inicio.grid_rowconfigure(0, weight=1)

        self.frame_kiosco = ctk.CTkFrame(self.body, fg_color="transparent")
        self.frame_kiosco.grid(row=0, column=0, sticky="nsew")
        self.frame_kiosco.grid_columnconfigure(0, weight=7)
        self.frame_kiosco.grid_columnconfigure(1, weight=4)
        self.frame_kiosco.grid_rowconfigure(0, weight=1)

        self.frame_presupuesto = ctk.CTkFrame(self.body, fg_color="transparent")
        self.frame_presupuesto.grid(row=0, column=0, sticky="nsew")
        self.frame_presupuesto.grid_columnconfigure(0, weight=3)
        self.frame_presupuesto.grid_columnconfigure(1, weight=2)
        self.frame_presupuesto.grid_rowconfigure(0, weight=1)

        self.frame_reportes = ctk.CTkFrame(self.body, fg_color="transparent")
        self.frame_reportes.grid(row=0, column=0, sticky="nsew")
        self.frame_reportes.grid_columnconfigure(0, weight=1)
        self.frame_reportes.grid_rowconfigure(0, weight=1)

        self.crear_inicio()
        self.crear_kiosco()
        self.crear_presupuesto()
        self.crear_reportes()

    def crear_footer(self):
        footer = ctk.CTkFrame(
            self.contenedor,
            fg_color=CARD,
            corner_radius=18,
            border_width=1,
            border_color=BORDER,
        )
        footer.grid(row=2, column=0, padx=24, pady=(2, 22), sticky="ew")
        footer.grid_columnconfigure(0, weight=1)

        self.resumen = ctk.CTkLabel(
            footer,
            text="",
            font=(FONT, 13),
            text_color=TEXT_SECONDARY,
        )
        self.resumen.grid(row=0, column=0, padx=18, pady=12, sticky="w")

    def cambiar_vista(self, vista):
        self.vista_actual = vista
        self.frame_inicio.grid_remove()
        self.frame_kiosco.grid_remove()
        self.frame_presupuesto.grid_remove()
        self.frame_reportes.grid_remove()

        if vista == "inicio":
            self.frame_inicio.grid()
        elif vista == "kiosco":
            self.frame_kiosco.grid()
        elif vista == "presupuesto":
            self.frame_presupuesto.grid()
        else:
            self.frame_reportes.grid()

        for clave, boton in self.nav_buttons.items():
            if clave == vista:
                boton.configure(fg_color=CARD, hover_color=CARD, text_color=TEXT)
            else:
                boton.configure(fg_color="transparent", hover_color="#EBEBEF", text_color=TEXT_SECONDARY)

    # Pantalla de Inicio 
    def crear_inicio(self):
        hero = ctk.CTkFrame(
            self.frame_inicio,
            fg_color=CARD,
            corner_radius=28,
            border_width=1,
            border_color=BORDER,
        )
        hero.grid(row=0, column=0, padx=(0, 10), pady=8, sticky="nsew")
        hero.grid_columnconfigure(0, weight=1)

        badge = ctk.CTkFrame(hero, fg_color=BLUE_SOFT, corner_radius=18)
        badge.grid(row=0, column=0, padx=28, pady=(28, 16), sticky="w")
        ctk.CTkLabel(
            badge,
            text="Un kiosco virtual en tu pantalla",
            font=(FONT, 12, "bold"),
            text_color=ACCENT,
        ).grid(row=0, column=0, padx=14, pady=8)

        ctk.CTkLabel(
            hero,
            text="Vendé más simple.",
            font=(FONT, 38, "bold"),
            text_color=TEXT,
        ).grid(row=1, column=0, padx=28, sticky="w")

        ctk.CTkLabel(
            hero,
            text="Una simulación de un kiosco que te permite vender, consultar y decidir rápido.",
            font=(FONT, 16),
            text_color=TEXT_SECONDARY,
            justify="left",
            wraplength=560,
        ).grid(row=2, column=0, padx=28, pady=(8, 18), sticky="w")

        acciones = ctk.CTkFrame(hero, fg_color="transparent")
        acciones.grid(row=3, column=0, padx=28, pady=(0, 18), sticky="w")

        boton_explorar = ctk.CTkButton(
            acciones,
            text="Explorar kiosco",
            command=partial(self.cambiar_vista, "kiosco"),
            width=180,
            height=46,
            corner_radius=14,
            fg_color=BLACK_BUTTON,
            hover_color=BLACK_BUTTON_HOVER,
            text_color="white",
            font=(FONT, 14, "bold"),
        )
        boton_explorar.grid(row=0, column=0, padx=(0, 10))
        self.touch_widgets[boton_explorar] = {
            "normal": {"width": 180, "height": 46, "font": (FONT, 14, "bold")},
            "touch": {"width": 220, "height": 60, "font": (FONT, 16, "bold")},
        }

        boton_presupuesto_home = ctk.CTkButton(
            acciones,
            text="Abrir presupuesto",
            command=partial(self.cambiar_vista, "presupuesto"),
            width=180,
            height=46,
            corner_radius=14,
            fg_color=CARD_MUTED,
            hover_color="#E8E8ED",
            text_color=TEXT,
            font=(FONT, 14, "bold"),
        )
        boton_presupuesto_home.grid(row=0, column=1, padx=(0, 10))
        self.touch_widgets[boton_presupuesto_home] = {
            "normal": {"width": 180, "height": 46, "font": (FONT, 14, "bold")},
            "touch": {"width": 220, "height": 60, "font": (FONT, 16, "bold")},
        }

        touch_wrap = ctk.CTkFrame(acciones, fg_color=CARD_MUTED, corner_radius=13)
        touch_wrap.grid(row=0, column=2)
        ctk.CTkLabel(
            touch_wrap, text="Modo touch", font=(FONT, 12, "bold"), text_color=TEXT_SECONDARY
        ).grid(row=0, column=0, padx=(12, 5), pady=10)
        ctk.CTkSwitch(
            touch_wrap,
            text="",
            variable=self.touch_var,
            command=self.refrescar,
            width=38,
            button_color=CARD,
            button_hover_color=CARD,
            progress_color=ACCENT,
        ).grid(row=0, column=1, padx=(0, 8), pady=8)

        highlights = ctk.CTkFrame(hero, fg_color="transparent")
        highlights.grid(row=4, column=0, padx=28, pady=(2, 22), sticky="ew")
        highlights.grid_columnconfigure((0, 1, 2), weight=1)

        self.home_chip_productos = self.crear_chip_inicio(highlights, 0, "Productos", "0")
        self.home_chip_stock = self.crear_chip_inicio(highlights, 1, "Stock", "0")
        self.home_chip_ventas = self.crear_chip_inicio(highlights, 2, "Ventas", "0")

        features = ctk.CTkFrame(hero, fg_color=CARD_SOFT, corner_radius=20, border_width=1, border_color=BORDER)
        features.grid(row=5, column=0, padx=28, pady=(0, 28), sticky="ew")
        features.grid_columnconfigure((0, 1), weight=1)

        textos = [
            ("Navegación clara", "Inicio, kiosco y presupuesto separados para una experiencia más prolija."),
            ("Tarjetas visuales", "Cada producto se ve como una card con miniatura, stock y precio."),
            ("Venta rápida", "Confirmás compras y seguís el total en tiempo real."),
            ("Presupuesto inteligente", "Podés ver combinaciones posibles de productos disponibles."),
        ]
        for idx, (titulo, descripcion) in enumerate(textos):
            col = idx % 2
            row = idx // 2
            block = ctk.CTkFrame(features, fg_color="transparent")
            block.grid(row=row, column=col, padx=18, pady=16, sticky="nsew")
            ctk.CTkLabel(block, text=titulo, font=(FONT, 14, "bold"), text_color=TEXT).grid(row=0, column=0, sticky="w")
            ctk.CTkLabel(
                block,
                text=descripcion,
                font=(FONT, 13),
                text_color=TEXT_SECONDARY,
                justify="left",
                wraplength=260,
            ).grid(row=1, column=0, pady=(4, 0), sticky="w")

        side = ctk.CTkFrame(
            self.frame_inicio,
            fg_color=CARD,
            corner_radius=28,
            border_width=1,
            border_color=BORDER,
        )
        side.grid(row=0, column=1, padx=(10, 0), pady=8, sticky="nsew")
        side.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(side, text="Vista previa", font=(FONT, 22, "bold"), text_color=TEXT).grid(
            row=0, column=0, padx=22, pady=(22, 4), sticky="w"
        )
        ctk.CTkLabel(
            side,
            text="Estos son algunos de nuestros productos:",
            font=(FONT, 13),
            text_color=TEXT_SECONDARY,
        ).grid(row=1, column=0, padx=22, pady=(0, 12), sticky="w")

        preview = ctk.CTkFrame(side, fg_color=CARD_SOFT, corner_radius=20, border_width=1, border_color=BORDER)
        preview.grid(row=2, column=0, padx=20, pady=(0, 16), sticky="ew")
        preview.grid_columnconfigure(0, weight=1)

        for idx in range(4):
            fila = ctk.CTkFrame(preview, fg_color="transparent")
            fila.grid(row=idx, column=0, padx=14, pady=10, sticky="ew")
            fila.grid_columnconfigure(1, weight=1)
            thumb = ctk.CTkLabel(fila, text="", width=32, height=32, fg_color="#F0F0F2", corner_radius=16)
            thumb.grid(row=0, column=0, padx=(0, 12))
            label = ctk.CTkLabel(fila, text="", font=(FONT, 13), text_color=TEXT, anchor="w")
            label.grid(row=0, column=1, sticky="w")
            self.preview_labels.append((thumb, label))

        box_quote = ctk.CTkFrame(side, fg_color=BLUE_SOFT, corner_radius=20)
        box_quote.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")
        ctk.CTkLabel(
            box_quote,
            text='Traido a ustedes por:',
            font=(FONT, 14, "bold"),
            text_color=TEXT,
            justify="left",
            wraplength=300,
        ).grid(row=0, column=0, padx=18, pady=(16, 6), sticky="w")
        ctk.CTkLabel(
            box_quote,
            text="Nombres y apellidos de los integrantes del grupo.",
            font=(FONT, 13),
            text_color=TEXT_SECONDARY,
            justify="left",
            wraplength=300,
        ).grid(row=1, column=0, padx=18, pady=(0, 16), sticky="w")

    def crear_chip_inicio(self, parent, column, titulo, valor):
        chip = ctk.CTkFrame(parent, fg_color=CARD_SOFT, corner_radius=18, border_width=1, border_color=BORDER)
        chip.grid(row=0, column=column, padx=(0 if column == 0 else 8, 0), sticky="ew")
        chip.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(chip, text=titulo, font=(FONT, 11, "bold"), text_color=TEXT_SECONDARY).grid(
            row=0, column=0, padx=16, pady=(14, 2), sticky="w"
        )
        value = ctk.CTkLabel(chip, text=valor, font=(FONT, 24, "bold"), text_color=TEXT)
        value.grid(row=1, column=0, padx=16, pady=(0, 14), sticky="w")
        chip.value_label = value
        return chip

    # Pantalla del Kiosco 
    def crear_kiosco(self):
        catalogo_card = ctk.CTkFrame(
            self.frame_kiosco,
            fg_color=CARD,
            corner_radius=24,
            border_width=1,
            border_color=BORDER,
        )
        catalogo_card.grid(row=0, column=0, padx=(0, 10), pady=8, sticky="nsew")
        catalogo_card.grid_columnconfigure(0, weight=1)
        catalogo_card.grid_rowconfigure(3, weight=1)

        top = ctk.CTkFrame(catalogo_card, fg_color="transparent")
        top.grid(row=0, column=0, padx=22, pady=(22, 10), sticky="ew")
        top.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(top, text="Lista de Productos", font=(FONT, 22, "bold"), text_color=TEXT).grid(
            row=0, column=0, sticky="w"
        )
        ctk.CTkLabel(
            top,
            text="Estos son los productos que ofrecemos, mostrando su cantidad disponible y su precio.",
            font=(FONT, 13),
            text_color=TEXT_SECONDARY,
        ).grid(row=1, column=0, pady=(2, 0), sticky="w")

        chips = ctk.CTkFrame(top, fg_color="transparent")
        chips.grid(row=0, column=1, rowspan=2, sticky="e")
        self.chip_productos = self.crear_chip_horizontal(chips, 0, "Productos", "0")
        self.chip_stock = self.crear_chip_horizontal(chips, 1, "Stock total", "0")

        filtros = ctk.CTkFrame(catalogo_card, fg_color="transparent")
        filtros.grid(row=1, column=0, padx=22, pady=(0, 12), sticky="ew")
        filtros.grid_columnconfigure(0, weight=1)

        self.buscador = ctk.CTkEntry(
            filtros,
            textvariable=self.busqueda_var,
            placeholder_text="Buscar producto...",
            height=42,
            corner_radius=13,
            fg_color=CARD_SOFT,
            border_color=BORDER,
            text_color=TEXT,
            placeholder_text_color="#9A9AA0",
            font=(FONT, 13),
        )
        self.buscador.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.buscador.bind("<KeyRelease>", lambda _event: self.refrescar())
        self.touch_widgets[self.buscador] = {
            "normal": {"height": 42, "font": (FONT, 13)},
            "touch": {"height": 54, "font": (FONT, 15)},
        }

        self.categorias = ctk.CTkSegmentedButton(
            filtros,
            values=["Todos", "Bebida", "Snack", "Energía", "Dulce"],
            variable=self.categoria_var,
            command=lambda _value: self.refrescar(),
            height=40,
            corner_radius=12,
            selected_color=TEXT,
            selected_hover_color=TEXT,
            unselected_color=CARD_MUTED,
            unselected_hover_color="#E8E8ED",
            text_color=TEXT,
            font=(FONT, 12, "bold"),
        )
        self.categorias.grid(row=0, column=1, padx=(0, 10))
        self.touch_widgets[self.categorias] = {
            "normal": {"height": 40, "font": (FONT, 12, "bold")},
            "touch": {"height": 52, "font": (FONT, 14, "bold")},
        }

        self.catalogo = ctk.CTkScrollableFrame(
            catalogo_card,
            fg_color="transparent",
            scrollbar_button_color="#C7C7CC",
            scrollbar_button_hover_color="#AEAEB2",
        )
        self.catalogo.grid(row=3, column=0, padx=14, pady=(0, 14), sticky="nsew")
        self.catalogo.grid_columnconfigure((0, 1), weight=1)

        compra = ctk.CTkFrame(
            self.frame_kiosco,
            fg_color=CARD,
            corner_radius=24,
            border_width=1,
            border_color=BORDER,
        )
        compra.grid(row=0, column=1, padx=(10, 0), pady=8, sticky="nsew")
        compra.grid_columnconfigure(0, weight=1)
        compra.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(compra, text="Tu compra", font=(FONT, 22, "bold"), text_color=TEXT).grid(
            row=0, column=0, padx=22, pady=(22, 2), sticky="w"
        )

        self.estado_carrito = ctk.CTkLabel(compra, text="", font=(FONT, 13), text_color=TEXT_SECONDARY)
        self.estado_carrito.grid(row=1, column=0, padx=22, pady=(0, 12), sticky="w")

        self.metricas_compra = ctk.CTkFrame(compra, fg_color="transparent")
        self.metricas_compra.grid(row=2, column=0, padx=20, pady=(0, 12), sticky="ew")
        self.metricas_compra.grid_columnconfigure((0, 1), weight=1)
        self.chip_items = self.crear_chip_horizontal(self.metricas_compra, 0, "Items", "0", wide=True)
        self.chip_ticket = self.crear_chip_horizontal(self.metricas_compra, 1, "Ticket", self.moneda(0), wide=True)
        

        self.detalle = ctk.CTkTextbox(
            compra,
            font=(FONT, 14),
            fg_color=CARD_SOFT,
            text_color=TEXT,
            border_width=1,
            border_color=BORDER,
            corner_radius=16,
            wrap="word",
            activate_scrollbars=True,
        )
        self.detalle.grid(row=3, column=0, padx=20, pady=(0, 14), sticky="nsew")

        total_box = ctk.CTkFrame(compra, fg_color="transparent")
        total_box.grid(row=4, column=0, padx=22, pady=(0, 10), sticky="ew")
        total_box.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(total_box, text="Total actual", font=(FONT, 13), text_color=TEXT_SECONDARY).grid(
            row=0, column=0, sticky="w"
        )
        self.total = ctk.CTkLabel(total_box, text=self.moneda(0), font=(FONT, 30, "bold"), text_color=TEXT)
        self.total.grid(row=1, column=0, sticky="w")

        self.boton_vender = ctk.CTkButton(
            compra,
            text="Confirmar venta",
            command=self.vender,
            height=46,
            corner_radius=14,
            fg_color=BLACK_BUTTON,
            hover_color=BLACK_BUTTON_HOVER,
            text_color="white",
            font=(FONT, 14, "bold"),
        )
        self.boton_vender.grid(row=5, column=0, padx=20, pady=(0, 10), sticky="ew")
        self.touch_widgets[self.boton_vender] = {
            "normal": {"height": 46, "font": (FONT, 14, "bold")},
            "touch": {"height": 60, "font": (FONT, 16, "bold")},
        }

        acciones = ctk.CTkFrame(compra, fg_color="transparent")
        acciones.grid(row=6, column=0, padx=20, pady=(0, 20), sticky="ew")
        acciones.grid_columnconfigure((0, 1), weight=1)

        boton_quitar = ctk.CTkButton(
            acciones,
            text="Quitar última",
            command=self.quitar,
            height=40,
            corner_radius=12,
            fg_color="#ECECF0",
            hover_color="#E1E1E6",
            text_color=TEXT,
            font=(FONT, 13, "bold"),
        )
        boton_quitar.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        self.touch_widgets[boton_quitar] = {
            "normal": {"height": 40, "font": (FONT, 13, "bold")},
            "touch": {"height": 54, "font": (FONT, 15, "bold")},
        }

        boton_vaciar = ctk.CTkButton(
            acciones,
            text="Vaciar carrito",
            command=self.vaciar,
            height=40,
            corner_radius=12,
            fg_color=DANGER_SOFT,
            hover_color="#FFE2E2",
            text_color=DANGER,
            font=(FONT, 13, "bold"),
        )
        boton_vaciar.grid(row=0, column=1, padx=(5, 0), sticky="ew")
        self.touch_widgets[boton_vaciar] = {
            "normal": {"height": 40, "font": (FONT, 13, "bold")},
            "touch": {"height": 54, "font": (FONT, 15, "bold")},
        }

    def crear_chip_horizontal(self, parent, column, titulo, valor, wide=False):
        chip = ctk.CTkFrame(
            parent,
            fg_color=CARD_MUTED,
            corner_radius=16,
            border_width=1,
            border_color=BORDER,
            width=170 if wide else 128,
        )
        chip.grid(row=0, column=column, padx=(0 if column == 0 else 8, 0), sticky="ew")
        chip.grid_columnconfigure(0, weight=1)

        titulo_lbl = ctk.CTkLabel(chip, text=titulo, font=(FONT, 11, "bold"), text_color=TEXT_SECONDARY)
        titulo_lbl.grid(row=0, column=0, padx=14, pady=(12, 2), sticky="w")

        valor_lbl = ctk.CTkLabel(chip, text=valor, font=(FONT, 18, "bold"), text_color=TEXT)
        valor_lbl.grid(row=1, column=0, padx=14, pady=(0, 12), sticky="w")

        chip.value_label = valor_lbl
        return chip
    
    def actualizar_texto_categorias(self):
        seleccionada = self.categoria_var.get()
        for valor, boton in self.categorias._buttons_dict.items():
            if valor == seleccionada:
                boton.configure(text_color="white")
            else:
                boton.configure(text_color=TEXT)

    # Pantalla del Presupuesto 
    def crear_presupuesto(self):
        izquierda = ctk.CTkFrame(
            self.frame_presupuesto,
            fg_color=CARD,
            corner_radius=24,
            border_width=1,
            border_color=BORDER,
        )
        izquierda.grid(row=0, column=0, padx=(0, 10), pady=8, sticky="nsew")
        izquierda.grid_columnconfigure(0, weight=1)
        izquierda.grid_rowconfigure(5, weight=1)

        ctk.CTkLabel(izquierda, text="¿Qué podés comprar?", font=(FONT, 26, "bold"), text_color=TEXT).grid(
            row=0, column=0, padx=26, pady=(24, 4), sticky="w"
        )
        ctk.CTkLabel(
            izquierda,
            text="Ingresá tu presupuesto y te mostramos combinaciones posibles de productos distintos.",
            font=(FONT, 14),
            text_color=TEXT_SECONDARY,
        ).grid(row=1, column=0, padx=26, pady=(0, 18), sticky="w")

        campo_wrap = ctk.CTkFrame(
            izquierda,
            fg_color=CARD_SOFT,
            corner_radius=18,
            border_width=1,
            border_color=BORDER,
        )
        campo_wrap.grid(row=2, column=0, padx=26, pady=(0, 14), sticky="ew")
        campo_wrap.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(campo_wrap, text="Presupuesto disponible", font=(FONT, 12, "bold"), text_color=TEXT_SECONDARY).grid(
            row=0, column=0, padx=16, pady=(12, 4), sticky="w"
        )

        self.presupuesto = ctk.CTkEntry(
            campo_wrap,
            placeholder_text="Ejemplo: 2000",
            height=46,
            corner_radius=12,
            fg_color=CARD,
            border_color=BORDER,
            text_color=TEXT,
            placeholder_text_color="#9A9AA0",
            font=(FONT, 15),
        )
        self.presupuesto.grid(row=1, column=0, padx=16, pady=(0, 16), sticky="ew")
        self.touch_widgets[self.presupuesto] = {
            "normal": {"height": 46, "font": (FONT, 15)},
            "touch": {"height": 58, "font": (FONT, 17)},
        }

        boton_sugerir = ctk.CTkButton(
            izquierda,
            text="Buscar combinaciones",
            command=self.sugerir,
            height=46,
            corner_radius=14,
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            font=(FONT, 14, "bold"),
        )
        boton_sugerir.grid(row=3, column=0, padx=26, pady=(0, 14), sticky="ew")
        self.touch_widgets[boton_sugerir] = {
            "normal": {"height": 46, "font": (FONT, 14, "bold")},
            "touch": {"height": 60, "font": (FONT, 16, "bold")},
        }

        self.opciones = ctk.CTkTextbox(
            izquierda,
            font=(FONT, 14),
            fg_color=CARD_SOFT,
            text_color=TEXT,
            border_width=1,
            border_color=BORDER,
            corner_radius=16,
            wrap="word",
        )
        self.opciones.grid(row=5, column=0, padx=26, pady=(0, 16), sticky="nsew")

        derecha = ctk.CTkFrame(
            self.frame_presupuesto,
            fg_color=CARD,
            corner_radius=24,
            border_width=1,
            border_color=BORDER,
        )
        derecha.grid(row=0, column=1, padx=(10, 0), pady=8, sticky="nsew")
        derecha.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(derecha, text="Resumen", font=(FONT, 22, "bold"), text_color=TEXT).grid(
            row=0, column=0, padx=22, pady=(22, 6), sticky="w"
        )

        self.chip_opciones = self.crear_chip_vertical(derecha, 1, "Combinaciones", "0")
        self.chip_minimo = self.crear_chip_vertical(derecha, 2, "Par más económico", "—", con_detalle=True)
        self.chip_maximo = self.crear_chip_vertical(derecha, 3, "Par más alto", "—", con_detalle=True)

        ayuda = ctk.CTkFrame(derecha, fg_color=CARD_SOFT, corner_radius=18, border_width=1, border_color=BORDER)
        ayuda.grid(row=4, column=0, padx=20, pady=(8, 20), sticky="ew")

        ctk.CTkLabel(ayuda, text="Cómo funciona", font=(FONT, 13, "bold"), text_color=TEXT).grid(
            row=0, column=0, padx=16, pady=(14, 6), sticky="w"
        )
        ctk.CTkLabel(
            ayuda,
            text=(
                "• Usa el stock actual del kiosco\n"
                "• Combina dos productos distintos\n"
                "• No reserva unidades\n"
                "• Ideal para consulta rápida"
            ),
            justify="left",
            font=(FONT, 13),
            text_color=TEXT_SECONDARY,
        ).grid(row=1, column=0, padx=16, pady=(0, 14), sticky="w")

        self.escribir(self.opciones, "Ingresá un presupuesto para ver opciones.")

    # Pantalla de Reportes 
    def crear_reportes(self):
        contenedor = ctk.CTkFrame(
            self.frame_reportes,
            fg_color=CARD,
            corner_radius=24,
            border_width=1,
            border_color=BORDER,
        )
        contenedor.grid(row=0, column=0, pady=8, sticky="nsew")
        contenedor.grid_columnconfigure(0, weight=1)
        contenedor.grid_rowconfigure(3, weight=1)

        top = ctk.CTkFrame(contenedor, fg_color="transparent")
        top.grid(row=0, column=0, padx=22, pady=(22, 10), sticky="ew")
        top.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(top, text="Historial de ventas", font=(FONT, 22, "bold"), text_color=TEXT).grid(
            row=0, column=0, sticky="w"
        )
        ctk.CTkLabel(
            top,
            text="Todas las ventas confirmadas en esta sesión, de la más reciente a la más vieja.",
            font=(FONT, 13),
            text_color=TEXT_SECONDARY,
        ).grid(row=1, column=0, pady=(2, 0), sticky="w")

        boton_vaciar_historial = ctk.CTkButton(
            top,
            text="Vaciar historial",
            command=self.vaciar_historial,
            width=150,
            height=38,
            corner_radius=12,
            fg_color=DANGER_SOFT,
            hover_color="#FFE2E2",
            text_color=DANGER,
            font=(FONT, 12, "bold"),
        )
        boton_vaciar_historial.grid(row=0, column=1, rowspan=2, sticky="e")
        self.touch_widgets[boton_vaciar_historial] = {
            "normal": {"height": 38, "font": (FONT, 12, "bold")},
            "touch": {"height": 50, "font": (FONT, 14, "bold")},
        }

        chips = ctk.CTkFrame(contenedor, fg_color="transparent")
        chips.grid(row=1, column=0, padx=22, pady=(0, 14), sticky="ew")
        chips.grid_columnconfigure((0, 1, 2), weight=1)
        self.chip_reportes_ventas = self.crear_chip_horizontal(chips, 0, "Ventas", "0", wide=True)
        self.chip_reportes_importe = self.crear_chip_horizontal(chips, 1, "Importe total", self.moneda(0), wide=True)
        self.chip_reportes_ticket = self.crear_chip_horizontal(chips, 2, "Ticket promedio", self.moneda(0), wide=True)
        ranking_card = ctk.CTkFrame(contenedor, fg_color=CARD_SOFT, corner_radius=18, border_width=1, border_color=BORDER)
        ranking_card.grid(row=2, column=0, padx=22, pady=(0, 14), sticky="ew")
        ranking_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(ranking_card, text="Productos más vendidos", font=(FONT, 15, "bold"), text_color=TEXT).grid(
            row=0, column=0, padx=18, pady=(14, 6), sticky="w"
        )
        self.ranking_lista = ctk.CTkFrame(ranking_card, fg_color="transparent")
        self.ranking_lista.grid(row=1, column=0, padx=18, pady=(0, 16), sticky="ew")
        self.ranking_lista.grid_columnconfigure(1, weight=1)
        self.reportes_lista = ctk.CTkScrollableFrame(
            contenedor,
            fg_color="transparent",
            scrollbar_button_color="#C7C7CC",
            scrollbar_button_hover_color="#AEAEB2",
        )
        self.reportes_lista.grid(row=3, column=0, padx=14, pady=(0, 14), sticky="nsew")
        self.reportes_lista.grid_columnconfigure(0, weight=1)

        self.actualizar_reportes()

    def actualizar_reportes(self):
        for widget in self.reportes_lista.winfo_children():
            widget.destroy()

        cantidad = len(self.historial_ventas)
        importe = sum(venta["total"] for venta in self.historial_ventas)
        promedio = importe // cantidad if cantidad else 0

        self.chip_reportes_ventas.value_label.configure(text=str(cantidad))
        self.chip_reportes_importe.value_label.configure(text=self.moneda(importe))
        self.chip_reportes_ticket.value_label.configure(text=self.moneda(promedio))
        
        for widget in self.ranking_lista.winfo_children():
            widget.destroy()

        top_productos = sorted(
            self.ranking_productos.values(), key=lambda item: item["cantidad"], reverse=True
        )[:5]

        if not top_productos:
            ctk.CTkLabel(
                self.ranking_lista, text="Todavía no hay ventas para armar un ranking.",
                font=(FONT, 12), text_color=TEXT_SECONDARY,
            ).grid(row=0, column=0, sticky="w")
        else:
            maximo = top_productos[0]["cantidad"]
            for fila, item in enumerate(top_productos):
                ctk.CTkLabel(
                    self.ranking_lista, text=f"{fila + 1}. {item['nombre']}",
                    font=(FONT, 13, "bold"), text_color=TEXT,
                ).grid(row=fila, column=0, padx=(0, 10), pady=4, sticky="w")

                barra = ctk.CTkProgressBar(
                    self.ranking_lista, height=8, corner_radius=4,
                    fg_color=CARD_MUTED, progress_color=ACCENT,
                )
                barra.set(item["cantidad"] / maximo)
                barra.grid(row=fila, column=1, padx=10, pady=4, sticky="ew")

                unidad = "unidad" if item["cantidad"] == 1 else "unidades"
                ctk.CTkLabel(
                    self.ranking_lista, text=f"{item['cantidad']} {unidad}",
                    font=(FONT, 12, "bold"), text_color=TEXT_SECONDARY,
                ).grid(row=fila, column=2, padx=(10, 0), pady=4, sticky="e")

        if not self.historial_ventas:
            vacio = ctk.CTkFrame(self.reportes_lista, fg_color=CARD_SOFT, corner_radius=20, border_width=1, border_color=BORDER)
            vacio.grid(row=0, column=0, padx=8, pady=16, sticky="ew")
            ctk.CTkLabel(
                vacio,
                text="Todavía no hay ventas registradas.",
                font=(FONT, 15, "bold"),
                text_color=TEXT,
            ).grid(row=0, column=0, padx=22, pady=(22, 4), sticky="w")
            ctk.CTkLabel(
                vacio,
                text="Cuando confirmes una venta en el kiosco, va a aparecer acá.",
                font=(FONT, 13),
                text_color=TEXT_SECONDARY,
            ).grid(row=1, column=0, padx=22, pady=(0, 22), sticky="w")
            return

        for fila, venta in enumerate(reversed(self.historial_ventas)):
            numero = len(self.historial_ventas) - fila
            card = ctk.CTkFrame(self.reportes_lista, fg_color=CARD_SOFT, corner_radius=18, border_width=1, border_color=BORDER)
            card.grid(row=fila, column=0, padx=8, pady=6, sticky="ew")
            card.grid_columnconfigure(0, weight=1)

            encabezado = ctk.CTkFrame(card, fg_color="transparent")
            encabezado.grid(row=0, column=0, padx=18, pady=(14, 4), sticky="ew")
            encabezado.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(
                encabezado,
                text=f"Venta #{numero}  ·  {venta['hora'].strftime('%d/%m %H:%M')}",
                font=(FONT, 14, "bold"),
                text_color=TEXT,
            ).grid(row=0, column=0, sticky="w")
            ctk.CTkLabel(
                encabezado,
                text=self.moneda(venta["total"]),
                font=(FONT, 16, "bold"),
                text_color=TEXT,
            ).grid(row=0, column=1, sticky="e")

            detalle = " · ".join(f"{nombre} x{cantidad}" for nombre, cantidad, _precio in venta["items"])
            ctk.CTkLabel(
                card,
                text=detalle,
                font=(FONT, 12),
                text_color=TEXT_SECONDARY,
                justify="left",
                wraplength=900,
            ).grid(row=1, column=0, padx=18, pady=(0, 14), sticky="w")

    def vaciar_historial(self):
        if not self.historial_ventas:
            return
        respuesta = messagebox.askyesno(
            "Vaciar historial",
            "¿Seguro que querés borrar el historial de ventas de esta sesión?",
            parent=self.ventana,
        )
        if respuesta:
            self.historial_ventas.clear()
            self.ventas.clear()
            self.refrescar()

    def crear_chip_vertical(self, parent, row, titulo, valor, con_detalle=False):
        chip = ctk.CTkFrame(parent, fg_color=CARD_MUTED, corner_radius=18, border_width=1, border_color=BORDER)
        chip.grid(row=row, column=0, padx=20, pady=6, sticky="ew")
        chip.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(chip, text=titulo, font=(FONT, 12, "bold"), text_color=TEXT_SECONDARY).grid(
            row=0, column=0, padx=16, pady=(14, 4), sticky="w"
        )
        value_label = ctk.CTkLabel(chip, text=valor, font=(FONT, 22, "bold"), text_color=TEXT)
        value_label.grid(row=1, column=0, padx=16, pady=(0, 4 if con_detalle else 14), sticky="w")
        chip.value_label = value_label

        if con_detalle:
            detail_label = ctk.CTkLabel(chip, text="", font=(FONT, 12), text_color=TEXT_SECONDARY)
            detail_label.grid(row=2, column=0, padx=16, pady=(0, 14), sticky="w")
            chip.detail_label = detail_label

        return chip

    # Ayudadores 
    @staticmethod
    def moneda(valor):
        return "$" + f"{valor:,}".replace(",", ".")

    def escribir(self, caja, texto):
        caja.configure(state="normal")
        caja.delete("1.0", "end")
        caja.insert("1.0", texto)
        caja.configure(state="disabled")

    def actualizar_preview_inicio(self):
        destacados = [p for p in self.productos if p.stock > 0]
        if not destacados:
            for thumb, label in self.preview_labels:
                thumb.configure(image=None, text="", fg_color="#F0F0F2")
                label.configure(text="")
            return
        total = len(destacados)
        for idx, (thumb, label) in enumerate(self.preview_labels):
            producto = destacados[(self.preview_offset + idx) % total]
            thumb.configure(text="", image=self.imagenes_producto[producto.codigo], fg_color="transparent")
            label.configure(text=f"{producto.nombre}  ·  {self.moneda(producto.precio)}")

    def rotar_preview(self):
        if not self.ventana.winfo_exists():
            return
        destacados = [p for p in self.productos if p.stock > 0]
        if destacados:
            self.preview_offset = (self.preview_offset + len(self.preview_labels)) % len(destacados)
        self.actualizar_preview_inicio()
        self.ventana.after(3000, self.rotar_preview)

    # Agranda o achica botones, entradas y filtros de toda la app según el switch de modo touch
    def aplicar_modo_touch(self):
        touch = self.touch_var.get()
        clave = "touch" if touch else "normal"
        for widget, tamanios in self.touch_widgets.items():
            widget.configure(**tamanios[clave])

    # cosa para actualizar el seleccionado de productos  en la pantalla 
    def refrescar(self):
        self.aplicar_modo_touch()

        for widget in self.catalogo.winfo_children():
            widget.destroy()
        
        self.actualizar_texto_categorias()

        stock_total = sum(producto.stock for producto in self.productos)
        self.chip_productos.value_label.configure(text=str(len(self.productos)))
        self.chip_stock.value_label.configure(text=str(stock_total))
        self.home_chip_productos.value_label.configure(text=str(len(self.productos)))
        self.home_chip_stock.value_label.configure(text=str(stock_total))
        self.home_chip_ventas.value_label.configure(text=str(len(self.ventas)))
        self.actualizar_preview_inicio()
        self.actualizar_reportes()

        termino = self.busqueda_var.get().strip().lower()
        categoria = self.categoria_var.get()
        productos_visibles = []
        for producto in self.productos:
            estilo_producto = PRODUCT_STYLES.get(producto.nombre, {"category": "Producto"})
            coincide_texto = not termino or termino in producto.nombre.lower() or termino in producto.codigo.lower()
            coincide_categoria = categoria == "Todos" or estilo_producto.get("category") == categoria
            if coincide_texto and coincide_categoria:
                productos_visibles.append(producto)

        self.chip_productos.value_label.configure(text=str(len(productos_visibles)))

        if not productos_visibles:
            vacio = ctk.CTkFrame(self.catalogo, fg_color=CARD_SOFT, corner_radius=20, border_width=1, border_color=BORDER)
            vacio.grid(row=0, column=0, columnspan=2, padx=8, pady=16, sticky="ew")
            ctk.CTkLabel(
                vacio,
                text="No encontramos productos con esos filtros.",
                font=(FONT, 15, "bold"),
                text_color=TEXT,
            ).grid(row=0, column=0, padx=22, pady=(22, 4), sticky="w")
            ctk.CTkLabel(
                vacio,
                text="Probá otra búsqueda o volvé a la categoría Todos.",
                font=(FONT, 13),
                text_color=TEXT_SECONDARY,
            ).grid(row=1, column=0, padx=22, pady=(0, 22), sticky="w")

        touch = self.touch_var.get()
        for indice, producto in enumerate(productos_visibles):
            columna = indice % 2
            fila = indice // 2

            en_carrito = cantidad_en_carrito(self.carrito, producto.codigo)
            disponible = max(producto.stock - en_carrito, 0)

            sin_stock_real = producto.stock == 0
            sin_stock_disponible = disponible == 0
            bajo_stock = 0 < disponible <= 2

            if sin_stock_real:
                estado = "Agotado"
                estado_color = TEXT_SECONDARY
            elif sin_stock_disponible:
                estado = "En tu carrito"
                estado_color = TEXT_SECONDARY
            elif bajo_stock:
                estado = "Últimas unidades"
                estado_color = WARNING
            else:
                estado = "Disponible"
                estado_color = SUCCESS

            agotado = sin_stock_disponible

            estilo = PRODUCT_STYLES.get(producto.nombre, {"category": "Producto"})

            card = ctk.CTkFrame(
                self.catalogo,
                fg_color=CARD_SOFT,
                corner_radius=20,
                border_width=1,
                border_color=BORDER,
            )
            card.grid(row=fila, column=columna, padx=8, pady=8, sticky="ew")
            card.grid_columnconfigure(1, weight=1)

            thumb = ctk.CTkLabel(card, text="", image=self.imagenes_producto[producto.codigo])
            thumb.grid(row=0, column=0, rowspan=4, padx=(20 if touch else 16, 14 if touch else 12), pady=22 if touch else 16, sticky="n")

            ctk.CTkLabel(card, text=estilo.get("category", "Producto"), font=(FONT, 11, "bold"), text_color=TEXT_SECONDARY).grid(
                row=0, column=1, padx=(0, 14), pady=(16, 0), sticky="w"
            )
            ctk.CTkLabel(card, text=producto.nombre, font=(FONT, 18, "bold"), text_color=TEXT).grid(
                row=1, column=1, padx=(0, 14), pady=(2, 2), sticky="w"
            )
            ctk.CTkLabel(card, text=f"{estado} · Stock {disponible}", font=(FONT, 12), text_color=estado_color).grid(
                row=2, column=1, padx=(0, 14), pady=(0, 8), sticky="w"
            )

            pie = ctk.CTkFrame(card, fg_color="transparent")
            pie.grid(row=3, column=1, padx=(0, 14), pady=(0, 16), sticky="ew")
            pie.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(pie, text=self.moneda(producto.precio), font=(FONT, 18, "bold"), text_color=TEXT).grid(
                row=0, column=0, sticky="w"
            )
            boton = ctk.CTkButton(
                pie,
                text="Agregar",
                width=124 if touch else 100,
                height=46 if touch else 36,
                corner_radius=12,
                fg_color=ACCENT if not agotado else DISABLED,
                hover_color=ACCENT_HOVER if not agotado else DISABLED,
                text_color="white",
                font=(FONT, 14 if touch else 12, "bold"),
                command=partial(self.agregar_uno, producto.codigo),
            )
            boton.grid(row=0, column=1, sticky="e")
            if agotado:
                boton.configure(state="disabled", text="Agotado" if sin_stock_real else "Sin stock")

        cantidad = len(self.carrito)
        total = total_carrito(self.carrito)
        self.chip_items.value_label.configure(text=str(cantidad))
        self.chip_ticket.value_label.configure(text=self.moneda(total))

        if cantidad == 0:
            detalle = "Tu carrito está vacío.\n\nSeleccioná un producto para empezar la compra."
            self.estado_carrito.configure(text="Todavía no agregaste productos")
            self.boton_vender.configure(state="disabled", fg_color=DISABLED, hover_color=DISABLED)
        else:
            resumen_por_producto = {}
            for producto in self.carrito:
                if producto.codigo not in resumen_por_producto:
                    resumen_por_producto[producto.codigo] = {
                        "nombre": producto.nombre,
                        "cantidad": 0,
                        "precio": producto.precio,
                    }
                resumen_por_producto[producto.codigo]["cantidad"] += 1

            lineas = []
            for item in resumen_por_producto.values():
                subtotal = item["cantidad"] * item["precio"]
                lineas.append(f"{item['nombre']}  ·  x{item['cantidad']}  ·  {self.moneda(subtotal)}")
            detalle = "\n".join(lineas)
            sufijo = "producto" if cantidad == 1 else "productos"
            self.estado_carrito.configure(text=f"{cantidad} {sufijo} en el carrito")
            self.boton_vender.configure(state="normal", fg_color=BLACK_BUTTON, hover_color=BLACK_BUTTON_HOVER)

        self.escribir(self.detalle, detalle)
        self.total.configure(text=self.moneda(total))

        importe = sum(self.ventas)
        ventas_txt = "venta" if len(self.ventas) == 1 else "ventas"
        self.resumen.configure(
            text=(
                f"Sesión actual  ·  {len(self.ventas)} {ventas_txt} registradas  ·  "
                f"Importe vendido: {self.moneda(importe)}"
            )
        )

    # Las acciones para que el kiosco ande, como agregar, quitar, vaciar y vender
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
        self.abrir_checkout()

    def abrir_checkout(self):
        checkout = ctk.CTkToplevel(self.ventana)
        checkout.title("Checkout · RecreoLab")
        checkout.geometry("560x620")
        checkout.resizable(False, False)
        checkout.configure(fg_color=BG)
        checkout.transient(self.ventana)
        checkout.grab_set()
        checkout.grid_columnconfigure(0, weight=1)
        checkout.grid_rowconfigure(0, weight=1)

        card = ctk.CTkFrame(checkout, fg_color=CARD, corner_radius=26, border_width=1, border_color=BORDER)
        card.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(4, weight=1)

        ctk.CTkLabel(card, text="Revisá tu compra", font=(FONT, 26, "bold"), text_color=TEXT).grid(
            row=0, column=0, padx=24, pady=(24, 4), sticky="w"
        )
        ctk.CTkLabel(
            card,
            text="Antes de registrar la venta, confirmá los productos y el total.",
            font=(FONT, 13),
            text_color=TEXT_SECONDARY,
        ).grid(row=1, column=0, padx=24, pady=(0, 14), sticky="w")

        resumen = {}
        for producto in self.carrito:
            if producto.codigo not in resumen:
                resumen[producto.codigo] = [producto, 0]
            resumen[producto.codigo][1] += 1

        lista = ctk.CTkScrollableFrame(card, fg_color=CARD_SOFT, corner_radius=18, border_width=1, border_color=BORDER)
        lista.grid(row=4, column=0, padx=24, pady=(0, 14), sticky="nsew")
        lista.grid_columnconfigure(0, weight=1)

        for fila, (producto, cantidad) in enumerate(resumen.values()):
            item = ctk.CTkFrame(lista, fg_color="transparent")
            item.grid(row=fila, column=0, padx=10, pady=8, sticky="ew")
            item.grid_columnconfigure(1, weight=1)
            ctk.CTkLabel(item, text="", image=self.imagenes_producto[producto.codigo]).grid(row=0, column=0, rowspan=2, padx=(0, 12))
            ctk.CTkLabel(item, text=producto.nombre, font=(FONT, 14, "bold"), text_color=TEXT).grid(row=0, column=1, sticky="w")
            ctk.CTkLabel(
                item,
                text=f"{cantidad} × {self.moneda(producto.precio)}",
                font=(FONT, 12),
                text_color=TEXT_SECONDARY,
            ).grid(row=1, column=1, sticky="w")
            ctk.CTkLabel(
                item,
                text=self.moneda(cantidad * producto.precio),
                font=(FONT, 14, "bold"),
                text_color=TEXT,
            ).grid(row=0, column=2, rowspan=2, padx=(12, 0), sticky="e")

        total = total_carrito(self.carrito)
        total_box = ctk.CTkFrame(card, fg_color=BLUE_SOFT, corner_radius=18)
        total_box.grid(row=5, column=0, padx=24, pady=(0, 14), sticky="ew")
        total_box.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(total_box, text="Total", font=(FONT, 13, "bold"), text_color=TEXT_SECONDARY).grid(
            row=0, column=0, padx=18, pady=(14, 0), sticky="w"
        )
        ctk.CTkLabel(total_box, text=self.moneda(total), font=(FONT, 30, "bold"), text_color=TEXT).grid(
            row=1, column=0, padx=18, pady=(0, 14), sticky="w"
        )

        acciones = ctk.CTkFrame(card, fg_color="transparent")
        acciones.grid(row=6, column=0, padx=24, pady=(0, 24), sticky="ew")
        acciones.grid_columnconfigure((0, 1), weight=1)
        touch = self.touch_var.get()
        alto_boton = 58 if touch else 44
        fuente_boton = (FONT, 15, "bold") if touch else (FONT, 13, "bold")
        ctk.CTkButton(
            acciones, text="Volver", command=checkout.destroy, height=alto_boton, corner_radius=13,
            fg_color=CARD_MUTED, hover_color="#E8E8ED", text_color=TEXT, font=fuente_boton
        ).grid(row=0, column=0, padx=(0, 6), sticky="ew")
        ctk.CTkButton(
            acciones, text="Confirmar venta", command=lambda: self.confirmar_venta(checkout), height=alto_boton, corner_radius=13,
            fg_color=BLACK_BUTTON, hover_color=BLACK_BUTTON_HOVER, text_color="white", font=fuente_boton
        ).grid(row=0, column=1, padx=(6, 0), sticky="ew")

    def confirmar_venta(self, ventana_checkout):
        resumen = {}
        for producto in self.carrito:
            if producto.codigo not in resumen:
                resumen[producto.codigo] = [producto.nombre, 0, producto.precio]
            resumen[producto.codigo][1] += 1

            if producto.codigo not in self.ranking_productos:
                self.ranking_productos[producto.codigo] = {"nombre": producto.nombre, "cantidad": 0}
            self.ranking_productos[producto.codigo]["nombre"] = producto.nombre
            self.ranking_productos[producto.codigo]["cantidad"] += 1
        try:
            total = confirmar(self.carrito, self.ventas)
        except ValueError as error:
            messagebox.showerror("No se registró", str(error), parent=ventana_checkout)
            return

        self.historial_ventas.append({
            "hora": datetime.now(),
            "items": [tuple(item) for item in resumen.values()],
            "total": total,
        })

        ventana_checkout.destroy()
        self.refrescar()
        self.escribir(self.opciones, "Cambió el stock. Volvé a buscar combinaciones.")
        self.chip_opciones.value_label.configure(text="0")
        self.chip_minimo.value_label.configure(text="—")
        self.chip_maximo.value_label.configure(text="—")
        messagebox.showinfo(
            "Venta registrada",
            f"Venta confirmada por {self.moneda(total)}.\nComprobante sin validez fiscal.",
            parent=self.ventana,
        )

    def sugerir(self):
        try:
            texto = self.presupuesto.get().strip()
            presupuesto = int(texto)
            if presupuesto <= 0 or presupuesto > 1_000_000:
                raise ValueError("Presupuesto fuera de rango.")
        except (TypeError, ValueError):
            messagebox.showwarning(
                "Presupuesto inválido",
                "Ingresá entre 1 y 1000000, sin puntos ni decimales.",
                parent=self.ventana,
            )
            return

        # Busca combinaciones para cada cantidad posible de productos, de más a menos
        disponibles = [producto for producto in self.productos if producto.stock > 0]

        # Límite de seguridad para evitar demasiadas combinaciones
        LIMITE_PRODUCTOS = 20

        # Si hay más de 20 productos, se toman solamente los 20 más baratos
        if len(disponibles) > LIMITE_PRODUCTOS:
            disponibles = sorted(disponibles, key=lambda producto: producto.precio)[:LIMITE_PRODUCTOS]

        opciones = []
        for cantidad in range(len(disponibles), 1, -1):
            for combo in combinations(disponibles, cantidad):
                total = sum(producto.precio for producto in combo)
                if total <= presupuesto:
                    opciones.append((cantidad, combo, total, presupuesto-total))

        # más productos primero; dentro de cada cantidad, menos vuelto primero
        opciones.sort(key=lambda opcion: (-opcion[0], opcion[3]))

        lineas = []
        cantidad_actual = None
        for cantidad, combo, total, sobra in opciones:
            if cantidad != cantidad_actual:
                cantidad_actual = cantidad
                etiqueta = "producto" if cantidad == 1 else "productos"
                lineas.append(f"— {cantidad} {etiqueta} —")
            nombres = " + ".join(f"{p.nombre} ({self.moneda(p.precio)})" for p in combo)
            lineas.append(f"{nombres}\nTotal: {self.moneda(total)}  ·  Te sobran {self.moneda(sobra)}")

        resultado = "\n\n".join(lineas) or "No hay combinaciones posibles para ese presupuesto."
        self.escribir(self.opciones, resultado)

        self.chip_opciones.value_label.configure(text=str(len(opciones)))
        if opciones:
            min_opcion = min(opciones, key=lambda opcion: opcion[2])
            max_opcion = max(opciones, key=lambda opcion: opcion[2])
            self.chip_minimo.value_label.configure(text=self.moneda(min_opcion[2]))
            self.chip_minimo.detail_label.configure(text=" + ".join(p.nombre for p in min_opcion[1]))
            self.chip_maximo.value_label.configure(text=self.moneda(max_opcion[2]))
            self.chip_maximo.detail_label.configure(text=" + ".join(p.nombre for p in max_opcion[1]))
        else:
            self.chip_minimo.value_label.configure(text="—")
            self.chip_minimo.detail_label.configure(text="")
            self.chip_maximo.value_label.configure(text="—")
            self.chip_maximo.detail_label.configure(text="")
            
    def ejecutar(self):
        self.ventana.mainloop()


if __name__ == "__main__":
    Aplicacion().ejecutar()
