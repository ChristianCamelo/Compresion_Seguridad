
# from encriptar.py import encriptar
#from desencriptar.py import desencriptar
from datetime import datetime

#fichero = open('pruebas/ejemplo.txt')




def escribirLog(mensaje):
    logs = open('logs.txt','a')
    now = datetime.now()
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    logs.writelines(date_time + ": " +mensaje+"\n")

def encriptarFichero():
    #encriptar(fichero)
    escribirLog("fichero encriptado con exito")

encriptarFichero()