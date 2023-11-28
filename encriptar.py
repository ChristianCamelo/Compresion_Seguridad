
import os
from utilities import escribirLog
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes # para generar la clave y el IV
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

#------------------------------------------------------------------------------------------------------------------------------------
# FUNCIÓN PARA ENCRIPTAR
#------------------------------------------------------------------------------------------------------------------------------------
def encriptar(fichero, cont):
    escribirLog("----------------INICIANDO ENCRIPTACION DE "+ fichero + "--------------")
    
    format = fichero[-3:]

    modo_encriptar = AES.MODE_CTR

    # --------------- PROTEGER LA LLAVE CON LA KPRIV ---------------
    key = get_random_bytes(16)
    with open('config.json', 'r') as config:
        data = config.read()
    kpriv = data.kpriv
    cipher = Cipher(algorithms.AES(kpriv), modes.ECB(), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_private_key = encryptor.update(key) + encryptor.finalize()

    objeto_ecriptador = AES.new(key, modo_encriptar)
    nonce = objeto_ecriptador.nonce
    print(len(nonce),type(nonce))
    print(key)
    print(nonce)
    llave_guardada = guardarKey(key, nonce,format , cont)
    print(llave_guardada)
    
    with open(fichero, 'rb') as f:
        fichero_a_encriptar = f.read()

    fichero_encriptado = objeto_ecriptador.encrypt(fichero_a_encriptar)
    archivo_encriptado_guardado = guardar_archivo_encriptado(fichero_encriptado, cont)
    escribirLog("Llave generada: "+ str(llave_guardada))
    escribirLog("----------------FINALIZANDO ENCRIPTACION DE "+ fichero + "--------------")
    return archivo_encriptado_guardado
#------------------------------------------------------------------------------------------------------------------------------------
# FUNCIÓN PARA GUARDAR EL ARCHIVO ENCRIPTADO: Guarda cada archivo en la carpeta archivos_encriptados
#------------------------------------------------------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------------------------------------------------------
# FUNCIÓN PARA GUARDAR EL ARCHIVO ENCRIPTADO: Guarda cada archivo en la carpeta archivos_encriptados
#------------------------------------------------------------------------------------------------------------------------------------
def guardar_archivo_encriptado(fichero, cont):

    guardado = False
    ruta_archivos_encriptados = os.path.join(os.getcwd(), 'archivos_encriptados')
    ruta_archivo = os.path.join(ruta_archivos_encriptados, 'archivo' + str(cont) + '.enc')

    # Escribiendo el archivo
    with open(ruta_archivo, 'wb') as a:
        a.write(fichero)

    # Comprobando que el archivo existe
    with open(ruta_archivo, 'rb') as b:
        data = b.read()
        if len(data) > 0:
            guardado = True
        else:
            guardado = False
    print(guardado)
    escribirLog("Encriptacion: Creando la ruta de guardado: "+ruta_archivo)
    return ruta_archivo

#------------------------------------------------------------------------------------------------------------------------------------
# FUNCIÓN PARA GUARDAR LA LLAVE: Guarda cada llave en un fichero binario guardado siguiendo el formato: 'llave' + contador + '.bin'
#------------------------------------------------------------------------------------------------------------------------------------
def guardarKey(key, nonce, format,cont):
    success = False
    ruta_keys = os.path.join(os.getcwd(), 'keys')
    ruta_archivo = os.path.join(ruta_keys, 'llave' + str(cont) + '.bin')
    formatParsed = format
    while len(formatParsed) < 10:
        formatParsed=formatParsed+'$'

    # Escribiendo la llave
    with open(ruta_archivo, 'ab') as ficheroKeys:
        ficheroKeys.write(key)
        ficheroKeys.write(nonce)
        ficheroKeys.write(formatParsed.encode('utf-8'))

    # Comprobando que el archivo existe
    with open(ruta_archivo, 'rb') as b:
        data = b.read()
        print(data)
        if len(data) > 0 and len(data) <= 34:
            success = True
            escribirLog("Encriptacion: Se ha generado la llave : "+ruta_archivo)
        else:
            success = False
    print(success)
    return success

