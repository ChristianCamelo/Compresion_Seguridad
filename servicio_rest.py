import requests
import os
import json
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

def subir_archivos():

    url = "http://127.0.0.1:5000/upload"
    
    directorio_local = os.path.join(os.getcwd(), 'archivos_encriptados')
    directorio_local_llaves = os.path.join(os.getcwd(), 'keys')
    directorio_local_formatos = os.path.join(os.getcwd(), 'formatos')
    
    directorios = os.listdir(directorio_local)

    print(f'Ruta de archivos encriptados: {directorio_local}')
    print(f'Ruta de llaves: {directorio_local_llaves}')
    print(f'Ruta de formatos: {directorio_local_formatos}')

    payload_bruto ={
        'username': "admin",
        'Archivos':  {},
    }

    print(f'Ruta de llaves: ' + str(len(directorios)))

    for index, directorio in enumerate(directorios):

        ruta_archivo = os.path.join(directorio_local, 'archivo' + str(index) + '.enc')
        ruta_llave = os.path.join(directorio_local_llaves, 'llave' + str(index) + '.bin')
        ruta_formato = os.path.join(directorio_local_formatos, 'formato' + str(index) + '.txt')
        
        with open(ruta_archivo, 'r',  encoding='latin-1') as a:
            archivo = a.read()
        
        with open(ruta_llave, 'r', encoding='latin-1') as b:
            llave = b.read()

        with open(ruta_formato, 'r', encoding='latin-1') as c:
            formato = c.read()

        nuevo_archivo = {
            'Encriptado': archivo,
            'Llave': llave,
            'Formato': formato
        }
        payload_bruto['Archivos'][str(index)] = nuevo_archivo

    headers = {
    'Content-Type': 'application/json'
    }

    payload = json.dumps(payload_bruto)

    print(payload)
    response = requests.post(url, headers=headers, data=payload)
    print(response.json())

def bajar_archivos():

    url = "http://127.0.0.1:5000/download/admin/"
    response = requests.get(url)
    
    data = response.json()

    print(data)

    username = extract_key_value(data,'username')
    archivos = extract_key_value(data,'Archivos')

    user_folder = os.path.join(os.getcwd())

    for numero, archivo in archivos.items():

        directorio_archivos = os.path.join(user_folder,"archivos_encriptados")
        directorio_llaves = os.path.join(user_folder,"keys")
        directorio_formatos = os.path.join(user_folder,"formatos")

        encriptado_filename = secure_filename('archivo'+str(numero)+'.enc')
        llave_filename = secure_filename('llave'+str(numero)+'.bin')
        formato_filename = secure_filename('formato'+str(numero)+'.txt')

        encriptado_path = os.path.join(directorio_archivos, encriptado_filename)
        llave_path = os.path.join(directorio_llaves, llave_filename)
        formato_path = os.path.join(directorio_formatos, formato_filename)

        with open(encriptado_path, 'w', encoding='latin-1') as f:
            f.write(archivo["Encriptado"])

        with open(llave_path, 'w', encoding='latin-1') as f:
            f.write(archivo["Llave"])

        with open(formato_path, 'w', encoding='latin-1') as f:
            f.write(archivo["Formato"])

def extract_key_value(json_data, key):
    data = json.loads(json_data)
    value = data.get(key)
    return value 


