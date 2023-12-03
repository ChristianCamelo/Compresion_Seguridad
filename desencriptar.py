import base64
import os
import json
from Crypto.Cipher import AES
from shutil import rmtree

from cryptography.hazmat.primitives import serialization,hashes ,padding
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def desencriptar(archivo):

    # ------------ BUSCAR LAS RUTAS DEL ARCHIVO -------------------
    ruta_archivo = archivo.encPath
    ruta_llave = archivo.keyPath
    cont = archivo.index
    desencriptado = False
    modo_desencriptar = AES.MODE_CTR
    # -------------- DESMONTAR LA KEY DEL OBJETO -------------------
    with open(ruta_llave, 'rb') as key:
        key_bruta = key.read()
        encrypted_key = key_bruta[:256]
        nonce = key_bruta[256:264]
        format = ''

        formato_archivo = list(key_bruta[264:].decode('utf-8'))
        for item in formato_archivo:
            if item!= "$":
                format+=item
    # ---------------- DESMONTAR EL OBJETO --------------------------
    with open(ruta_archivo, 'rb') as f:
        datos_encriptados = f.read()

    ############################# DESCENCRIPTAR LLAVE ##############################
    
    # print("llave bruta:",len(key_bruta))
    # print("llave encriptada:",len(encrypted_key))
    # print("nonce:",len(nonce))
    # print("format:",len(formato_archivo))

    with open('config.json', 'r') as file:
        data = json.load(file) 
        private_key_str = data.get('kpriv')
        private_key_pem = reverse_formater64(private_key_str)
        #print(private_key_pem)
        private_key = serialization.load_pem_private_key(private_key_pem, password=None, backend=default_backend())

    print("encriptada_leida :",encrypted_key)
    key = private_key.decrypt(
        encrypted_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    #print("llave: " + formater64(key))
    #print("llave encriptada: " + formater64(encrypted_key))

    # ------------------ DESENCRIPTAR EL OBJETO ------------------------
    crypterObj = AES.new(key, modo_desencriptar, nonce=nonce)
    datos_desencriptados = crypterObj.decrypt(datos_encriptados)
    
    archivo_desencriptado_guardado = guardar_archivo_desencriptado(datos_desencriptados, cont, format)

    if archivo_desencriptado_guardado:
        desencriptado = True

    #print("archivo: "+ formater64(datos_desencriptados))
    #print("archivo encriptado: "+ formater64(datos_encriptados))

    # -------------------- ELIMINAR KEY Y OBJETO ENCRIPTADO --------------
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

# -------------- HERRAMIENTA AUXILIAR BASE64 -----------------
def formater64(data):
    return base64.b64encode(data).decode('utf-8')

def reverse_formater64(encoded_data):
    return base64.b64decode(encoded_data.encode('utf-8'))