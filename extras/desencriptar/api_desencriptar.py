from cryptography.fernet import Fernet
from pathlib import Path

def desencriptar(archivo,clave):
    f = Fernet(clave)
    with open(archivo, 'rb') as file: #archivo abierto solo para lectura
        datos_encriptados = file.read()

    datos = f.decrypt(datos_encriptados)

    with open(archivo, 'wb') as file: #archivo abierto solo para escritura
        file.write(datos)         #escribimos los datos desencriptados

#############################################

def leerArchivo(archivo):
    stream = open(archivo,"rt",encoding="utf-8")
    print(stream.read())

def escribirArchivo(linea,archivo):
    with open(archivo,"a") as file: #argumento a = append o agregar
        file.write("\n"+linea)

def generar_clave():
    archivo = r'key.key'
    objetoArchivo = Path(archivo)
    if not objetoArchivo.is_file():
        clave = Fernet.generate_key()
        with open("key.key","wb") as key_file:
            key_file.write(clave)
    else:
        print("La clave ya existe")

def cargar_clave():
    return open("key.key","rb").read()

def encriptar(archivo,clave):
    f = Fernet(clave)
    with open(archivo, 'rb') as file: #archivo abierto solo para lectura
        datos = file.read()

    datos_encriptados = f.encrypt(datos)

    with open(archivo, 'wb') as file: #archivo abierto solo para escritura
        file.write(datos_encriptados) #escribimos los datos encriptados