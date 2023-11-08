import hashlib
import json
import bcrypt

def crea_administrador():
    admin = {
        "user": "admin",
        "password": "admin"
    }
    return admin

def guarda_info_admin(usuarios_registrados, file_path='config.json'):
    info = usuarios_registrados.get("admin", {})
    with open(file_path, 'w') as json_file:
        json.dump({'admin': info}, json_file)

def hash_password():
    json_file_path = 'config.json'
    with open (json_file_path, 'r') as json_file:
        data = json.load(json_file)
    
    password = data.get("admin", {}).get("password", None)
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
    
    info_admin = data.get("admin", {})
    info_admin["k_login"] = bcrypt.hashpw(k_login.encode(), bcrypt.gensalt()).decode()
    print('La info del admin es: ', info_admin)

    with open (file_path, 'w') as json_file:
        data['admin'] = info_admin
        json.dump(data, json_file, indent=4)