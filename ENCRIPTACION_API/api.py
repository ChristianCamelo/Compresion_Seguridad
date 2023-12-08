import metodos_api
import encriptar_rsa
import json
import os
import bcrypt
import requests
import base64
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify

# Cdo se sube un archivo se crea carpeta para el usuario dentro de datos, y dentro de cada carpeta los archivos cifrados y las contraseñas, nonce
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'archivos'
app.config['SHARE'] = 'share'



# Almacenamiento temporal para usuarios registrados (en un entorno de producción, usa una base de datos real).
config_path = "./config.json"
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

    SALT = bcrypt.gensalt()

    user_data['k_login'] = bcrypt.hashpw(k_login.encode(), SALT).decode()
    usuarios_registrados[user_data["user"]] = {
        "user": user_data["user"],
        "k_login": user_data["k_login"],
        "k_publica": user_data["k_publica"],
        "k_privada": user_data["k_privada"],
        "Salt": base64.b64encode(SALT).decode("utf-8")
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
    if user not in config_data:
        return jsonify({"Error": "El usuario no existe. Por favor, ingrese unas credenciales válidas."}), 401
    if k_login not in config_data[user]["k_login"]:
        return jsonify({"Error": "La clave de login no coincide. Por favor, ingrese unas credenciales válidas."}), 402
    
    return jsonify({
        "k_login": config_data[user]["k_login"],
        "k_publica": config_data[user]["k_publica"],
        "k_privada":config_data[user]["k_privada"], 
        "message" : "Usuario registrado correctamente"
        })

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


@app.route('/upload', methods=['POST'])
def cargar_archivo():

    data = request.json
    user = data['user']

    with app.app_context():
        with open("config.json", "r") as config_file:
            config_data = json.load(config_file)

    if user not in config_data:
        return jsonify({"Error": "El usuario no existe. Por favor, ingrese unas credenciales válidas."}), 401
    if data['k_login'] not in config_data[user]["k_login"]:
        return jsonify({"Error": "La clave de login no coincide. Por favor, ingrese unas credenciales válidas."}), 402
    
    try:
        datos_folder = os.path.join(os.getcwd(),'datos',user)
        user_folder = os.path.join(datos_folder,'Archivos_Encriptados')
        archivos = data['archivos']

        cantidad = len(os.listdir(user_folder))

        for index, archivo_info in archivos.items():

            file = archivo_info.get('archivo')
            key = archivo_info.get('key')

            carpeta_archivo = os.path.join(user_folder, str(cantidad+int(index)))
            os.makedirs(carpeta_archivo, exist_ok=True)

            archivo_path = os.path.join(carpeta_archivo, secure_filename('archivo.txt'))
            key_path = os.path.join(carpeta_archivo, secure_filename('key.txt'))

            with open(archivo_path, 'w') as f:
                f.write(file)

            with open(key_path, 'w') as f:
                f.write(key)

        return jsonify({'message': 'Archivos cargados correctamente'}) , 200

    except Exception as e:
        return jsonify({'error': f'Error en la carga de archivos: {str(e)}'}), 500


@app.route('/download', methods=['GET'])
def descargar_archivo():
    with app.app_context():
        with open("config.json", "r") as config_file:
            config_data = json.load(config_file)

    data = request.json
    user = data['user']
    k_login = data['k_login']

    if user not in config_data:
        return jsonify({"Error": "El usuario no existe. Por favor, ingrese unas credenciales válidas."}), 401
    if k_login not in config_data[user]["k_login"]:
        return jsonify({"Error": "La clave de login no coincide. Por favor, ingrese unas credenciales válidas."}), 402
    
    try:

        datos_folder = os.path.join(os.getcwd(),'datos',user)
        user_folder = os.path.join(datos_folder,'Archivos_Encriptados')

        cantidad = len(os.listdir(user_folder))

        if not os.path.exists(user_folder):
            return jsonify({'error': f'Error interno al intentar descargar: Directorio no encontrado'}), 404

        archivos_dict = {}

        for index, file in enumerate(os.listdir(user_folder)):
            print("PART FOR")
            ruta_archivo = os.path.join(user_folder, file,'archivo.txt')
            ruta_llave = os.path.join(user_folder, file,'key.txt')

            with open(ruta_archivo, 'r') as a:
                archivo = a.read()

            with open(ruta_llave, 'r') as b:
                llave = b.read()

            archivos_dict[index] = {
                'archivo': archivo,
                'key': llave
            }
        
        response = ({'archivos': archivos_dict})
        print(response)
        return jsonify(response) , 200

    except Exception as e:
        return jsonify({'error': f'Error interno al intentar descargar: {str(e)}'}), 500


@app.route('/share', methods=['POST'])
def cargar_share():
    
    with app.app_context():
        with open("config.json", "r") as config_file:
            config_data = json.load(config_file)

    data = request.json
    user = data['user']
    receptor = data['receptor']
    k_login = data['k_login']

    if user not in config_data:
        return jsonify({"Error": "El usuario no existe. Por favor, ingrese unas credenciales válidas."}), 401
    if k_login not in config_data[user]["k_login"]:
        return jsonify({"Error": "La clave de login no coincide. Por favor, ingrese unas credenciales válidas."}), 402

    try:

        datos_folder = os.path.join(os.getcwd(),'datos',receptor)
        user_folder = os.path.join(datos_folder,'Archivos_Compartidos')
        cantidad = len(os.listdir(user_folder))

        carpeta_archivo = os.path.join(user_folder, str(cantidad))
        os.makedirs(carpeta_archivo, exist_ok=True)

        archivo_path = os.path.join(carpeta_archivo, secure_filename('archivo.txt'))
        key_path = os.path.join(carpeta_archivo, secure_filename('key.txt'))

        with open(archivo_path, 'w') as f:
            f.write(data['data']['archivo'])

        with open(key_path, 'w') as f:
            f.write(data['data']['key'])
        return jsonify({'mensaje': 'Archivo compartido correctamente.'}) , 200

    except Exception as e:
        return jsonify({'error': f'Error interno al intentar descargar: {str(e)}'}), 500


@app.route('/share', methods=['GET'])
def descargar_share():
    with app.app_context():
        with open("config.json", "r") as config_file:
            config_data = json.load(config_file)

    data = request.json

    user = data['user']
    k_login = data['k_login']

    if user not in config_data:
        return jsonify({"Error": "El usuario no existe. Por favor, ingrese unas credenciales válidas."}), 401
    if k_login not in config_data[user]["k_login"]:
        return jsonify({"Error": "La clave de login no coincide. Por favor, ingrese unas credenciales válidas."}), 402
    
    try:
        datos_folder = os.path.join(os.getcwd(),'datos',user)
        user_folder = os.path.join(datos_folder,'Archivos_Compartidos')

        cantidad = len(os.listdir(user_folder))

        if not os.path.exists(user_folder):
            return jsonify({'error': f'Error interno al intentar descargar: Directorio no encontrado'}), 404

        archivos_dict = {}
        for index, file in enumerate(os.listdir(user_folder)):

            ruta_archivo = os.path.join(user_folder, file,'archivo.txt')
            ruta_llave = os.path.join(user_folder, file,'key.txt')

            with open(ruta_archivo, 'r') as a:
                archivo = a.read()

            with open(ruta_llave, 'r') as b:
                llave = b.read()

            archivos_dict[index] = {
                'archivo': archivo,
                'key': llave
            }
        
        response = ({'archivos': archivos_dict})
        print(response)
        return jsonify(response) , 200

    except Exception as e:
        return jsonify({'error': f'Error interno al intentar descargar: {str(e)}'}), 500

# Ruta raiz
@app.route('/')
def home():
    return jsonify('Bienvenido')

if __name__ == '__main__':
    #app.run(ssl_context='adhoc', debug=True, port=5000)
    app.run(debug=True, port=5000)


def formater64(data):
    return base64.b64encode(data).decode('utf-8')

def reverse_formater64(encoded_data):
    return base64.b64decode(encoded_data.encode('utf-8'))