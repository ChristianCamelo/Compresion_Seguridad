import tkinter as tk
import os
from tkinter import filedialog
from encriptar import encriptar
from principal import escribirLog
from desencriptar import desencriptar
from shutil import rmtree

ventana = None
global cantidad
cantidad = 0

class Archivo:
    def __init__(self, archivo):
        self.archivo = archivo
        self.cifrar = True
        self.frame = None
        self.label = None
        self.descifrar_button = None

def cargar_archivo():
    global cantidad
    archivo = filedialog.askopenfilename()
    ruta_keys = os.path.join(os.getcwd(), 'keys')
    ruta_archivos_encriptados = os.path.join(os.getcwd(), 'archivos_encriptados')
    
    if archivo:
        archivo_obj = Archivo(archivo)
        archivo_obj.ruta = os.path.abspath(archivo)
        archivo_obj.pos=cantidad
        archivo_obj.enc = cifrar(archivo_obj.ruta, cantidad)
        archivo_obj.encPath = os.path.join(archivo_obj.enc)
        archivo_obj.format = (archivo_obj.ruta).split(".")[-1]
        archivo_obj.keyPath = os.path.join(ruta_keys, 'llave' + str(archivo_obj.pos) + '.bin')
        archivo_obj.noncePath = os.path.join(ruta_archivos_encriptados, 'nonce' + str(archivo_obj.pos) + '.bin')

        escribirLog("Lectura: Ruta de archivo leido es: "+ archivo_obj.archivo)
        escribirLog("Escritura: Ruta de archivo cifrado es: "+ archivo_obj.enc)
        
        actualizarUI()
        crear_botones_descifrar(archivo_obj)
        cantidad = cantidad+1
        archivos_seleccionados.append(archivo_obj)

def toggle_botones(archivo):

    archivo.descifrar_button.grid()

    escribirLog("Descencriptando archivo "+str(archivo.enc))
    escribirLog("Descencriptando con llave: "+ str(archivo.keyPath))
    escribirLog("La desencriptacion ha sido: " + str(desencriptar(archivo.encPath,archivo.keyPath,archivo.pos, archivo.format)))

def cifrar(ruta,cantidad):
    return encriptar(ruta,cantidad)

def crear_botones_descifrar(archivo_obj):

    archivo_obj.frame = tk.Frame(ventana, borderwidth=2, relief="solid")
    archivo_obj.frame.grid(row=len(archivos_seleccionados), column=0, padx=5, pady=5, sticky="w")

    color1 = "#2233FF"

    archivo_obj.label = tk.Label(archivo_obj.frame, text=archivo_obj.enc, font=("Helvetica", 12), background=color1, fg="black")
    archivo_obj.label.grid(row=1, column=0, padx=5, pady=5)

    archivo_obj.descifrar_button = tk.Button(archivo_obj.frame, text="Descifrar", font=("Helvetica", 12, "bold"), command=lambda a=archivo_obj: toggle_botones(a))
    archivo_obj.descifrar_button.grid(row=1, column=1, padx=(0, 5))


def limpiar_cache():
    # Eliminando directorios
    rmtree("archivos_desencriptados")
    rmtree("archivos_encriptados")
    rmtree("keys")
    # Creadon directorios
    os.mkdir("archivos_desencriptados")
    os.mkdir("archivos_encriptados")
    os.mkdir("keys")

archivos_seleccionados = []

def actualizarUI():
    # Botón para cargar un archivo
    cargar_button = tk.Button(ventana, text="Cargar archivo", font=("Helvetica", 12, "bold"), command=cargar_archivo)
    cargar_button.grid(row=cantidad+1, column=0, columnspan=3, pady=10)

    # Botón para limpiar
    limpiar_button = tk.Button(ventana, text="Limpiar cache", font=("Helvetica", 12, "bold"), command=limpiar_cache)
    limpiar_button.grid(row=cantidad+2, column=0, columnspan=3, pady=10)

def iniciar_ventana():
    limpiar_cache()
    ventana = tk.Tk()
    actualizarUI()
    ventana.title("Ejemplo de Cifrado y Descifrado")
    escribirLog("----------------INICIANDO EL PROGRAMA--------------")
    ventana.mainloop()


iniciar_ventana()