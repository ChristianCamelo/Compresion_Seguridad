import tkinter as tk
import os
from tkinter import filedialog
from encriptar import encriptar
from principal import escribirLog
from desencriptar import desencriptar

#encriptar(r'E:\Universidad\Tercero_1\Compresion_Seguridad\Compresion_Seguridad\archivos_normales\archivo.txt',1)
#escribirLog("fichero encriptado con exito")
#desencriptar(r'E:\Universidad\Tercero_1\Compresion_Seguridad\Compresion_Seguridad\archivos_normales\archivo.txt.enc',r'E:\Universidad\Tercero_1\Compresion_Seguridad\Compresion_Seguridad\keys\llave1.bin')

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
    if archivo:
        archivo_obj = Archivo(archivo)
        archivo_obj.ruta = os.path.abspath(archivo)
        escribirLog("Lectura: Ruta de archivo leido es: "+ archivo_obj.archivo)
        archivos_seleccionados.append(archivo_obj)
        archivo_obj.enc = cifrar(archivo_obj.ruta, cantidad)
        archivo_obj.encPath = os.path.join(archivo_obj.enc)
        escribirLog("Escritura: Ruta de archivo cifrado es: "+ archivo_obj.enc)
        crear_botones_descifrar(archivo_obj)
        archivo_obj.pos=cantidad
        cantidad = cantidad+1

def toggle_botones(archivo):

    archivo.descifrar_button.grid()
    escribirLog("Descencriptando archivo "+str(archivo.enc))
    ruta_keys = os.path.join(os.getcwd(), 'keys')
    ruta_archivo = os.path.join(ruta_keys, 'llave' + str(archivo.pos) + '.bin')
    escribirLog("Descencriptando con llave: "+ ruta_archivo)
    with open(ruta_archivo, 'rb') as key:
        asociatedKey = key.read()
    escribirLog("La desencriptacion ha sido: " + (str)(desencriptar(archivo.encPath,asociatedKey,archivo.pos)))

def cifrar(ruta,cantidad):
    return encriptar(ruta,cantidad)

def crear_botones_descifrar(archivo_obj):

    archivo_obj.frame = tk.Frame(ventana, borderwidth=2, relief="solid")
    archivo_obj.frame.grid(row=len(archivos_seleccionados), column=0, padx=5, pady=5, sticky="w")

    gradient_frame = tk.Frame(archivo_obj.frame)
    gradient_frame.grid(row=0, column=0, columnspan=3)

    color1 = "#22cc22"

    archivo_obj.label = tk.Label(archivo_obj.frame, text=archivo_obj.enc, font=("Helvetica", 12), background=color1, fg="black")
    archivo_obj.label.grid(row=1, column=0, padx=5, pady=5)

    archivo_obj.descifrar_button = tk.Button(archivo_obj.frame, text="Descifrar", font=("Helvetica", 12, "bold"), command=lambda a=archivo_obj: toggle_botones(a))
    archivo_obj.descifrar_button.grid(row=1, column=1, padx=(0, 5))


archivos_seleccionados = []

# Crear una ventana principal
ventana = tk.Tk()
ventana.title("Ejemplo de Cifrado y Descifrado")
escribirLog("----------------INICIANDO EL PROGRAMA--------------")
# Botón para cargar un archivo
cargar_button = tk.Button(ventana, text="Cargar Archivo", font=("Helvetica", 12, "bold"), command=cargar_archivo)
cargar_button.grid(row=0, column=0, columnspan=3, pady=10)

# Etiqueta para mostrar el resultado
resultado_label = tk.Label(ventana, text="")
resultado_label.grid(row=1, column=0, columnspan=3, pady=10)

# Iniciar el bucle principal de la aplicación
ventana.mainloop()
