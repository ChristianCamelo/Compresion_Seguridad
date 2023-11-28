import os
import json
import requests
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import base64


SERVER_URL = "http://127.0.0.1:5000"
HEADERS =  {'Content-Type': 'application/json'}
DIR_LOCAL = os.path.dirname(os.path.abspath(__file__))
DIR_KEYS = os.path.join(DIR_LOCAL, 'keys')
DIR_FILES = os.path.join(DIR_LOCAL, 'archivos_desencriptados')
DIR_ENC = os.path.join(DIR_LOCAL, 'archivos_encriptados')

def subir_archivos(archivos,user):
    
    payload_bruto ={
        'username': user,
        'archivos':  {},
    }

    for index, item in enumerate(archivos):

        ruta_archivo = os.path.join(DIR_ENC, 'archivo' + str(index) + '.enc')
        ruta_llave = os.path.join(DIR_KEYS, 'llave' + str(index) + '.bin')
        
        with open(ruta_archivo, 'r',encoding='utf-8') as a:
            archivo = a.read()
        
        with open(ruta_llave, 'r',encoding='utf-8') as b:
            llave = b.read()

        archivo64 = base64.b64encode(archivo)
        llave64 = base64.b64encode(llave)
        nuevo_archivo = {
            'archivo': archivo64,
            'llave': llave64
        }
        payload_bruto['archivos'][str(index)] = nuevo_archivo

    payload = json.dumps(payload_bruto)

    print(payload)
    response = requests.post(SERVER_URL+'/upload', headers=HEADERS, data=payload)
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


