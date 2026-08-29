import customtkinter as ctk
def mostrar():
    try:
        monto = int(entrada.get().strip())
        if monto <= 0:
            raise ValueError("Monto no positivo")
    except ValueError:
        salida.configure(text="Ingresá un entero mayor que cero.")
        return
    salida.configure(text=f"Tu presupuesto es ${monto}")

ventana = ctk.CTk()
ventana.title("Probar un presupuesto")
ventana.geometry("600x320")
ventana.grid_columnconfigure(0, weight=1)
entrada = ctk.CTkEntry(ventana,
                placeholder_text="Pesos enteros, sin puntos")
entrada.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
boton = ctk.CTkButton(ventana, text="Consultar", command=mostrar)
boton.grid(row=1, column=0, pady=10)
salida = ctk.CTkLabel(ventana, text="Esperando un presupuesto")
salida.grid(row=2, column=0, pady=20)
ventana.mainloop()