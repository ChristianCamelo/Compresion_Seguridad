from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
import metodos_api

app = Flask(__name__)

# Configuración de la carpeta de subida
app.config['UPLOAD_FOLDER'] = './datos/'

# Almacenamiento temporal para usuarios registrados (en un entorno de producción, usa una base de datos real).
usuarios_registrados = {}

# CREANDO EL ADMIN
if len(usuarios_registrados) <= 0:
    admin = metodos_api.crea_administrador()
    usuarios_registrados["admin"] = admin
print('Los usuarios registrados son: ', usuarios_registrados)

# GUARDANDO LA INFORMACION EN EL config.json
metodos_api.guarda_info_admin(usuarios_registrados)

# HACIENDO EH HASH DE LA PASS DEL ADMIN
pass_SHA256 = metodos_api.hash_password()

# CONSIGUIENDO LA CLAVE DEL LOGIN
k_login = metodos_api.get_clave_login(pass_SHA256)

# CONSIGUIENDO LA CLAVE DE DATOS
k_datos = metodos_api.get_clave_datos(pass_SHA256)

# HASHEANDO EL K_LOGIN Y GUARDAR EN CONFIG.JSON
metodos_api.hash_k_login(k_login)

# Endpoint de carga de archivos
@app.route('/upload', methods=['POST'])
def cargar_archivo():
    try:
        data = request.get_json()

        if 'username' not in data or 'Archivos' not in data:
            return jsonify({'error': 'Faltan campos obligatorios en el JSON'}), 400

        username = data['username']
        user_folder = os.path.join(app.config['UPLOAD_FOLDER'], username)
        os.makedirs(user_folder, exist_ok=True)

        archivos = data['Archivos']

        for numero, archivo in archivos.items():
            # Crear carpeta 'archivoN' dentro de la carpeta del usuario
            carpeta_archivo = os.path.join(user_folder, f'archivo{numero}')
            os.makedirs(carpeta_archivo, exist_ok=True)

            # Guardar el archivo en la carpeta 'archivoN'
            encriptado_filename = secure_filename(archivo['Encriptado'])
            llave_filename = secure_filename(archivo['Llave'])

            encriptado_path = os.path.join(carpeta_archivo, encriptado_filename)
            llave_path = os.path.join(carpeta_archivo, llave_filename)

            with open(encriptado_path, 'wb') as f:
                f.write(b'Tu archivo encriptado')

            with open(llave_path, 'wb') as f:
                f.write(b'Tu llave de archivo')

        return jsonify({'message': 'Archivos cargados exitosamente'})

    except Exception as e:
        print(f"Error en cargar_archivo: {str(e)}")
        return jsonify({'error': 'Error interno'}), 500




# Endpoint de descarga de archivos específicos
@app.route('/download/<username>/<path:filename>', methods=['GET'])
def descargar_archivo(username, filename):
    try:
        user_folder = os.path.join(app.config['UPLOAD_FOLDER'], username)
        file_path = os.path.join(user_folder, filename)

        # Verificar si la carpeta del usuario existe
        if not os.path.exists(user_folder):
            return jsonify({'error': f'El usuario {username} no existe'}), 404

        # Verificar si el archivo o carpeta existe en la carpeta del usuario
        if not os.path.exists(file_path):
            return jsonify({'error': f'El archivo o carpeta {filename} no existe para el usuario {username}'}), 404

        # Verificar si es un archivo o una carpeta
        if os.path.isfile(file_path):
            # Devolver el archivo al cliente como descarga adjunta
            return send_from_directory(user_folder, filename, as_attachment=True)
        else:
            # Listar el contenido de la carpeta
            files_in_folder = [f for f in os.listdir(file_path)]
            return jsonify({'contenido': files_in_folder})

    except Exception as e:
        print(f"Error en descargar_archivo: {str(e)}")
        return jsonify({'error': f'Error interno al intentar descargar {filename} para el usuario {username}'}), 500






# Ruta raíz
@app.route('/')
def home():
    return jsonify('Bienvenido')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
