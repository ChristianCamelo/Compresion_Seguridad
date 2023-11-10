from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
import metodos_api

app = Flask(__name__)

# Almacenamiento temporal para usuarios registrados (en un entorno de producción, usa una base de datos real).
usuarios_registrados = {}
#-----------------------------------------------------------------------------------------------------------------------------------------------------
# CREANDO EL ADMIN
#-----------------------------------------------------------------------------------------------------------------------------------------------------
if len(usuarios_registrados) <= 0:
    admin = metodos_api.crea_administrador()
    usuarios_registrados["admin"] = admin
print('Los usuarios registrados son: ', usuarios_registrados)

#-----------------------------------------------------------------------------------------------------------------------------------------------------
# GUARDANDO LA INFORMACION EN EL config.json
#-----------------------------------------------------------------------------------------------------------------------------------------------------
metodos_api.guarda_info_admin(usuarios_registrados)

#-----------------------------------------------------------------------------------------------------------------------------------------------------
# HACIENDO EH HASH DE LA PASS DEL ADMIN
#-----------------------------------------------------------------------------------------------------------------------------------------------------
pass_SHA256 = metodos_api.hash_password()

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

# Endpoint de carga de archivos
@app.route('/upload', methods=['POST'])
def cargar_archivo():
    data = request.get_json()
    if 'username' in data and 'password' in data:
        username = data['username']

        user_folder = os.path.join(app.config['UPLOAD_FOLDER'], username)
        os.makedirs(user_folder, exist_ok=True)
        # Verificar si se han enviado archivos
        if 'file' not in data:
            return jsonify({'error': 'No se han enviado archivos'}), 400

        uploaded_file = data['file']

        # Verificar que se haya seleccionado un archivo
        if uploaded_file.filename == '':
            return jsonify({'error': 'No se ha seleccionado ningún archivo'}), 400

        # Verificar si el archivo es válido
        if uploaded_file:
            # Asegurarse de que el nombre del archivo sea seguro
            filename = secure_filename(uploaded_file.filename)
            file_path = os.path.join('datos', user_folder, filename)
            uploaded_file.save(file_path)
            return jsonify({'message': 'Archivo cargado exitosamente'})
        else:
            return jsonify({'error': 'Formato de archivo no válido'}), 400
    else:
        return jsonify({'error': 'Usuario no autenticado'}), 401

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
