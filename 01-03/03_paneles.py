import customtkinter as ctk
ventana = ctk.CTk()
ventana.geometry("850x500")
ventana.grid_columnconfigure(0, weight=2)
ventana.grid_columnconfigure(1, weight=1)
ventana.grid_rowconfigure(0, weight=1)

catalogo = ctk.CTkFrame(ventana)
catalogo.grid(row=0, column=0, padx=12, pady=12, sticky="nsew")
carrito = ctk.CTkFrame(ventana)
carrito.grid(row=0, column=1, padx=12, pady=12, sticky="nsew")

catalogo.grid_columnconfigure(0, weight=1)
carrito.grid_columnconfigure(0, weight=1)

ctk.CTkLabel(catalogo, text="Productos").grid(
    row=0, column=0, padx=12, pady=12)
ctk.CTkLabel(carrito, text="Tu compra").grid(
    row=0, column=0, padx=12, pady=12)

tabs = ctk.CTkTabview(ventana)
tabs.grid(row=0, column=0, padx=12, pady=12, sticky="nsew")
tabs.add("Kiosco")
tabs.add("Presupuesto")
etiqueta = ctk.CTkLabel(tabs.tab("Kiosco"), text="Catálogo")
etiqueta.grid(row=0, column=0, padx=12, pady=12)

def escribir(caja, texto):
    caja.configure("quot;normal")
    caja.delete("1.0", "end")
    caja.insert("1.0", texto)
    caja.configure(state="disabled")

ventana.mainloop()