import tkinter as tk
import os
import shutil
from tkinter import filedialog
from tkinter import ttk
from encriptar import encriptar
from utilities import escribirLog
from desencriptar import desencriptar
from shutil import rmtree
from servicio_rest import subir_archivos, bajar_archivos

global ventana
global cantidad
cantidad = 0
width = 1000
height = 800

DIR_LOCAL = os.path.dirname(os.path.abspath(__file__))

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
    ruta_formatos = os.path.join(os.getcwd(), 'formatos')
    
    if archivo:
        archivo_obj = Archivo(archivo)
        archivo_obj.ruta = os.path.abspath(archivo)
        archivo_obj.pos=cantidad
        archivo_obj.enc = cifrar(archivo_obj.ruta, cantidad)
        archivo_obj.size = os.path.getsize(archivo_obj.enc)
        archivo_obj.encPath = os.path.join(archivo_obj.enc)
        archivo_obj.format = (archivo_obj.ruta).split(".")[-1]


        ruta_formato = os.path.join(ruta_formatos, 'formato' + str(cantidad) + '.txt')
        with open(ruta_formato, 'w') as file:
            file.write(archivo_obj.format)

        archivo_obj.nombre = os.path.basename(archivo_obj.ruta)
        archivo_obj.keyPath = os.path.join(ruta_keys, 'llave' + str(archivo_obj.pos) + '.bin')

        escribirLog("Lectura: Ruta de archivo leido es: "+ archivo_obj.archivo)
        escribirLog("Escritura: Ruta de archivo cifrado es: "+ archivo_obj.enc)
        escribirLog("Escritura: Llave de archivo cifrado es: "+ archivo_obj.keyPath)
        
        mostrarCifrado(archivo_obj)
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

def mostrarCifrado(archivo_obj):
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


def limpiar_cache():
    # Eliminando directorios
    directorios_a_borrar = [
        "archivos_desencriptados",
        "archivos_encriptados",
        "keys",
        "formatos"
    ]
    for directorio in directorios_a_borrar:
        ruta_directorio = os.path.join(os.getcwd(), directorio)
        if os.path.exists(ruta_directorio):
            shutil.rmtree(ruta_directorio)
            print(f"Directorio '{ruta_directorio}' borrado exitosamente.")
        else:
            print(f"El directorio '{ruta_directorio}' no existe.")
    # Creadon directorios
    os.mkdir("archivos_desencriptados")
    os.mkdir("archivos_encriptados")
    os.mkdir("keys")
    os.mkdir("formatos")

archivos_seleccionados = []

def actualizarUI():

    estilo = ttk.Style()
    estilo.theme_use('clam')
    estilo.configure('cargar.TButton',
                    borderwidth=0,
                    font=("Helvetica", 16, "normal"))

    # Botón para cargar un archivo
    cargar_button = ttk.Button(ventana, text="Encriptar Archivo",style= "cargar.TButton", command=cargar_archivo)
    cargar_button.place(x=50,  y=height-80)

    # Botón para cargar un archivo
    subir_button = ttk.Button(ventana, text="Subir Archivos",style= "cargar.TButton", command=subir)
    subir_button.place(x=580,  y=height-80)

    # Botón para cargar un archivo
    descargar_button = ttk.Button(ventana, text="Descargar Archivos",style= "cargar.TButton", command=descargar)
    descargar_button.place(x=750,  y=height-80)

    if(cantidad>=0):
        descifrar_button = ttk.Button(ventana, text='Descifrar Archivos', style='cargar.TButton', command=lambda a=archivos_seleccionados: descifrarArchivos(a))
        descifrar_button.place(x=250, y=height-80)

    leerLocales()

def iniciar_ventana():
    global ventana
    createVentana()
    #limpiar_cache()    
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
    limpiar_cache()
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

def leerLocales():
    global cantidad
    cantidad = 0
    directorio_local = os.path.join(DIR_LOCAL, 'archivos_encriptados')
    directorio_local_llaves = os.path.join(DIR_LOCAL, 'keys')
    directorios = os.listdir(directorio_local)

    print(f'Ruta de archivos encriptados: {directorio_local}')
    print(f'Ruta de llaves: {directorio_local_llaves}')

    for index, directorio in enumerate(directorios):

        ruta_archivo = os.path.join(directorio_local, 'archivo' + str(index) + '.enc')
        ruta_llave = os.path.join(directorio_local_llaves, 'llave' + str(index) + '.bin')
        ruta_formatos = os.path.join(os.getcwd(), 'formatos')
        
        archivo = ruta_archivo

        archivo_obj = Archivo(archivo)
        archivo_obj.ruta = os.path.abspath(archivo)
        archivo_obj.pos=cantidad
        archivo_obj.enc = ruta_archivo
        archivo_obj.size = os.path.getsize(archivo_obj.enc)
        archivo_obj.encPath = os.path.join(archivo_obj.enc)

        ruta_formato = os.path.join(ruta_formatos, 'formato' + str(cantidad) + '.txt')
        with open(ruta_formato, 'r') as f:
            formato_bruto = f.read()
            archivo_obj.format = str(formato_bruto[2:-1])
            print("FORMATO ES: "+ archivo_obj.format)

        archivo_obj.nombre = os.path.basename(archivo_obj.ruta)
        archivo_obj.keyPath = ruta_llave
        
        mostrarCifrado(archivo_obj)
        archivos_seleccionados.append(archivo_obj)
        cantidad = cantidad+1

    cantidad = len(directorios)

def descargar():
    bajar_archivos()
    actualizarUI()

def subir():
    subir_archivos()
    actualizarUI()


iniciar_ventana()