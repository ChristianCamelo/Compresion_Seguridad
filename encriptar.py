
import os
from principal import escribirLog
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes # para generar la clave y el IV

#------------------------------------------------------------------------------------------------------------------------------------
# FUNCIÓN PARA ENCRIPTAR
#------------------------------------------------------------------------------------------------------------------------------------
def encriptar(fichero, cont):
    escribirLog("----------------INICIANDO ENCRIPTACION DE "+ fichero + "--------------")
    modo_encriptar = AES.MODE_CTR
    iv = get_random_bytes(16)
    key = get_random_bytes(16)
    llave_guardada = guardarKey(key, cont)
    objeto_ecriptador = AES.new(key, modo_encriptar)
    with open(fichero, 'rb') as f:
        fichero_a_encriptar = f.read()
        # fichero_padeado = pad_fichero(fichero_a_encriptar)
    fichero_encriptado = objeto_ecriptador.encrypt(fichero_a_encriptar)
    archivo_encriptado_guardado = guardar_archivo_encriptado(fichero_encriptado, cont)
    escribirLog("Llave generada: "+ str(llave_guardada))
    escribirLog("----------------FINALIZANDO ENCRIPTACION DE "+ fichero + "--------------")
    return archivo_encriptado_guardado

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
def guardarKey(key, cont):
    success = False
    ruta_keys = os.path.join(os.getcwd(), 'keys')
    ruta_archivo = os.path.join(ruta_keys, 'llave' + str(cont) + '.bin')

    # Escribiendo la llave
    with open(ruta_archivo, 'ab') as ficheroKeys:
        ficheroKeys.write(key)
    
    # Comprobando que el archivo existe
    with open(ruta_archivo, 'rb') as b:
        data = b.read()
        if len(data) > 0 and len(data) <= 16:
            success = True
            escribirLog("Encriptacion: Se ha generado la llave : "+ruta_archivo)
        else:
            success = False
    print(success)
    return success

#------------------------------------------------------------------------------------------------------------------------------------
# FUNCIÓN PARA PONERLE PADDING AL FICHERO
#------------------------------------------------------------------------------------------------------------------------------------
# def pad_fichero(fichero):
#     while len(fichero) % 16 != 0:
#         fichero = fichero + b'0' # Hay que añadir bits porque es un fichero
#     return fichero