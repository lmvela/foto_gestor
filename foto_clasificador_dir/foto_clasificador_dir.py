import os
import sys

if sys.platform.startswith('win'):
    sys.path.append("C:\\work\\02_Pers\\proyectos\\foto_gestor")
else:
    sys.path.append("/home/luis/Documentos/02_projects/fotogest/foto_gestor")
from foto_comun.foto_comun import *
from foto_db.foto_db import *

##
#
##
def get_list_image_hash(root_dir, lista_tipos):
    ret_list = []
    file_list = get_file_list(root_dir, lista_tipos)
    for filename in file_list:
        hash = calculate_hash(filename)
        size = os.path.getsize(filename)
        ret_list.append((filename, hash, size))
    return ret_list

##
#
##
def proc_duplicado(nuevo_filename, existing_img, user, tipo):
    if nombre_fichero(nuevo_filename) != nombre_fichero(existing_img['filename']):
        # ATENCION: Mismo hash pero distinto nombre: Hay que analizar manualmente
        img_revision_db(nuevo_filename, existing_img['filename'], user, tipo)
    elif es_img_mejor(nuevo_filename, existing_img['filename']):
        # comprobar si nuevo_filename es "mejor" que el que hay en Bd
        img_replace_img_db(nuevo_filename, existing_img)
    else:
        # se trata de un duplicado
        img_duplicado_db(nuevo_filename, existing_img, user, tipo)
        
##
#
##
def es_img_mejor(nuevo_filename, viejo_filename):
    # Regla1: Conservar imagenes en el directorio Eventos
    if "Eventos" in nuevo_filename and "Eventos" not in viejo_filename:
        return True
    return False

##
#
##
def main():
    # Show all extensions in dirtree
    exts = set(f.split('.')[-1] for dir,dirs,files in os.walk(CATALOGO_ROOT_DIR) for f in files if '.' in f) 
    print (str(exts))

    # Primero analizamos imagenes para cada usuario por separado
    for user in USER_LIST:
        # Analyzamos ficheros por tipo
        for lista_tipos, tag_tipo in LISTA_TIPOS_CATALOGO:
            # Get list {file, hash}
            img_hash_list = get_list_image_hash(CATALOGO_ROOT_DIR + '/' + user + '/', lista_tipos)

            # Update info in DB
            for img in img_hash_list:
                exists_img = img_new_db(img[1], user)
                print('Existing img {0} is {1}'.format(img[0], str(exists_img)))

                if exists_img is None:
                    # Es un fichero nuevo que no existe en BD
                    img_add_db(img, user, tag_tipo)
                elif exists_img['filename'] == img[0]:
                    # Es un fichero que ya esta en la BD
                    img_existing_ok_db(exists_img)
                else: 
                    # Es un posible duplicado, procesalo          
                    proc_duplicado(img[0], exists_img, user, tag_tipo)


if __name__ == "__main__":
    main()