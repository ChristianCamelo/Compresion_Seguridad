import os
from utilities import escribirLog
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes # para generar la clave y el IV
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

import base64
import json

#------------------------------------------------------------------------------------------------------------------------------------
# FUNCIÓN PARA ENCRIPTAR
#------------------------------------------------------------------------------------------------------------------------------------
def encriptar(private_pem, k_datos):
    modo_encriptar = AES.MODE_CTR
    key = k_datos

    objeto_ecriptador = AES.new(key, modo_encriptar)
    nonce = objeto_ecriptador.nonce


    rsa_privada_encriptada = objeto_ecriptador.encrypt(private_pem)


    rsa_privada_encriptada_str = base64.b64encode(rsa_privada_encriptada).decode('utf-8')
    with open("config.json", "r") as config_file:
        config = json.load(config_file)
        config["admin"]["k_privada"] =  rsa_privada_encriptada_str

    with open("config.json", "w") as config_file:
        json.dump(config, config_file, indent=4)


    return rsa_privada_encriptada