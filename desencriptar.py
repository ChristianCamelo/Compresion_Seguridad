import os
from Crypto.Cipher import AES

def desencriptar(ruta_archivo, ruta_llave, cont, formato_archivo):

    desencriptado = False
    modo_desencriptar = AES.MODE_CTR

    with open(ruta_llave, 'rb') as key:
        clave_bruta = key.read()
        print(clave_bruta)
        clave = clave_bruta[:16]
        nonce = clave_bruta[-8:]

    with open(ruta_archivo, 'rb') as f:
        datos_encriptados = f.read()

    # with open(ruta_nonce, 'rb') as n:
    #     nonce = n.read()


    objeto_desencriptador = AES.new(clave, modo_desencriptar, nonce=nonce)

    datos_desencriptados = objeto_desencriptador.decrypt(datos_encriptados)
    #print("Datos desencriptados:", ruta_archivo)  # Agregar esta línea para verificar los datos desencriptados

    #archivo_original = unpad_fichero(datos_desencriptados)
    #print("Datos originales:", datos_desencriptados)  # Agregar esta línea para verificar los datos originales

    archivo_desencriptado_guardado = guardar_archivo_desencriptado(datos_desencriptados, cont, formato_archivo)

    if archivo_desencriptado_guardado:
        desencriptado = True

    return desencriptado


def guardar_archivo_desencriptado(datos_desencriptados, cont, formato):
    guardado = False
    ruta_archivos_desencriptados = os.path.join(os.getcwd(), 'archivos_desencriptados')
    ruta_archivo = os.path.join(ruta_archivos_desencriptados, 'archivo_' + str(cont)+ '.' + formato) #Cambiar

    with open(ruta_archivo, 'wb') as a:
        a.write(datos_desencriptados)

    if os.path.exists(ruta_archivo):
        guardado = True

    return guardado

# def unpad_fichero(data):
#     last_byte = data[-1]
#     return data[:-last_byte]