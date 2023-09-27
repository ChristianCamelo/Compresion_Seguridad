import tkinter as tk
from tkinter import filedialog

class Archivo:
    def __init__(self, archivo):
        self.archivo = archivo
        self.cifrar = True
        self.frame = None
        self.label = None
        self.cifrar_button = None
        self.descifrar_button = None

def cargar_archivo():
    archivo = filedialog.askopenfilename()
    if archivo:
        archivo_obj = Archivo(archivo)
        archivos_seleccionados.append(archivo_obj)
        crear_botones_cifrar_descifrar(archivo_obj)

def toggle_botones(archivo):
    archivo.cifrar = not archivo.cifrar
    if archivo.cifrar:
        archivo.cifrar_button.grid()
        archivo.descifrar_button.grid_remove()
    else:
        archivo.descifrar_button.grid()
        archivo.cifrar_button.grid_remove()

def crear_botones_cifrar_descifrar(archivo_obj):
    archivo_obj.frame = tk.Frame(ventana)
    archivo_obj.frame.grid(row=len(archivos_seleccionados), column=0, padx=5, pady=5, sticky="w")

    archivo_obj.label = tk.Label(archivo_obj.frame, text=archivo_obj.archivo)
    archivo_obj.label.grid(row=0, column=0)

    archivo_obj.cifrar_button = tk.Button(archivo_obj.frame, text="Cifrar", command=lambda a=archivo_obj: toggle_botones(a))
    archivo_obj.descifrar_button = tk.Button(archivo_obj.frame, text="Descifrar", command=lambda a=archivo_obj: toggle_botones(a))

    archivo_obj.cifrar_button.grid(row=0, column=1, padx=(0, 5), sticky="e")
    archivo_obj.descifrar_button.grid(row=0, column=1, padx=(0, 5), sticky="e")
    archivo_obj.descifrar_button.grid_remove()

archivos_seleccionados = []

# Crear una ventana principal
ventana = tk.Tk()
ventana.title("Ejemplo de Cifrado y Descifrado")

# Botón para cargar un archivo
cargar_button = tk.Button(ventana, text="Cargar Archivo", command=cargar_archivo)
cargar_button.grid(row=0, column=0, columnspan=3, pady=10)

# Etiqueta para mostrar el resultado
resultado_label = tk.Label(ventana, text="")
resultado_label.grid(row=1, column=0, columnspan=3, pady=10)

# Iniciar el bucle principal de la aplicación
ventana.mainloop()
