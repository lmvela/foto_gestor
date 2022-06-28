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
def clasificacion_completa_desde_zero(dir_a_clasificar):
    
    # Primero analizamos imagenes para cada usuario por separado
    for user in USER_LIST:
        # Analyzamos ficheros por tipo
        for lista_tipos, tag_tipo in LISTA_TIPOS_CATALOGO:
            # Get list {file, hash, size}
            dir_list_img = os.path.join(dir_a_clasificar, user)
            img_hash_list = get_list_image_hash(dir_list_img, lista_tipos)

            # Update info in DB
            for fn_hash_sz in img_hash_list:
                # Retorna un doc de lista_media
                exists_img = get_media_hash_user_db(fn_hash_sz[1], user)
                print('Existing img {0} is {1}'.format(fn_hash_sz[0], str(exists_img)))

                if exists_img is None:
                    # Es un fichero nuevo que no existe en BD
                    add_img_catalogo_db(fn_hash_sz, user, tag_tipo)
                elif exists_img['filename'] == fn_hash_sz[0]:
                    # Es un fichero que ya esta en la BD
                    img_existing_ok_db(exists_img)
                else: 
                    # Es un posible duplicado, procesalo          
                    proc_duplicado(fn_hash_sz, exists_img, user, tag_tipo)

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
def proc_duplicado(fn_hash_sz, existing_img, user, tipo):
    if nombre_fichero(fn_hash_sz[0]) != nombre_fichero(existing_img['filename']):
        # ATENCION: Mismo hash pero distinto nombre: Hay que analizar manualmente
        add_img_revision_db(fn_hash_sz, existing_img['filename'], user, tipo)
    else:
        # se trata de un duplicado
        add_img_duplicado_db(fn_hash_sz, existing_img, user, tipo)
        
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
    print_ext_summary(CATALOGO_ROOT_DIR)
    clasificacion_completa_desde_zero(CATALOGO_ROOT_DIR)

if __name__ == "__main__":
    main()