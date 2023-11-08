from flask import Flask, request, jsonify
import metodos_api
import encriptar_rsa

# Cdo se sube un archivo se crea carpeta para el usuario dentro de datos, y dentro de cada carpeta los archivos cifrados y las contraseñas, nonce
app = Flask(__name__)

# Almacenamiento temporal para usuarios registrados (en un entorno de producción, usa una base de datos real).
usuarios_registrados = {}
#-----------------------------------------------------------------------------------------------------------------------------------------------------
# CREANDO EL ADMIN
#-----------------------------------------------------------------------------------------------------------------------------------------------------
if len(usuarios_registrados) <= 0:
    admin = metodos_api.crea_administrador()
    usuarios_registrados["admin"] = admin
print('Los usuarios registrados son: ', usuarios_registrados["admin"])

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
    data = request.get_json()
    if 'username' in data and 'password' in data:
        username = data['username']
        password = data['password']
        usuarios_registrados[username] = password
        return jsonify({'message': 'Usuario registrado exitosamente'})
    else:
        return jsonify({'error': 'Se requieren campos "username" y "password" en la solicitud'}), 400

# Endpoint de inicio de sesión
@app.route('/login', methods=['POST'])
def iniciar_sesion():
    data = request.get_json()
    if 'username' in data and 'password' in data:
        username = data['username']
        password = data['password']
        if username in usuarios_registrados and usuarios_registrados[username] == password:
            return jsonify({'message': 'Inicio de sesión exitoso'})
        else:
            return jsonify({'error': 'Credenciales inválidas'}), 401
    else:
        return jsonify({'error': 'Se requieren campos "username" y "password" en la solicitud'}), 400

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