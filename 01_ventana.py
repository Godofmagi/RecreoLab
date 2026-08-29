import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

ventana = ctk.CTk()
ventana.title("Mi primer kiosco")
ventana.geometry("640x600")
ventana.minsize(480, 300)
ventana.grid_columnconfigure(0, weight=1)

titulo = ctk.CTkLabel(
    ventana,
    text= "Bienvenidos a RecreoLab",
    font=("Arial", 24, "bold")
)
titulo.grid(row=0, column=0, padx=20, pady=20)

ventana.mainloop()