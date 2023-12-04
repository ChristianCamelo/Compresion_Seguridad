from flask import Flask, request, jsonify
import metodos_api
import encriptar_rsa
import json
import os
import bcrypt
from flask_jwt_extended import JWTManager, create_access_token

# Cdo se sube un archivo se crea carpeta para el usuario dentro de datos, y dentro de cada carpeta los archivos cifrados y las contraseñas, nonce
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = "clave_super_secreta"
jwt = JWTManager(app)

# Almacenamiento temporal para usuarios registrados (en un entorno de producción, usa una base de datos real).
config_path = "config.json"
usuarios_registrados = {}
if os.path.exists(config_path):
    with open(config_path, 'r') as config_file:
        usuarios_registrados.update(json.load(config_file))
else:
    with open(config_path, 'w') as config_file:
        admin = metodos_api.crea_administrador()[0]
        usuarios_registrados = {"admin":admin}
        json.dump(usuarios_registrados, config_file, indent=4)
#-----------------------------------------------------------------------------------------------------------------------------------------------------
# CREANDO EL ADMIN
#-----------------------------------------------------------------------------------------------------------------------------------------------------
if "admin" not in usuarios_registrados:
    admin = metodos_api.crea_administrador()[0]
    usuarios_registrados["admin"] = admin
print('Los usuarios registrados son: {"user":"admin", "pass":"admin"}')

#-----------------------------------------------------------------------------------------------------------------------------------------------------
# GUARDANDO LA INFORMACION EN EL config.json
#-----------------------------------------------------------------------------------------------------------------------------------------------------
metodos_api.guarda_info_admin(usuarios_registrados)

#-----------------------------------------------------------------------------------------------------------------------------------------------------
# HACIENDO EH HASH DE LA PASS DEL ADMIN
#-----------------------------------------------------------------------------------------------------------------------------------------------------
pass_SHA256 = metodos_api.crea_administrador()[1]

#-----------------------------------------------------------------------------------------------------------------------------------------------------
# CONSIGUIENDO LA CLAVE DEL LOGIN
#-----------------------------------------------------------------------------------------------------------------------------------------------------
k_login = metodos_api.get_clave_login(pass_SHA256)

#-----------------------------------------------------------------------------------------------------------------------------------------------------
# CONSIGUIENDO LA CLAVE DE DATOS
#-----------------------------------------------------------------------------------------------------------------------------------------------------
k_datos = metodos_api.get_clave_datos(pass_SHA256)

#-----------------------------------------------------------------------------------------------------------------------------------------------------
# HASHEANDO EL K_LOGIN Y GUARDAR EN CONFIG.JSON
#-----------------------------------------------------------------------------------------------------------------------------------------------------
metodos_api.hash_k_login(k_login)

#-----------------------------------------------------------------------------------------------------------------------------------------------------
# CREANDO LA CLAVE RSA
#-----------------------------------------------------------------------------------------------------------------------------------------------------
claves_privada_y_publica = metodos_api.genera_clave_rsa()

#-----------------------------------------------------------------------------------------------------------------------------------------------------
# ENCRIPTADO LA CLAVE PRIVADA CON LA K_DATOS
#-----------------------------------------------------------------------------------------------------------------------------------------------------
encriptar_rsa.encriptar(claves_privada_y_publica[0], k_datos.encode())

#-----------------------------------------------------------------------------------------------------------------------------------------------------
# BORRANDO LA CONTRASEÑA. DEBE IR AL FINAL
#-----------------------------------------------------------------------------------------------------------------------------------------------------
metodos_api.elimina_password()

# Endpoint de registro PARA LA SIGUIENTE FASE
@app.route('/registrar', methods=['POST'])
def registrar_usuario():
    user_data = request.json
    # with app.app_context():
        #with open("config.json", "r") as config_file:
        #    config_data = json.load(config_file)
    username = user_data["user"]

    if username in usuarios_registrados:
        return jsonify({"Error": "El nombre de usuario ya existe. Por favor, elige otro."}), 401
    
    # CREANDO CARPETA PARA EL USUARIO
    datos_folder_path = os.path.join(os.getcwd(), "datos")
    user_folder_path = os.path.join(datos_folder_path, username)
    os.makedirs(user_folder_path, exist_ok=True)

    user_data['klogin'] = bcrypt.hashpw(k_login.encode(), bcrypt.gensalt()).decode()

    usuarios_registrados[user_data["user"]] = {
        "user": user_data["user"],
        "k_login": user_data["klogin"],
        "k_admin_publica": user_data["kpub"],
        "k_admin_priv": user_data["kprivkdatos"]
    }

    with open("config.json", "w") as file:
        json.dump(usuarios_registrados, file, indent=4)
        
    #RESPUESTA
    acces_token = create_access_token(identity=user_data["user"])
    return jsonify({"access_token" : acces_token, "message" : "Usuario registrado correctamente"})

# Endpoint de inicio de sesión
@app.route('/login', methods=['POST'])
def iniciar_sesion():
    data = request.json
    with app.app_context():
        with open ("config.json", "r") as config_file:
            config_data = json.load(config_file)
    user = data['user']
    klogin = data['k_login']
    if user not in config_data:
        return jsonify({"Error": "El usuario no existe. Por favor, ingrese unas credenciales válidas."}), 401
    
    print("Los datos son", config_data[user])
    
    acces_token = create_access_token(identity=data["user"])
    return jsonify({"access_token" : acces_token, "Kprivada":config_data[user]["k_admin_priv"], "message" : "Usuario registrado correctamente"})

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
    app.run(ssl_context='adhoc', debug=True, port=5000)