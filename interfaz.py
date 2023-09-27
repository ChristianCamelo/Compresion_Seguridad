import tkinter as tk
from tkinter import filedialog

def cargar_archivo():
    archivo = filedialog.askopenfilename()
    archivos_seleccionados.append(archivo)
    crear_botones_cifrar_descifrar(archivo, cifrar=True)

def cifrar_archivo(archivo):
    resultado_label.config(text=f"Cifrar {archivo} - Función pendiente")
    # Ocultar el botón de cifrar y mostrar el botón de descifrar
    cifrar_button.grid_remove()
    descifrar_button.grid(row=0, column=1, padx=(0, 5), sticky="e")

def descifrar_archivo(archivo):
    resultado_label.config(text=f"Descifrar {archivo} - Función pendiente")
    # Ocultar el botón de descifrar y mostrar el botón de cifrar
    descifrar_button.grid_remove()
    cifrar_button.grid(row=0, column=1, padx=(0, 5), sticky="e")

def crear_botones_cifrar_descifrar(archivo, cifrar=True):
    frame = tk.Frame(ventana)
    frame.grid(row=len(archivos_seleccionados), column=0, padx=5, pady=5, sticky="w")

    label_archivo = tk.Label(frame, text=archivo)
    label_archivo.grid(row=0, column=0)

    global cifrar_button
    global descifrar_button

    cifrar_button = tk.Button(frame, text="Cifrar", command=lambda: cifrar_archivo(archivo))
    descifrar_button = tk.Button(frame, text="Descifrar", command=lambda: descifrar_archivo(archivo))

    if cifrar:
        cifrar_button.grid(row=0, column=1, padx=(0, 5), sticky="e")
    else:
        descifrar_button.grid(row=0, column=1, padx=(0, 5), sticky="e")

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