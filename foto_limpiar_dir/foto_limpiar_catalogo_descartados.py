import os
import sys
import shutil

if sys.platform.startswith('win'):
    sys.path.append("C:\\work\\02_Pers\\proyectos\\foto_gestor")
else:
    sys.path.append("/home/luis/Documentos/02_projects/fotogest/foto_gestor")
from foto_comun.foto_comun import *

##
#
##
def get_list_image_hash(root_dir, lista_tipos):
    ret_list = []
    file_list = get_file_list(root_dir, lista_tipos)
    for filename in file_list:
        hash = calculate_hash(filename)
        size = os.path.getsize(filename)
        ret_list.append((filename, hash, size, type))
    return ret_list

##
#
##
def main():

    # Analizamos imagenes para cada usuario por separado
    for user in USER_LIST:

        # Analyzamos ficheros por tipo: Descartar ficheros que no son parte del catalogo de medios
        for lista_tipos, tag_tipo, carpeta_destino in LISTA_TIPOS_DESCARTAR:
            carpeta_destino_completa = DESCARTAR_ROOT_DIR + '/' + carpeta_destino 
            crea_carpeta(carpeta_destino_completa)
            # Get list {file, hash}
            descartar_list = get_file_list(CATALOGO_ROOT_DIR + '/' + user + '/', lista_tipos)
            for fichero in descartar_list:
                # move files 
                destino = carpeta_destino_completa + '/' + user + "_" + nombre_fichero(fichero)
                print("MV: " + fichero + " -> " + destino)
                shutil.move(fichero, destino)


if __name__ == "__main__":
    main()