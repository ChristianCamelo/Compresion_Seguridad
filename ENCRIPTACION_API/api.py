from flask import Flask, request, jsonify
import metodos_api
import encriptar_rsa
import json
import os
import bcrypt
import base64
from flask_jwt_extended import JWTManager, create_access_token
from werkzeug.utils import secure_filename

# Cdo se sube un archivo se crea carpeta para el usuario dentro de datos, y dentro de cada carpeta los archivos cifrados y las contraseñas, nonce
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = "clave_super_secreta"
app.config['UPLOAD_FOLDER'] = 'archivos'
app.config['SHARE'] = 'share'
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
    print("La clave de login de camelo es: ", data['k_login'])
    print("La clave de login del servidor es: ", k_login)
    
    if user not in config_data:
        return jsonify({"Error": "El usuario no existe. Por favor, ingrese unas credenciales válidas."}), 401
    if k_login not in config_data[user]["k_login"]:
        return jsonify({"Error": "La clave de login no coincide. Por favor, ingrese unas credenciales válidas."}), 402
    
    acces_token = create_access_token(identity=data["user"])
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
    data = request.json

    if 'user' not in data or 'archivos' not in data:
        return jsonify({'error': 'Estructura JSON incorrecta'}), 400
    username = data['user']
    user = data['user']
    # Abre el archivo de configuración JSON y carga los datos en config_data
    with app.app_context():
        with open("config.json", "r") as config_file:
            config_data = json.load(config_file)
    k_login = data['k_login']

    # Verifica si el usuario existe y si la clave de inicio de sesión coincide
    if user not in config_data:
        return jsonify({"Error": "El usuario no existe. Por favor, ingrese unas credenciales válidas."}), 401
    if k_login not in config_data[user]["k_login"]:
        return jsonify({"Error": "La clave de login no coincide. Por favor, ingrese unas credenciales válidas."}), 402
    try:
        
        user_folder = os.path.join(app.config['UPLOAD_FOLDER'], username)
        os.makedirs(user_folder, exist_ok=True)

        archivos = data['archivos']

        for index, archivo_info in archivos.items():
            archivo_nombre = archivo_info.get('archivo')
            key = archivo_info.get('key')

            if archivo_nombre and key:

                # Crear carpeta 'archivoN' dentro de la carpeta del usuario
                carpeta_archivo = os.path.join(user_folder, f'{index}')
                os.makedirs(carpeta_archivo, exist_ok=True)

                # Guardar el archivo en la carpeta 'archivoN'
                archivo_path = os.path.join(carpeta_archivo, secure_filename(archivo_nombre))
                key_path = os.path.join(carpeta_archivo, secure_filename(key))

                with open(archivo_path, 'wb') as file:
                    file.write(b'Tu archivo encriptado')#Aqui hay que meter el contenido del archvio encriptado

                with open(key_path, 'wb') as key_file:
                    key_file.write(b'Tu llave de archivo')

        return jsonify({'message': 'Archivos cargados correctamente'})

    except Exception as e:
        return jsonify({'error': f'Error en la carga de archivos: {str(e)}'}), 500


# Endpoint de descarga de archivos
@app.route('/download/<username>/', methods=['GET'])
def descargar_archivo(username):
    # Abre el archivo de configuración JSON y carga los datos en config_data
    with app.app_context():
        with open("config.json", "r") as config_file:
            config_data = json.load(config_file)

    # Obtiene los datos del usuario y la clave de inicio de sesión de la solicitud
    data = request.json
    user = data['user']
    k_login = data['k_login']

    # Verifica si el usuario existe y si la clave de inicio de sesión coincide
    if user not in config_data:
        return jsonify({"Error": "El usuario no existe. Por favor, ingrese unas credenciales válidas."}), 401
    if k_login not in config_data[user]["k_login"]:
        return jsonify({"Error": "La clave de login no coincide. Por favor, ingrese unas credenciales válidas."}), 402

    try:
        # Construye la ruta del directorio del usuario en la nueva estructura
        user_folder = os.path.join(os.getcwd(), "archivos", username)
        
        

        # Verifica si el directorio existe
        if not os.path.exists(user_folder):
            return jsonify({'error': f'Error interno al intentar descargar: Directorio no encontrado'}), 404

        # Inicializa un diccionario para almacenar la información de archivos
        archivos_dict = {}

        # Itera sobre los archivos en el directorio del usuario
        for index, archivo_nombre in enumerate(os.listdir(user_folder)):
        
            # Construye las rutas de los archivos y las llaves
            ruta_archivo = os.path.join(user_folder, archivo_nombre,'archivo.txt')
            ruta_llave = os.path.join(user_folder, archivo_nombre,'key.key')

            # Lee el archivo binario y lo codifica en base64
            with open(ruta_archivo, 'rb') as a:
                archivo = base64.b64encode(a.read()).decode('utf-8')

            # Lee la llave binaria y la codifica en base64
            with open(ruta_llave, 'rb') as b:
                llave = base64.b64encode(b.read()).decode('utf-8')

            # Agrega la información del archivo al diccionario
            archivos_dict[str(index)] = {
                'archivo': archivo,
                'key': llave
            }

        # Construye la respuesta JSON con la información de los archivos
        response = {'archivos': archivos_dict}

        # Retorna la respuesta JSON
        return jsonify(response)

    except Exception as e:
        return jsonify({'error': f'Error interno al intentar descargar: {str(e)}'}), 500


@app.route('/share/<username>/', methods=['GET'])
def descargar_share(username):
    # Abre el archivo de configuración JSON y carga los datos en config_data
    with app.app_context():
        with open("config.json", "r") as config_file:
            config_data = json.load(config_file)

    # Obtiene los datos del usuario y la clave de inicio de sesión de la solicitud
    data = request.json
    user = data['user']
    k_publica = data['k_publica']

    # Verifica si el usuario existe y si la clave de inicio de sesión coincide
    if user not in config_data:
        return jsonify({"Error": "El usuario no existe. Por favor, ingrese unas credenciales válidas."}), 401
    if k_publica not in config_data[user]["k_publica"]:
        return jsonify({"Error": "La clave de login no coincide. Por favor, ingrese unas credenciales válidas."}), 402

    try:
        # Construye la ruta del directorio del usuario en la nueva estructura
        user_folder = os.path.join(os.getcwd(), "share", username)
        
        

        # Verifica si el directorio existe
        if not os.path.exists(user_folder):
            return jsonify({'error': f'Error interno al intentar descargar: Directorio no encontrado'}), 404

        # Inicializa un diccionario para almacenar la información de archivos
        archivos_dict = {}

        # Itera sobre los archivos en el directorio del usuario
        for index, archivo_nombre in enumerate(os.listdir(user_folder)):
        
            # Construye las rutas de los archivos y las llaves
            ruta_archivo = os.path.join(user_folder, archivo_nombre,'archivo.txt')
            ruta_llave = os.path.join(user_folder, archivo_nombre,'key.key')

            # Lee el archivo binario y lo codifica en base64
            with open(ruta_archivo, 'rb') as a:
                archivo = base64.b64encode(a.read()).decode('utf-8')

            # Lee la llave binaria y la codifica en base64
            with open(ruta_llave, 'rb') as b:
                llave = base64.b64encode(b.read()).decode('utf-8')

            # Agrega la información del archivo al diccionario
            archivos_dict[str(index)] = {
                'archivo': archivo,
                'key': llave
            }

        # Construye la respuesta JSON con la información de los archivos
        response = {'archivos': archivos_dict}

        # Retorna la respuesta JSON
        return jsonify(response)

    except Exception as e:
        return jsonify({'error': f'Error interno al intentar descargar: {str(e)}'}), 500


@app.route('/share', methods=['POST'])
def cargar_share():
    data = request.json

    if 'user' not in data or 'archivos' not in data:
        return jsonify({'error': 'Estructura JSON incorrecta'}), 400
    username = data['user']
    user = data['user']
    # Abre el archivo de configuración JSON y carga los datos en config_data
    with app.app_context():
        with open("config.json", "r") as config_file:
            config_data = json.load(config_file)
    k_publica = data['k_publica']

    # Verifica si el usuario existe y si la clave de inicio de sesión coincide
    if user not in config_data:
        return jsonify({"Error": "El usuario no existe. Por favor, ingrese unas credenciales válidas."}), 401
    if k_publica not in config_data[user]["k_publica"]:
        return jsonify({"Error": "La clave de login no coincide. Por favor, ingrese unas credenciales válidas."}), 402
    try:
        
        user_folder = os.path.join(app.config['SHARE'], username)
        os.makedirs(user_folder, exist_ok=True)

        archivos = data['archivos']

        for index, archivo_info in archivos.items():
            archivo_nombre = archivo_info.get('archivo')
            key = archivo_info.get('key')

            if archivo_nombre and key:

                # Crear carpeta 'archivoN' dentro de la carpeta del usuario
                carpeta_archivo = os.path.join(user_folder, f'{index}')
                os.makedirs(carpeta_archivo, exist_ok=True)

                # Guardar el archivo en la carpeta 'archivoN'
                archivo_path = os.path.join(carpeta_archivo, secure_filename(archivo_nombre))
                key_path = os.path.join(carpeta_archivo, secure_filename(key))

                with open(archivo_path, 'wb') as file:
                    file.write(b'Tu archivo encriptado')#Aqui hay que meter el contenido del archvio encriptado

                with open(key_path, 'wb') as key_file:
                    key_file.write(b'Tu llave de archivo')

        return jsonify({'message': 'Archivos cargados correctamente'})

    except Exception as e:
        return jsonify({'error': f'Error en la carga de archivos: {str(e)}'}), 500

# Ruta raiz
@app.route('/')
def home():
    return jsonify('Bienvenido')

if __name__ == '__main__':
    #app.run(ssl_context='adhoc', debug=True, port=5000)
    app.run(debug=True, port=5000)