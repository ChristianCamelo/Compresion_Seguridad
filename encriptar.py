import base64
import os
import json
import hashlib
from utilities import escribirLog
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes # para generar la clave y el IV
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

#------------------------------------------------------------------------------------------------------------------------------------
# FUNCIÓN PARA ENCRIPTAR
#------------------------------------------------------------------------------------------------------------------------------------
def encriptar(fichero):

    cont = count(DIR_ENC)
    # ---------------- OBTENER FORMATO ---------------------------
    format = fichero[-3:]
    # --------------- ENCRIPTAR LA KEY CON LA KPUB ---------------
    key = get_random_bytes(16)

    with open('config.json', 'r') as file:
        data = json.load(file) 
        public_key_str = data.get('k_publica')
        public_key_pem = reverse_formater64(public_key_str)
        public_key = serialization.load_pem_public_key(public_key_pem, backend=default_backend())
        
    encrypted_key = public_key.encrypt(
        key, 
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    # ---------------- ENCRIPTAR OBJETO CON KEY SIN ENCRIPTAR ---------
    crypterObj = AES.new(key, CRYPT_MODE)
    nonce = crypterObj.nonce

    with open(fichero, 'rb') as f:
        fichero_a_encriptar = f.read()

    fichero_encriptado = crypterObj.encrypt(fichero_a_encriptar)
    archivo_encriptado_guardado = guardar_archivo_encriptado(fichero_encriptado,cont)

    # ------------------ ALMACENAR KEY ENCRIPTADA ----------------------
    guardarKey(encrypted_key, nonce,format , cont)

    return archivo_encriptado_guardado

def encriptarCompartido(fichero, kpub):

    # ---------------- OBTENER FORMATO ---------------------------
    format = fichero[-3:]
    # --------------- ENCRIPTAR LA KEY CON LA KPUB ---------------
    key = get_random_bytes(16)

    public_key_str = kpub
    public_key_pem = reverse_formater64(public_key_str)
    public_key = serialization.load_pem_public_key(public_key_pem, backend=default_backend())
        

    encrypted_key = public_key.encrypt(
        key, 
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    crypterObj = AES.new(key, CRYPT_MODE)
    nonce = crypterObj.nonce

    with open(fichero, 'rb') as f:
        fichero_a_encriptar = f.read()

    fichero_encriptado = crypterObj.encrypt(fichero_a_encriptar)
    fichero_encriptado_str = formater64(fichero_encriptado)

    # ------------------ ALMACENAR KEY ENCRIPTADA ----------------------

    formatParsed = format
    while len(formatParsed) < 10:
        # --------- SE AGREGAN SIMBOLOS $ PARA COMPLETAR EL ARRAY DEL FORMATO------------
        formatParsed=formatParsed+'$'

    llave_generada_str = formater64(encrypted_key) + formater64(nonce) + formatParsed

    return (fichero_encriptado_str,llave_generada_str)

#------------------------------------------------------------------------------------------------------------------------------------
# FUNCIÓN PARA GUARDAR EL ARCHIVO ENCRIPTADO: Guarda cada archivo en la carpeta archivos_encriptados
#------------------------------------------------------------------------------------------------------------------------------------
def guardar_archivo_encriptado(fichero,cont):

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
    return ruta_archivo

#------------------------------------------------------------------------------------------------------------------------------------
# FUNCIÓN PARA GUARDAR LA LLAVE: Guarda cada llave en un fichero binario guardado siguiendo el formato: 'llave' + contador + '.bin'
#------------------------------------------------------------------------------------------------------------------------------------
def guardarKey(key, nonce, format,cont):
    success = False
    ruta_keys = os.path.join(os.getcwd(), 'keys')
    ruta_archivo = os.path.join(ruta_keys, 'key' + str(cont) + '.bin')
    formatParsed = format
    while len(formatParsed) < 10:
        # --------- SE AGREGAN SIMBOLOS $ PARA COMPLETAR EL ARRAY ------------
        formatParsed=formatParsed+'$'
    # Escribiendo la llave
    with open(ruta_archivo, 'ab') as ficheroKeys:
        ficheroKeys.write(key)
        ficheroKeys.write(nonce)
        ficheroKeys.write(formatParsed.encode('utf-8'))
    # Comprobando que el archivo existe
    with open(ruta_archivo, 'rb') as b:
        data = b.read()
        # print(data)
        if len(data) > 0 and len(data) <= 34:
            success = True
        else:
            success = False
    return success

# -------------- HERRAMIENTA AUXILIAR BASE64 -----------------
def formater64(data):
    return base64.b64encode(data).decode('utf-8')

def reverse_formater64(encoded_data):
    return base64.b64decode(encoded_data.encode('utf-8'))

def count(ruta_directorio):

    lista_elementos = os.listdir(ruta_directorio)
    cantidad_elementos = len(lista_elementos)
    
    return cantidad_elementos
