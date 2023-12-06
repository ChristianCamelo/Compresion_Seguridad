import tkinter as tk
import os
import shutil
from encriptar import encriptar
from desencriptar import desencriptarPropios,desencriptarCompartidos
from tkinter import ttk, filedialog
import turtle
from shutil import rmtree
from servicios_auth import login,register,getUser
from servicios_crud import downloadOwn,downloadShared,upload,shareFile,getNames

global ventana
global cantidad

global encriptados
global archivos
global llaves
global subidos
global compartidos

cantidad = 0
width = 1000
height = 800

DIR_LOCAL = os.path.dirname(os.path.abspath(__file__))
DIR_KEYS = os.path.join(DIR_LOCAL, 'keys')
DIR_FILES = os.path.join(DIR_LOCAL, 'archivos_desencriptados')
DIR_ENC = os.path.join(DIR_LOCAL, 'archivos_encriptados')

FONT = ("Helvetica", 14, "normal")
FONT_S = ("Helvetica", 10, "normal")
LINE_H = 30

class Archivo:
    def __init__(self, archivo):
        self.archivo = archivo
        self.index = len(encriptados)
        self.filePath = os.path.abspath(self.archivo)
        self.encPath = os.path.join(DIR_ENC, 'archivo' + str(len(encriptados)) + '.enc')
        self.keyPath = os.path.join(DIR_KEYS, 'llave' + str(len(encriptados)) + '.bin')

def limpiar_cache():
    # Eliminando directorios
    directorios_a_borrar = [
        "archivos_desencriptados",
        "archivos_encriptados",
        "archivos_encriptados_compartidos",
        "keys_compartidos",
        "keys"
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
    os.mkdir("archivos_encriptados_compartidos")
    os.mkdir("keys_compartidos")

def iniciar_ventana():
    global ventana
    global encriptados
    global compartidos
    global subidos
    
    encriptados=[]
    subidos=[]
    compartidos =[]

    limpiar_cache()
    createVentana()
    ventanaHome()
    # #limpiar_cache()    
    # escribirLog("----------------INICIANDO EL PROGRAMA--------------")
    ventana.mainloop()

def ventanaHome(): #VENTANA DE IDENTIFICACION
    frame = createFrame()
    estilo = ttk.Style()
    estilo.theme_use('clam')
    estilo.configure('cargar.TButton',
                    borderwidth=2,
                    background="white",
                    font=(FONT, 16, "normal"))
    estilo.configure('leer.TButton',
                    font=(FONT, 16, "normal"))
    estilo.configure('submit.TButton',
                    background="#36ff6f",
                    font=FONT)
    estilo.configure('login.TButton',
                    background="#1100FF",
                    font=FONT)

    text = ttk.Label(frame, text="Ingrese el Usuario",style= "leer.TButton") 
    text.place(x=width/2 - 130 ,y=height/10 * 1.5,width=300)
    user = ttk.Entry(frame, font=(FONT, 12, "normal"),style= "cargar.TButton")
    user.place(x=width/2 - 130 ,y=height/10 * 2,width=300)
    text2 = ttk.Label(frame, text="Ingrese la contraseña",style= "leer.TButton") 
    text2.place(x=width/2 - 130 ,y=height/10 * 2.5,width=300)
    password = ttk.Entry(frame,font=(FONT, 12, "normal"),style= "cargar.TButton")
    password.place(x=width/2 - 130 ,y=height/10 * 3,width=300)
    text = tk.Label(frame, text="APLICACIÓN DE ENCRIPTACION",font=FONT)
    text.place(x=width/2 - 150,y=height/10 * 0.5)

    loginUser = ttk.Button(frame, text="Login",style= "login.TButton" ,command=lambda:loguear(user,password))
    loginUser.place(x=width/2 - 60 ,y=height/10 * 5)

    submitUser = ttk.Button(frame, text="Sign up",style= "submit.TButton" ,command=lambda:registrar(user,password))
    submitUser.place(x=width/2 - 60 ,y=height/10 * 5.5)

    text3 = ttk.Label(frame, text="Desarrollado por: ",style= "leer.TButton") 
    text3.place(x=width/2 - 130 ,y=height/10 * 7,width=300)
    text3 = ttk.Label(frame, text="Christian Camelo, Javier Escutia, Guillermo Sansano, Mattia Sorella",style= "leer.TButton") 
    text3.place(x=200,y=height/10 * 7)

def registrar(entry_u,entry_pwd):
    user = entry_u.get()
    password = entry_pwd.get()

    print(f'usuario: {user}/ password: {password}')

    if(register(user,password)==True):
        ventanaProgram()

def loguear(entry_u,entry_pwd):
    user = entry_u.get()
    password = entry_pwd.get()

    print(f'usuario: {user}/ password: {password}')

    if(login(user,password)==True):
        ventanaProgram()

def createVentana(): # INICIALIZACION DE TKINTER
    global ventana
    ventana = tk.Tk()
    ventana.title("Cifrado y Descifrado")
    ventana.minsize(width,height)
    ventana.maxsize(width,height)
    ventana.geometry("0x0+524+128")

def createFrame(): # CUADRO DE INTERFAZ
    frame = tk.Frame(ventana, borderwidth=1, relief="flat")
    frame.place(width=width,height=height,x=0, y=0)
    for widgets in frame.winfo_children():
      widgets.destroy()
    return frame

def ventanaProgram():
    global encriptados
    global subidos
    global user
    # ------------ VENTANA DE LOCALES -------------
    localFrame = tk.Frame(ventana,bg='#1010FF', borderwidth=1, relief="flat")
    localFrame.place(width=width/3,height=height,x=0, y=0)
    text = tk.Label(localFrame, text="Almacenamiento local",font=FONT)
    text.place(x=10,y=10)
    text = tk.Label(localFrame, text="Encriptados",font=FONT_S)
    text.place(x=10,y=50)
    # DIBUJAR ARCHIVOS ENCRIPTADOS EN LISTA
    for index,item in enumerate(getNames(DIR_ENC)):
        text = tk.Label(localFrame, text=item,font=(FONT, 10, "normal"))
        text.place(x=10,y=80+(LINE_H*index))
    text = tk.Label(localFrame, text="Desencriptados",font=FONT_S)
    text.place(x=10,y=height/2)
    # DIBUJAR ARCHIVOS DESENCRIPTADOS EN LISTA
    for index,item in enumerate(getNames(DIR_FILES)):
        text = tk.Label(localFrame, text=item,font=(FONT, 10, "normal"))
        text.place(x=10,y=(height/2+(30))+(LINE_H*index))
    nuevoBt = ttk.Button(localFrame, text="Nuevo archivo",command=lambda:crypt())
    nuevoBt.place(x=10,y=height-50)
    des = ttk.Button(localFrame, text="Desencriptar archivos",command=lambda:decrypt())
    des.place(x=190,y=height-50)

    # ------------ VENTANA DE NUBE PERSONAL -------------
    netFrame = tk.Frame(ventana,bg='#10AA10', borderwidth=1, relief="flat")
    netFrame.place(width=width/3,height=height,x=(width/3)*1, y=0)
    text = tk.Label(netFrame, text="Almacenamiento online",font=FONT)
    text.place(x=10,y=10)
    # DIBUJAR ARCHIVOS SUBIDOS EN LISTA
    for index,item in enumerate(subidos):
        text = tk.Label(netFrame, text=item,font=(FONT, 10, "normal"))
        text.place(x=10,y=80+(LINE_H*index))
    bajarBt = ttk.Button(netFrame, text="Bajar archivos",command=lambda:downloadOwn())
    bajarBt.place(x=10,y=height-50)
    subirBt = ttk.Button(netFrame, text="Subir archivos",command=lambda:uploadLocal())
    subirBt.place(x=230,y=height-50)

    # ------------ VENTANA DE COMPARTIDOS -------------

    # COMPARTIDOS CONMIGO
    sharedFrameA = tk.Frame(ventana,bg='#AAFF22', borderwidth=1, relief="flat")
    sharedFrameA.place(width=width/3,height=height/2,x=width/3 * 2, y=0)
    text = tk.Label(sharedFrameA, text="Compartido conmigo",font=FONT)
    text.place(x=10,y=10)
    button = ttk.Button(sharedFrameA, text="Bajar archivos",command=lambda:downloadShared())
    button.place(x=10,y=(height/2)-50)

    # COMPARTIDOS POR MI
    sharedFrameB = tk.Frame(ventana,bg='#AA0022',  borderwidth=10, relief="flat")
    sharedFrameB.place(width=width/3,height=height/2,x=width/3 * 2, y=height/2)
    text = tk.Label(sharedFrameB, text="Compartidos",font=FONT)
    text.place(x=10,y=10)
    text = tk.Label(sharedFrameB, text="Archivo",font=FONT_S)
    text.place(x=10,y=10+LINE_H)
    text = tk.Label(sharedFrameB, text="Usuario",font=FONT_S)
    text.place(x=width/6,y=10+LINE_H)
        # DIBUJAR ARCHIVOS COMPARTIDOS EN LISTA
    for index,item in enumerate(compartidos):
        text = tk.Label(sharedFrameB, text=compartidos[index][0],font=(FONT, 10, "normal"))
        text.place(x=10,y=80+(LINE_H*index))
        text = tk.Label(sharedFrameB, text=compartidos[index][1],font=(FONT, 10, "normal"))
        text.place(x=width/6,y=80+(LINE_H*index))
    bajarBt = ttk.Button(sharedFrameB, text="Compartir",command=lambda:share())
    bajarBt.place(x=10,y=(height/2)-(60))

def crypt():
    archivo = tk.filedialog.askopenfilename()
    if archivo: 
        encriptar(archivo)
    ventanaProgram()

def decrypt():
    desencriptarPropios()
    ventanaProgram()

def share():
        global compartidos
        archivo = tk.filedialog.askopenfilename()
        if archivo: 
                user = tk.simpledialog.askstring("Receptor", "Ingresa el nombre del usuario")
                if user:
                    shareFile(archivo,user)
                    filename = archivo.split("/")[-1:]
                    file = [filename,user]
                    compartidos.append(file)
                    print("Shared",compartidos)
        ventanaProgram()

def uploadLocal():
    upload()
    global subidos
    for index,item in enumerate(getNames(DIR_ENC)):
        subidos.append(item)
    ventanaProgram()
        

iniciar_ventana()