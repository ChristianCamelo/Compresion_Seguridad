import os
from principal import escribirLog
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes # para generar la clave y el IV

#------------------------------------------------------------------------------------------------------------------------------------
# FUNCIÓN PARA ENCRIPTAR
#------------------------------------------------------------------------------------------------------------------------------------
def encriptar(fichero, cont):
    encriptado = False
    modo_encriptar = AES.MODE_CTR
    iv = get_random_bytes(16)
    key = get_random_bytes(16)
    llave_guardada = guardarKey(key, cont)
    iv_guardadi = guardarIV(iv, cont)
    objeto_ecriptador = AES.new(key, modo_encriptar)
    with open(fichero, 'rb') as f:
        fichero_a_encriptar = f.read()
        fichero_padeado = pad_fichero(fichero_a_encriptar)
    fichero_encriptado = objeto_ecriptador.encrypt(fichero_padeado)
    archivo_encriptado_guardado = guardar_archivo_encriptado(fichero_encriptado, cont)
    escribirLog("prueba encriptación de un fichero en PDF")
    if llave_guardada and archivo_encriptado_guardado:
        encriptado = True
    else:
        encriptado = False
    return encriptado

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
    escribirLog("prueba de guardar un archivo encripado pdf")
    return guardado

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
        else:
            success = False
    print(success)
    return success

#------------------------------------------------------------------------------------------------------------------------------------
# FUNCIÓN PARA GUARDAR EL IV: Guarda cada iv en un fichero binario guardado siguiendo el formato: 'iv' + contador + '.bin'
#------------------------------------------------------------------------------------------------------------------------------------
def guardarIV(iv, cont):
    guardado = False
    ruta_iv = os.path.join(os.getcwd(), 'iv')
    ruta_archivo = os.path.join(ruta_iv, 'iv' + str(cont) + 'bin')

    # Escribiendo el IV
    with open(ruta_archivo, 'ab') as fichero_iv:
        fichero_iv.write(iv)

    
    # Comprobando que el archivo existe
    with open(ruta_archivo, 'rb') as f:
        data = f.read()
        if len(data) > 0 and len(data) <= 16:
            guardado = True
        else:
            guardado = False
    print(guardado)
    return(guardado)

#------------------------------------------------------------------------------------------------------------------------------------
# FUNCIÓN PARA PONERLE PADDING AL FICHERO
#------------------------------------------------------------------------------------------------------------------------------------
def pad_fichero(fichero):
    while len(fichero) % 16 != 0:
        fichero = fichero + b'0' # Hay que añadir bits porque es un fichero
    return fichero