from PIL import Image, ExifTags
from datetime import datetime
import os
import sys
import re

if sys.platform.startswith('win'):
    sys.path.append("C:\\work\\02_Pers\\proyectos\\foto_gestor")
else:
    sys.path.append("/home/luis/Documentos/02_projects/fotogest/foto_gestor")
from foto_comun.foto_comun import *
from foto_db.foto_db import *
from foto_clasificador.foto_clasificador_comun import *

##
#
##
def clasificacion_completa_desde_zero(dir_a_clasificar):
    
    # Primero analizamos imagenes para cada usuario por separado
    for user in USER_LIST:
        # Analyzamos ficheros por tipo (tipos de catalogo)
        for lista_tipos, tag_tipo in LISTA_TIPOS_CATALOGO:
            # Get list {file, hash, size}
            dir_list_img = os.path.join(dir_a_clasificar, user)
            img_hash_list = get_list_image_hash_sz(user, tag_tipo, dir_list_img, lista_tipos)

            # Update info in DB
            for fn_hash_sz in img_hash_list:
                # Retorna un doc de lista_media
                exists_img = get_media_hash_user_db(fn_hash_sz[1], user)

                if exists_img is None:
                    # Es un fichero nuevo que no existe en BD
                    media_dt, media_origen = get_fn_source(fn_hash_sz[0])
                    add_img_catalogo_db(fn_hash_sz, user, tag_tipo, media_origen, media_dt)
                    print("CATALOGO AÑADIDO: " + fn_hash_sz[0])
                elif exists_img['filename'] == fn_hash_sz[0]:
                    # Es un fichero que ya esta en la BD
                    img_existing_ok_db(exists_img)
                    print("CATALOGO YA EXISTE: " + fn_hash_sz[0])
                else: 
                    # Es un posible duplicado, procesalo          
                    proc_duplicado(fn_hash_sz, exists_img, user, tag_tipo)
                    print("CATALOGO DUPLICADO: " + fn_hash_sz[0])

        # Analyzamos ficheros por tipo (tipos a descartar)
        for lista_tipos, tag_tipo in LISTA_TIPOS_DESCARTAR:
            # Get list {file, hash, size}
            dir_list_img = os.path.join(dir_a_clasificar, user)
            img_hash_list = get_list_image_hash_sz(user, tag_tipo, dir_list_img, lista_tipos)

            # Update info in DB
            for fn_hash_sz in img_hash_list:
                add_fn_descartar_db(fn_hash_sz, user, tag_tipo)

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
def main():
    print_ext_summary(CATALOGO_ROOT_DIR)
    clasificacion_completa_desde_zero(CATALOGO_ROOT_DIR)

if __name__ == "__main__":
    main()