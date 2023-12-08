import hashlib
import base64
import json
import requests
import bcrypt
import tkinter as tk
from tkinter import ttk
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from cryptography.hazmat.primitives import serialization,hashes ,padding
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

SERVER_URL = "http://127.0.0.1:5000"
CRYPTERMODE = AES.MODE_CTR

def register(user,password):
    
    print(type(password))

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    # Obtener la clave pública correspondiente
    public_key = private_key.public_key()

    # Serializar la clave privada en formato PEM
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )

    # Serializar la clave pública en formato PEM
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    #----RSA KEYS QUEDA EN FORMATO STR--------------
    public_key_str = formater64(public_key_pem)
    private_key_str = formater64(private_key_pem)

    # ------------GENERAR KLOGIN KDATOS-------------------------
    sha256_hash = hashlib.sha256(password.encode()).hexdigest()
    k_login = sha256_hash[:32]
    k_datos = sha256_hash[-32:]

    # -------------- ENCRIPTART KPRIV -------------------------
    crypter = AES.new(k_datos.encode(), CRYPTERMODE , nonce=b'0')
    private_key_bytes = reverse_formater64(private_key_str)
    private_key_crypted = crypter.encrypt(private_key_bytes)
    private_key_crypted_str = formater64(private_key_crypted)

    # ------------ PAQUETE DE LLAVES A SERVIDOR ----------------
    data_server={
        "user":user,
        "k_login":k_login,
        "k_publica":public_key_str,
        "k_privada":private_key_crypted_str
    }
    print("paquete",data_server)
    response = requests.post(SERVER_URL+"/registrar", json=data_server)
    response_data = response.json()

    # --------------- MANEJAR RESPUESTAS --------------------
    if response.status_code == 200: # registrado correctamente
        print("Datos enviados correctamente al endpoint en la nube.")
        # --------------- ALMACENA LAS LLAVES DE FORMA LOCAL --------------
        data = {
            "user":user,
            "k_login":response_data.get('k_login'),
            "k_datos":k_datos,
            "k_publica": public_key_str,
            "k_privada": private_key_str
        }
        with open('config.json', 'w') as json_file:
            json.dump(data, json_file, indent=4)
        return True
    else:
        print("Error al enviar los datos al endpoint en la nube. Código de estado:", response.status_code)
        return False   

def login(user,password):

    sha256_hash = hashlib.sha256(password.encode()).hexdigest()
    k_login = sha256_hash[:32]
    k_datos = sha256_hash[-32:]

    print(k_login)

    payload = {
        'user': user,
        'k_login' : k_login
    }

    # ------------- LLAMADA AL SERVIDOR -------------
    response = requests.post(SERVER_URL+"/login", json=payload)
    response_data = response.json()
    public_key_str = response_data.get('k_publica')
    private_key_crypted_str = response_data.get('k_privada')
    k_login = response_data.get('k_login')


    # ------------------- PROCESO DE DESENCRIPTACION DE LLAVE KPRIVKDATOS ------------------
    private_key_crypted = reverse_formater64(private_key_crypted_str)
    crypter = AES.new(k_datos.encode(), CRYPTERMODE, nonce=b'0')
    private_key = crypter.decrypt(private_key_crypted)
    private_key_str = formater64(private_key)
    
    # --------------------- ALMACENA LAS LLAVES DE FORMA LOCAL --------------
    data={
        "user":user,
        "k_login":k_login,
        "k_datos":k_datos,
        "k_publica": public_key_str,
        "k_privada": private_key_str
    }
    with open('config.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)
    # --------------- MANEJAR RESPUESTAS --------------------
    if response.status_code == 200: # registrado correctamente
        return True
    else:    
        print("Error al enviar los datos al endpoint en la nube. Código de estado:", response.status_code)
        return False

def getUser(user):
    payload ={
        'user': user,
    }
    response = requests.get(SERVER_URL+"/getpublickey", json=payload)
    response_data = response.json()
    public_key_str = response_data.get("k_publica")
    print("PUBLIC KEY",public_key_str)
    return public_key_str

# -------------- HERRAMIENTA AUXILIAR BASE64 -----------------
def formater64(data):
    return base64.b64encode(data).decode('utf-8')

def reverse_formater64(encoded_data):
    return base64.b64decode(encoded_data.encode('utf-8'))