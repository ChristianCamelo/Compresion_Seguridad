import hashlib
import json
import requests
import bcrypt
from cryptography.hazmat.primitives import serialization,hashes ,padding
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

SERVER_URL = "http://127.0.0.1:8000"

def generate_keys(user,password):

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()

    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    sha256_hash = hashlib.sha256(password.encode()).hexdigest()
    k_login = sha256_hash[:32]
    k_datos = sha256_hash[-32:]
    k_login_bytes = bytes.fromhex(k_login)
    k_datos_bytes = bytes.fromhex(k_datos)

    # Aplicar relleno PKCS7 a los datos
    padder = padding.PKCS7(128).padder()  # Tamaño del bloque en bits (128 bits para AES)
    private_key_padded = padder.update(private_key_pem) + padder.finalize()

    # -------------- ENCRIPTACION DE KPRIV+KDATOS-------------------------
    cipher = Cipher(algorithms.AES(k_datos_bytes), modes.ECB(), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_private_key = encryptor.update(private_key_padded) + encryptor.finalize()

    k_login_hashed = bcrypt.hashpw(k_login.encode(), bcrypt.gensalt()).decode()


    # ------------ PAQUETE DE LLAVES A SERVIDOR ----------------
    data={
        "user":user,
        "klogin":k_login_hashed,
        "kpub":public_key_pem.decode(),
        "kprivkdatos":encrypted_private_key.hex()
    }

    print(data)
    response = requests.post(SERVER_URL+"/register", json=data)
    if response.status_code == 200:
        print("Datos enviados correctamente al endpoint en la nube.")
        # --------------- ALMACENA LAS LLAVES DE FORMA LOCAL --------------
        keys = {
            "kpub": public_key_pem.decode(),
            "kpriv": private_key_pem.decode()
        }
        with open('config.json', 'w') as json_file:
            json.dump(keys, json_file, indent=4)
    else:
        print("Error al enviar los datos al endpoint en la nube. Código de estado:", response.status_code)

def get_keys(user,password):
    sha256_hash = hashlib.sha256(password.encode()).hexdigest()
    k_login = sha256_hash[:32]
    k_login_bytes = bytes.fromhex(k_login)
    k_login_hashed = bcrypt.hashpw(k_login.encode(), bcrypt.gensalt()).decode()
    data={
        "user":user,
        "klogin":k_login_hashed,
    }

    # ------------- LLAMADA AL SERVIDOR -------------
    response = requests.post(SERVER_URL+"/login", json=data)

    # 
    #   Aqui el servidor debe comparar que las claves de login en el sistema y la enviada
    #   coincidan con las del usuario solicitado. Si no coinciden, se devuelve un mensaje
    #   de error, si conciden se debe devolver:
    #       data={
    #           "kpub":key,
    #           "kpriv+kdatos":key
    #       }
    #           keys = response.json

    sha256_hash = hashlib.sha256(password.encode()).hexdigest()
    k_datos = sha256_hash[-32:]
    k_datos_bytes = bytes.fromhex(k_datos)
    # Ajustar la longitud de k_datos_bytes para que sea múltiplo del tamaño del bloque del cifrado AES
    k_datos_bytes = k_datos_bytes[:16]
    # ------------------- PROCESO DE DESENCRIPTACION DE LLAVES ------------------
    cipher = Cipher(algorithms.AES(k_datos_bytes), modes.ECB(), backend=default_backend())
    decryptor = cipher.decryptor()

    public_key_pem = "data.kpub"
    private_key_pem = decryptor.update("data.kprivkdatos") + decryptor.finalize()

    # --------------------- ALMACENA LAS LLAVES DE FORMA LOCAL --------------
    keys = {
        "kpub": public_key_pem.decode(),
        "kpriv": private_key_pem.decode()
    }
    with open('config.json', 'w') as json_file:
        json.dump(keys, json_file, indent=4)