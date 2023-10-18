# Compresion_Seguridad

Por Mattia Sorella, Javier Escutia, Christian Camelo y Guillermo Sansano
Versión 1.0.0

Este repositorio contiene los modulos necesarios para la realizacion de la practica 1 de la asignatura Compresion y Seguridad.

El programa se compone de 4 Modulos:
  -  Interfaz: API para la integración de todos los modulos, se encarga de manejar las rutas de los archivos y visualizar los resultados e interfaz de usuario
  -  Principal: Utilidades como el log o historial de cambios
  -  Encriptacion: Funcionalidad principal numero uno, encargada de encriptar los archivos
  -  Desencriptacion: Funcionalidad principal numero dos, encargada de desencriptar los archivos

## Preparacion

Para ejecutar el programa desde la ubicación del directorio /Compresion_Seguridad se requiere instalar los modulos:
  ``` pip install pycryptodome ```
### Nota: El proyecto require la existencia de todos los directorios contenidos en este repositorio sin alterar su jerarquia ni nombres.

## Puesta en marcha

Para la ejecucion desde la carpeta "root" del proyecto se debe llamar a la ejecucion mediante Python:
```py ./interfaz.py```
### Instrucciones

Al iniciarlizar la ejecucion se debe:
  1. Clickar en "Cargar archivo"
  2. Seleccionar un archivo dentro de cualquier fichero
  3. Una vez cargado el archivo encriptado se almacenara en ./archivos_encriptados con el formato .enc
  4. El archivo encriptado se cargara ahora en la interfaz y se podra obtener su archivo original en x formato con un nuevo formateo de nombre, para ello solo de debe clickar en "Descifrar"
  5. Para limpiar los directorios de encriptados, llaves y descencriptados se puede hacer mediante el boton de "Limpiar cache" o reiniciando el programa
  6. Se recomiendo solo descifrar los archivos encriptados una sola vez para evitar errores
  7. En caso de que se quiera, se puede consultar los cambios de estado a traves del archivo ./logs.txt

## Funcionamiento

1.Mediante la libreria Tk se dibuja un GUI desde la inicializacion del programa
2.Al cargarse un archivo se encripta mediante AES 128 y se almacena una copia del archivo encriptado en un directorio local, a su vez se almacena dentro de un archivo binario el nonce utilizado por el algoritmo AES_CTR de la libreria Crypto.cypher, junto a la llave generada en el proceso
3.Cuando se desencripta un archivo se separa del archivo binario almacenado en ./keys con el mismo numero de indexacion el nonce y la llave usada durante el proceso de encriptacion, de esta forma se verifica el resultado
4.Durante el proceso de guardado se formatea el codigo binario extraido del archivo original


