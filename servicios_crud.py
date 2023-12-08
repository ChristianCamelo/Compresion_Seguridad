import os
import json
import requests
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from encriptar import encriptarCompartido, encriptar
from servicios_auth import getUser
import base64


SERVER_URL = "http://127.0.0.1:5000"
HEADERS =  {'Content-Type': 'application/json'}
DIR_LOCAL = os.path.dirname(os.path.abspath(__file__))
DIR_KEYS = os.path.join(DIR_LOCAL, 'keys')
DIR_FILES = os.path.join(DIR_LOCAL, 'archivos_desencriptados')
DIR_ENC = os.path.join(DIR_LOCAL, 'archivos_encriptados')

def upload():
    
    with open('config.json', 'r') as file:
        data = json.load(file) 
        user = data.get('user')
        k_login = data.get('k_login')

    archivos = os.listdir(DIR_ENC)

    payload_bruto ={
        'user': user,
        'k_login': k_login,
        'archivos':  {}
    }

    for index, item in enumerate(archivos):

        ruta_archivo = os.path.join(DIR_ENC, 'archivo' + str(index) + '.enc')
        ruta_llave = os.path.join(DIR_KEYS, 'key' + str(index) + '.bin')
        
        with open(ruta_archivo, 'rb') as a:
            archivo = a.read()
        
        with open(ruta_llave, 'rb') as b:
            llave = b.read()

        nuevo_archivo = {
            'archivo': formater64(archivo),
            'key': formater64(llave)
        }
        payload_bruto['archivos'][str(index)] = nuevo_archivo

    payload = json.dumps(payload_bruto)

    print(payload)
    response = requests.post(SERVER_URL+'/upload', headers=HEADERS, data=payload)
    return True

def downloadOwn():

    with open('config.json', 'r') as file:
        data = json.load(file) 
        user = data.get('user')
        k_login = data.get('k_login')

    payload_bruto ={
        'user': user,
        'k_login':  k_login
    }

    payload = json.dumps(payload_bruto)

    response = requests.get(SERVER_URL+"/download",headers=HEADERS, data=payload)
    data = response.json()

    archivos = data['archivos']

    user_folder = os.path.join(os.getcwd())

    for numero, archivo in archivos.items():

        directorio_archivos = os.path.join(user_folder,"archivos_encriptados")
        directorio_llaves = os.path.join(user_folder,"keys")

        encriptado_filename = secure_filename('archivo'+str(numero)+'.enc')
        llave_filename = secure_filename('key'+str(numero)+'.bin')

        encriptado_path = os.path.join(directorio_archivos, encriptado_filename)
        llave_path = os.path.join(directorio_llaves, llave_filename)

        with open(encriptado_path, 'wb') as f:
            f.write(reverse_formater64(archivo["archivo"]))

        with open(llave_path, 'wb') as f:
            f.write(reverse_formater64(archivo["key"]))

def shareFile(fichero,receptor):
    
    receptorkpub = getUser(receptor)
    fichero_encriptado = encriptarCompartido(fichero,receptorkpub)
    
    with open('config.json', 'r') as file:
        data = json.load(file) 
        user = data.get('user')
        k_login = data.get('k_login')
    
    payload_bruto ={
        'user': user,
        'k_login': k_login,
        'receptor': receptor,
        'data':  {
            'archivo': fichero_encriptado[0],
            'key': fichero_encriptado[1]
        }
    }
    payload = json.dumps(payload_bruto)
    response = requests.post(SERVER_URL+'/share', headers=HEADERS, data=payload)
    return response

def downloadShared():

    with open('config.json', 'r') as file:
        data = json.load(file) 
        user = data.get('user')
        k_login = data.get('k_login')

    payload_bruto ={
        'user': user,
        'k_login':  k_login
    }

    payload = json.dumps(payload_bruto)
    response = requests.get(SERVER_URL+"/share",headers=HEADERS,data=payload)
    data = response.json()

    archivos = data.get('archivos')

    user_folder = os.path.join(os.getcwd())
    directorio_archivos = os.path.join(user_folder,"archivos_encriptados_compartidos")
    directorio_llaves = os.path.join(user_folder,"keys_compartidos")

    archivos = data['archivos']

    user_folder = os.path.join(os.getcwd())

    for numero, archivo in archivos.items():

        encriptado_filename = secure_filename('archivo'+str(numero)+'.enc')
        llave_filename = secure_filename('key'+str(numero)+'.bin')

        encriptado_path = os.path.join(directorio_archivos, encriptado_filename)
        llave_path = os.path.join(directorio_llaves, llave_filename)

        with open(encriptado_path, 'wb') as f:
            f.write(reverse_formater64(archivo["archivo"]))

        with open(llave_path, 'wb') as f:
            f.write(reverse_formater64(archivo["key"]))

def getNames(dir_path):
    names = []
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            names.append(file)
    return names

def extract_key_value(json_data, key):
    data = json.loads(json_data)
    value = data.get(key)
    return value 

def formater64(data):
    return base64.b64encode(data).decode('utf-8')

def reverse_formater64(encoded_data):
    return base64.b64decode(encoded_data.encode('utf-8'))

