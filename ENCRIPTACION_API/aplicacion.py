import tkinter as tk
import os
from tkinter import filedialog
from tkinter import ttk
from encriptar import encriptar
from utilities import escribirLog
from desencriptar import desencriptar
from shutil import rmtree

global ventana
global cantidad
cantidad = 0
width = 1000
height = 800

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
    
    if archivo:
        archivo_obj = Archivo(archivo)
        archivo_obj.ruta = os.path.abspath(archivo)
        archivo_obj.pos=cantidad
        archivo_obj.enc = cifrar(archivo_obj.ruta, cantidad)
        archivo_obj.size = os.path.getsize(archivo_obj.enc)
        archivo_obj.encPath = os.path.join(archivo_obj.enc)
        archivo_obj.format = (archivo_obj.ruta).split(".")[-1]
        archivo_obj.nombre = os.path.basename(archivo_obj.ruta)
        archivo_obj.keyPath = os.path.join(ruta_keys, 'llave' + str(archivo_obj.pos) + '.bin')

        escribirLog("Lectura: Ruta de archivo leido es: "+ archivo_obj.archivo)
        escribirLog("Escritura: Ruta de archivo cifrado es: "+ archivo_obj.enc)
        escribirLog("Escritura: Llave de archivo cifrado es: "+ archivo_obj.keyPath)
        
        actualizarUI()
        cifrarArchivo(archivo_obj)
        archivos_seleccionados.append(archivo_obj)
        cantidad = cantidad+1

def descifrarArchivos(archivos):

    for archivo_obj in archivos: 
        archivo_obj.status = tk.Label(archivo_obj.frame, text="Desencriptado", font=("Helvetica", 12), background="red", fg="white")
        archivo_obj.status.grid(row=0, column=0, padx=20,pady=5)

        escribirLog("Descencriptando archivo "+str(archivo_obj.enc))
        escribirLog("Descencriptando con llave: "+ str(archivo_obj.keyPath))

        resultado = desencriptar(archivo_obj.encPath,archivo_obj.keyPath,archivo_obj.pos, archivo_obj.format)

        escribirLog("La desencriptacion ha sido: " + str(resultado))
    
    archivos_seleccionados.clear()

def cifrar(ruta,cantidad):
    return encriptar(ruta,cantidad)

def cifrarArchivo(archivo_obj):
    global ventana

    archivo_obj.frame = tk.Frame(ventana, borderwidth=1, relief="flat")
    archivo_obj.frame.place(width=width,height=height/20,x=0, y=(height/20) * (cantidad) + 10)

    archivo_obj.status = tk.Label(archivo_obj.frame, text="Encriptado", font=("Helvetica", 14), background="green", fg="white")
    archivo_obj.status.grid(row=0, column=0,pady=5)

    archivo_obj.label = tk.Label(archivo_obj.frame, text=archivo_obj.nombre, font=("Helvetica", 14))
    archivo_obj.label.grid(row=0, column=1,pady=5)

    if(archivo_obj.size<1000000):
        archivo_obj.sizeLabel = tk.Label(archivo_obj.frame, text=str(archivo_obj.size), font=("Helvetica", 10), background="#36ff6f", fg="white")
        archivo_obj.sizeLabel.grid(row=0, column=2,pady=5)
    if(archivo_obj.size<50000000 & archivo_obj.size>=1000001):
        archivo_obj.sizeLabel = tk.Label(archivo_obj.frame, text=str(archivo_obj.size), font=("Helvetica", 10), background="#ffbf36", fg="white")
        archivo_obj.sizeLabel.grid(row=0, column=2,pady=5)
    if(archivo_obj.size>50000001):
        archivo_obj.sizeLabel = tk.Label(archivo_obj.frame, text=str(archivo_obj.size), font=("Helvetica", 10), background="#ff3936", fg="white")
        archivo_obj.sizeLabel.grid(row=0, column=2,pady=5)




    actualizarUI()

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

    estilo = ttk.Style()
    estilo.theme_use('clam')
    estilo.configure('cargar.TButton',
                    borderwidth=0,
                    font=("Helvetica", 16, "normal"))

    # Botón para cargar un archivo
    cargar_button = ttk.Button(ventana, text="Encriptar Archivo",style= "cargar.TButton", command=cargar_archivo)
    cargar_button.place(x=50, y=(height/20) * (cantidad+1) + 10)

    if(cantidad>=0):
        descifrar_button = ttk.Button(ventana, text='Descifrar Archivos', style='cargar.TButton', command=lambda a=archivos_seleccionados: descifrarArchivos(a))
        descifrar_button.place(x=250, y=(height/20) * (cantidad+1) + 10)

def iniciar_ventana():
    global ventana
    createVentana()
    limpiar_cache()    
    escribirLog("----------------INICIANDO EL PROGRAMA--------------")
    ventana.mainloop()

def ventanaUser():
    global ventana

    estilo = ttk.Style()
    estilo.theme_use('clam')
    estilo.configure('cargar.TButton',
                    borderwidth=2,
                    background="white",
                    font=("Helvetica", 16, "normal"))
    estilo.configure('leer.TButton',
                    font=("Helvetica", 16, "normal"))
    estilo.configure('submit.TButton',
                     background="#36ff6f",
                    font=("Helvetica", 16, "bold"))

    text = ttk.Label(ventana, text="Ingrese el Usuario",style= "leer.TButton") 
    text.place(x=width/2 - 130 ,y=height/10 * 1.5,width=300)
    user = ttk.Entry(ventana, font=("Helvetica", 12, "normal"),style= "cargar.TButton")
    user.place(x=width/2 - 130 ,y=height/10 * 2,width=300)
    text2 = ttk.Label(ventana, text="Ingrese la contraseña",style= "leer.TButton") 
    text2.place(x=width/2 - 130 ,y=height/10 * 2.5,width=300)
    password = ttk.Entry(ventana,font=("Helvetica", 12, "normal"),style= "cargar.TButton")
    password.place(x=width/2 - 130 ,y=height/10 * 3,width=300)
    submitUser = ttk.Button(ventana, text="Ingresar",style= "submit.TButton" ,command=submit_User)
    submitUser.place(x=width/2 - 60 ,y=height/10 * 5)
    text3 = ttk.Label(ventana, text="Desarrollado por: ",style= "leer.TButton") 
    text3.place(x=width/2 - 130 ,y=height/10 * 7,width=300)
    text3 = ttk.Label(ventana, text="Christian Camelo, Javier Escutia, Guillermo Sansano, Mattia Sorella",style= "leer.TButton") 
    text3.place(x=200,y=height/10 * 7)

def ventanaProgram():
    global ventana
    ventana = tk.Tk()
    ventana.title("Cifrado y Descifrado")
    ventana.minsize(width,height)
    ventana.maxsize(width,height)
    ventana.geometry("0x0+524+128")
    actualizarUI()

def submit_User():
    ventana.destroy()
    ventanaProgram()

def createVentana():
    global ventana
    ventana = tk.Tk()
    ventana.title("Cifrado y Descifrado")
    ventana.minsize(width,height)
    ventana.maxsize(width,height)
    ventana.geometry("0x0+524+128")
    text = tk.Label(ventana, text="APLICACIÓN DE ENCRIPTACION",font=("Helvetica", 16, "bold"))
    text.place(x=width/2 - 150,y=height/10 * 0.5)
    ventanaUser()

iniciar_ventana()