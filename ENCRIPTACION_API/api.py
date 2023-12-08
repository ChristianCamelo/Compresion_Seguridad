from flask import Flask, request, jsonify
import metodos_api
import encriptar_rsa
import json
import os
import bcrypt
import base64
from flask_jwt_extended import JWTManager, create_access_token

# Cdo se sube un archivo se crea carpeta para el usuario dentro de datos, y dentro de cada carpeta los archivos cifrados y las contraseñas, nonce
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = "clave_super_secreta"
jwt = JWTManager(app)



# Almacenamiento temporal para usuarios registrados (en un entorno de producción, usa una base de datos real).
config_path = "config.json"
usuarios_registrados = {}
with open(config_path, 'r') as config_file:
    usuarios_registrados.update(json.load(config_file))
#-----------------------------------------------------------------------------------------------------------------------------------------------------
# CREANDO EL ADMIN
#-----------------------------------------------------------------------------------------------------------------------------------------------------
if "admin" not in usuarios_registrados:
    admin = metodos_api.crea_administrador()[0]
    usuarios_registrados["admin"] = admin

    metodos_api.guarda_info_admin(usuarios_registrados)

    pass_SHA256 = metodos_api.crea_administrador()[1]
    k_login = metodos_api.get_clave_login(pass_SHA256)
    k_datos = metodos_api.get_clave_datos(pass_SHA256)

    metodos_api.hash_k_login(k_login)

    claves_privada_y_publica = metodos_api.genera_clave_rsa()

    encriptar_rsa.encriptar(claves_privada_y_publica[0], k_datos.encode())
    metodos_api.elimina_password()

print('Los usuarios registrados son: {"user":"admin", "pass":"admin"}')

# Endpoint de registro PARA LA SIGUIENTE FASE
@app.route('/registrar', methods=['POST'])
def registrar_usuario():
    user_data = request.json
    username = user_data["user"]
    k_login = user_data['k_login']

    if username in usuarios_registrados:
        return jsonify({"Error": "El nombre de usuario ya existe. Por favor, elige otro."}), 401
    
    # CREANDO CARPETA PARA EL USUARIO
    datos_folder_path = os.path.join(os.getcwd(), "datos")
    user_folder_path = os.path.join(datos_folder_path, username)
    encripted_folder_path = os.path.join(user_folder_path, "Archivos_Encriptados")
    shared_folder_path = os.path.join(user_folder_path, "Archivos_Compartidos")
    os.makedirs(user_folder_path, exist_ok=True)
    os.makedirs(encripted_folder_path, exist_ok=True)
    os.makedirs(shared_folder_path, exist_ok=True)

    access_token = create_access_token(username)
    print(access_token)
    
    SALT = bcrypt.gensalt()
    user_data['k_login'] = bcrypt.hashpw(k_login.encode(), SALT).decode()
    usuarios_registrados[user_data["user"]] = {
        "user": user_data["user"],
        "k_login": user_data["k_login"],
        "k_publica": user_data["k_publica"],
        "k_privada": user_data["k_privada"],
        "Salt": base64.b64encode(SALT).decode("utf-8"),
        "token": access_token
    }



    with open("config.json", "w") as file:
        json.dump(usuarios_registrados, file, indent=4)
        
    #RESPUESTA
    return jsonify({"k_login" : user_data['k_login'], "message" : "Usuario registrado correctamente"})

# Endpoint de inicio de sesión
@app.route('/login', methods=['POST'])
def iniciar_sesion():
    data = request.json
    with app.app_context():
        with open ("config.json", "r") as config_file:
            config_data = json.load(config_file)

    user = data['user']
    SALT = base64.b64decode(config_data[user]['Salt'].encode("utf-8")) 
    k_login = bcrypt.hashpw(data['k_login'].encode(), SALT).decode() 
    acces_token = create_access_token(identity=data["user"])
    
    if user not in config_data:
        return jsonify({"Error": "El usuario no existe. Por favor, ingrese unas credenciales válidas."}), 401
    if data["k_login"] not in config_data[user]["k_login"]:
        return jsonify({"Error": "La clave de login no coincide. Por favor, ingrese unas credenciales válidas."}), 402
    
    config_data[user]["token"] = acces_token

    with open(config_path, 'w') as config_file:
        json.dump(config_data, config_file, indent=4)

    
    return jsonify({"access_token" : acces_token, "k_privada":config_data[user]["k_privada"], "message" : "Usuario registrado correctamente"})
# Endpoint de carga de archivos
@app.route('/getpublickey', methods=['GET'])
def get_public_key():
    data = request.json
    user = data['user']
    with app.app_context():
        with open ("config.json", "r") as config_file:
            config_data = json.load(config_file)
    if user not in config_data:
        return jsonify({"Error": "El usuario no existe. Por favor, ingrese unas credenciales válidas."}), 401
    return jsonify({'k_publica': config_data[user]['k_publica']})

# Endpoint de carga de archivos
@app.route('/upload', methods=['POST'])
def cargar_archivo():
    # Lógica para cargar archivos
    return jsonify({'message': 'Archivo cargado'})

# Endpoint de descarga de archivos
@app.route('/download', methods=['GET'])
def descargar_archivo():
    # Lógica para descargar archivos
    return jsonify({'message': 'Archivo descargado'})

# Ruta raiz
@app.route('/')
def home():
    return jsonify('Bienvenido')

if __name__ == '__main__':
    app.run(ssl_context=('./certificados/cert.pem', './certificados/key.pem'), debug=True, port=5000)