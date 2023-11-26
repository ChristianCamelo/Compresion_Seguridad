from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
import json
import metodos_api

app = Flask(__name__)

# Configuración de la carpeta de subida
app.config['UPLOAD_FOLDER'] = './datos/'
DIR_LOCAL = os.path.dirname(os.path.abspath(__file__))

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
            encriptado_filename = secure_filename('Encriptado.enc')
            llave_filename = secure_filename('Llave.bin')
            formato_filename = secure_filename('Formato.txt')

            encriptado_path = os.path.join(carpeta_archivo, encriptado_filename)
            llave_path = os.path.join(carpeta_archivo, llave_filename)
            formato_path = os.path.join(carpeta_archivo, formato_filename)

            with open(encriptado_path, 'w', encoding='latin-1') as f:
                f.write(archivo["Encriptado"])

            with open(llave_path, 'w', encoding='latin-1') as f:
                f.write(archivo["Llave"])

            with open(formato_path, 'w') as f:
                f.write(archivo["Formato"])

        return jsonify({'message': 'Archivos cargados exitosamente'})

    except Exception as e:
        print(f"Error en cargar_archivo: {str(e)}")
        return jsonify({'error': 'Error interno'}), 500




# Endpoint de descarga de archivos específicos
@app.route('/download/<username>/', methods=['GET'])
def descargar_archivo(username):
    try:
        user_folder = os.path.join(DIR_LOCAL, "datos", username)

        print(f'Ruta del directorio: {user_folder}')

        directorios = os.listdir(user_folder) # lista de todos los directorios archivo

        payload_bruto ={
            'username': username,
            'Archivos':  {}
        }

        for index, directorio in enumerate(directorios):

            ruta_repositorio_n = os.path.join(user_folder,"archivo"+str(index))

            print(f'Ruta del directorio {index} : {ruta_repositorio_n}')

            ruta_archivo = os.path.join(ruta_repositorio_n, 'Encriptado.enc')
            ruta_llave = os.path.join(ruta_repositorio_n, 'Llave.bin')
            ruta_formato = os.path.join(ruta_repositorio_n, 'Formato.txt')

            print(f'Ruta del archivo: {ruta_archivo}')
            print(f'Ruta de la llave: {ruta_llave}')

            with open(ruta_archivo, 'rb') as a:
                archivo = a.read()
        
            with open(ruta_llave, 'rb') as b:
                llave = b.read()    

            with open(ruta_formato, 'rb') as c:
                formato = c.read()  

            nuevo_archivo = {
                'Encriptado': archivo.decode('latin1'),
                'Llave': llave.decode('latin1'),
                'Formato': str(formato)
            }

            payload_bruto['Archivos'][str(index)] = nuevo_archivo


        payload = json.dumps(payload_bruto)
        print(f'{payload}')
        return jsonify(payload)

    except Exception as e:
        return jsonify({'error': f'Error interno al intentar descargar'}), 500


# Ruta raíz
@app.route('/')
def home():
    return jsonify('Bienvenido')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
