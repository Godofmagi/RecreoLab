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

subtitulo = ctk.CTkLabel(
    ventana,
    text ="Equipo formado por Borgazzi Dante, Gonzales Luca y Revainera Thiago",
    font=("Comic sans", 14, "bold")
)
subtitulo.grid(row=1,column=0 ,padx=30, pady= 30)

ventana.mainloop()