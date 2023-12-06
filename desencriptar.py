import base64
import os
import json
from Crypto.Cipher import AES
from shutil import rmtree

from cryptography.hazmat.primitives import serialization,hashes ,padding
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

DIR_LOCAL = os.path.dirname(os.path.abspath(__file__))
DIR_KEYS = os.path.join(DIR_LOCAL, 'keys')
DIR_KEYS_SHARED = os.path.join(DIR_LOCAL, 'keys_compartidos')
DIR_FILES = os.path.join(DIR_LOCAL, 'archivos_desencriptados')
DIR_FILES_SHARED = os.path.join(DIR_LOCAL, 'archivos_desencriptados_compartidos')
DIR_ENC = os.path.join(DIR_LOCAL, 'archivos_encriptados')
DIR_ENC_SHARED = os.path.join(DIR_LOCAL, 'archivos_encriptados_compartidos')
CRYPT_MODE = AES.MODE_CTR

def desencriptarPropios():

    archivos = os.listdir(DIR_ENC)
    for index,archivo in enumerate(archivos):
        # ------------ BUSCAR LAS RUTAS DEL ARCHIVO -------------------
        ruta_archivo = os.path.join(DIR_ENC, 'archivo' + str(index) + '.enc')
        ruta_llave = os.path.join(DIR_KEYS, 'key' + str(index) + '.bin')
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
        with open('config.json', 'r') as file:
            data = json.load(file) 
            private_key_str = data.get('k_privada')
            private_key_pem = reverse_formater64(private_key_str)
            print("Key privada",private_key_pem)
            private_key = serialization.load_pem_private_key(private_key_pem, password=None, backend=default_backend())

        key = private_key.decrypt(
            encrypted_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        # ------------------ DESENCRIPTAR EL OBJETO ------------------------
        crypterObj = AES.new(key, CRYPT_MODE, nonce=nonce)
        archivo_desencriptado = crypterObj.decrypt(datos_encriptados)
        archivo = save_own(archivo_desencriptado, index, format)

        # -------------------- ELIMINAR KEY Y OBJETO ENCRIPTADO --------------
        os.remove(ruta_archivo)
        os.remove(ruta_llave)

def desencriptarCompartidos():

    archivos = os.listdir(DIR_ENC_SHARED)
    for index,archivo in enumerate(archivos):
        # ------------ BUSCAR LAS RUTAS DEL ARCHIVO -------------------
        ruta_archivo = os.path.join(DIR_ENC_SHARED, 'archivo' + str(index) + '.enc')
        ruta_llave = os.path.join(DIR_KEYS_SHARED, 'key' + str(index) + '.bin')
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
        with open('config.json', 'r') as file:
            data = json.load(file) 
            private_key_str = data.get('k_privada')
            private_key_pem = reverse_formater64(private_key_str)
            private_key = serialization.load_pem_private_key(private_key_pem, password=None, backend=default_backend())

        key = private_key.decrypt(
            encrypted_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        # ------------------ DESENCRIPTAR EL OBJETO ------------------------
        crypterObj = AES.new(key, CRYPT_MODE, nonce=nonce)
        archivo_desencriptado = crypterObj.decrypt(datos_encriptados)
        archivo = save_ext(archivo_desencriptado, index, format)
        # -------------------- ELIMINAR KEY Y OBJETO ENCRIPTADO --------------
        os.remove(ruta_archivo)
        os.remove(ruta_llave)

def save_own(archivo_desencriptado, cont, formato):

    guardado = False
    cont = count(DIR_FILES)
    ruta_archivo = os.path.join(DIR_FILES, 'archivo' + str(cont)+ '.' + formato) 
    with open(ruta_archivo, 'wb') as a:
        a.write(archivo_desencriptado)

    if os.path.exists(ruta_archivo):
        guardado = True

    return guardado

def save_ext(archivo_desencriptado, cont, formato):
    guardado = False
    ruta_archivo = os.path.join(DIR_FILES_SHARED, 'archivo' + str(cont)+ '.' + formato) 

    with open(ruta_archivo, 'wb') as a:
        a.write(archivo_desencriptado)

    if os.path.exists(ruta_archivo):
        guardado = True

    return guardado

# -------------- HERRAMIENTA AUXILIAR BASE64 -----------------
def formater64(data):
    return base64.b64encode(data).decode('utf-8')

def reverse_formater64(encoded_data):
    return base64.b64decode(encoded_data.encode('utf-8'))

def count(ruta_directorio):

    lista_elementos = os.listdir(ruta_directorio)
    cantidad_elementos = len(lista_elementos)
    
    return cantidad_elementos