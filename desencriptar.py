import os
from Crypto.Cipher import AES
from shutil import rmtree

def desencriptar(archivo):

    ruta_archivo = archivo.encPath
    ruta_llave = archivo.keyPath
    cont = archivo.index

    desencriptado = False
    modo_desencriptar = AES.MODE_CTR

    with open(ruta_llave, 'rb') as key:
        clave_bruta = key.read()
        print(clave_bruta)
        clave = clave_bruta[:16]
        nonce = clave_bruta[-18:-10]
        format = ''

        formato_archivo = list(clave_bruta[-10:].decode('utf-8'))
        for item in formato_archivo:
            if item!= "$":
                format+=item

    with open(ruta_archivo, 'rb') as f:
        datos_encriptados = f.read()
        
    objeto_desencriptador = AES.new(clave, modo_desencriptar, nonce=nonce)

    datos_desencriptados = objeto_desencriptador.decrypt(datos_encriptados)

    archivo_desencriptado_guardado = guardar_archivo_desencriptado(datos_desencriptados, cont, format)

    if archivo_desencriptado_guardado:
        desencriptado = True

    os.remove(ruta_archivo)
    os.remove(ruta_llave)
    return desencriptado


def guardar_archivo_desencriptado(datos_desencriptados, cont, formato):
    guardado = False
    ruta_archivos_desencriptados = os.path.join(os.getcwd(), 'archivos_desencriptados')
    ruta_archivo = os.path.join(ruta_archivos_desencriptados, 'archivo_' + str(cont)+ '.' + formato) 

    with open(ruta_archivo, 'wb') as a:
        a.write(datos_desencriptados)

    if os.path.exists(ruta_archivo):
        guardado = True

    return guardado
