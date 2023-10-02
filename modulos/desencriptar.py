from cryptography.fernet import Fernet
from pathlib import Path

def desencriptar(archivo,clave):
    f = Fernet(clave)
    with open(archivo, 'rb') as file: #archivo abierto solo para lectura
        datos_encriptados = file.read()

    datos = f.decrypt(datos_encriptados)

    with open(archivo, 'wb') as file: #archivo abierto solo para escritura
        file.write(datos)         #escribimos los datos desencriptados


def desencriptar_bool(archivo, clave):  # Devuelve True si se desencriptó correctamente, False si no
    f = Fernet(clave)
    with open(archivo, 'rb') as file:
        datos_encriptados = file.read()

    try:
        datos = f.decrypt(datos_encriptados)
        with open(archivo, 'wb') as file:
            file.write(datos)
        return True
    except:
        return False




# import api_desencriptar as archivos
# opcion = 0

# archivos.generar_clave()
# clave = archivos.cargar_clave()

# archivo = "archivo.txt"

# while opcion != 5:

#     print("\nSelecciona una opción:")
#     print("1. Leer archivo\n2. Agregar texto al archivo\n3. Encriptar archivo\n4. Desencriptar archivo\n5. Salir")
#     opcion = int(input("Opción: "))

#     if opcion == 1:
#         print("Contenido del archivo: ")
#         archivos.leerArchivo(archivo)

#     elif opcion == 2:
#         linea = input("Escribe una línea para introducir al archivo: ")
#         archivos.escribirArchivo(linea,archivo)

#     elif opcion == 3:
#         print("Encriptando archivo...")
#         archivos.encriptar(archivo,clave)
#     elif opcion == 4:
#         print("Desencriptando archivo...")
#         archivos.desencriptar(archivo,clave)
#     elif opcion == 5:
#         print("Adiós")
#     else:
#         print("Opción no válida")