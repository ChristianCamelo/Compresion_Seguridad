import hashlib
import json
import bcrypt
import base64

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

def crea_administrador():
    admin = {
        "user": "admin",
        "password": "admin"
    }
    pass_hashed = hash_password("admin")
    return admin, pass_hashed

def guarda_info_admin(usuarios_registrados, file_path='config.json'):
    info = usuarios_registrados.get("admin", {})
    with open(file_path, 'w') as json_file:
        json.dump({'admin': info}, json_file, indent=4)

def hash_password(password):
    sha256_hash = hashlib.sha256(password.encode()).hexdigest()
    return sha256_hash

def get_clave_login(password):
    k_login = password[:32]
    return k_login

def get_clave_datos(password):
    k_datos = password[-32:]
    return k_datos

def hash_k_login(k_login, file_path='config.json'):
    with open (file_path, 'r') as fichero_json:
        data = json.load(fichero_json)
    
    if 'admin' in data:
        info_admin = data.get("admin", {})
        info_admin["k_login"] = bcrypt.hashpw(k_login.encode(), bcrypt.gensalt()).decode()

    with open (file_path, 'w') as json_file:
        data['admin'] = info_admin
        json.dump(data, json_file, indent=4)

def genera_clave_rsa():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    public_key = private_key.public_key()

    # Serializar la clave privada en formato PEM (Privacy Enhanced Mail)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    # Serializar la clave pública en formato PEM
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    guardar_clave_publica(public_pem)

    return (private_pem, public_pem)


def guardar_clave_publica (public_pem):
    rsa_publica_str = base64.b64encode(public_pem).decode('utf-8')
    
    with open("config.json", 'r') as config_file:
        config = json.load(config_file)

    # Modificar solo la parte necesaria del archivo
    if 'admin' in config:
        config["admin"]["k_admin_publica"] = rsa_publica_str

    with open("config.json", 'w') as config_file:
        json.dump(config, config_file, indent=4)

def elimina_password(file_path='config.json'):
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)

    if 'admin' in data:
        if 'password' in data['admin']:
            del data['admin']['password']

    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)
