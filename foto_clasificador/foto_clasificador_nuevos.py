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
def calcular_dir_fechas(media_dt, origin_fn, dir_destino, user):
    media_dt_dt = media_dt[1]
    path_fechas = os.path.join(dir_destino, user, FECHAS_DIR, media_dt_dt.strftime("%Y"), media_dt_dt.strftime("%Y_%m"))
    return os.path.join(path_fechas, nombre_fichero(origin_fn))
    
##
#
##
def clasificacion_nuevos(dir_a_clasificar, dir_destino, dir_rechazados, dir_cuarentena):
    
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
                    target_fn = calcular_dir_fechas(media_dt, fn_hash_sz[0], dir_destino, user)
                    # Copialo a carpeta Fechas
                    mueve_file_con_fecha_crea_dirs(fn_hash_sz[0], target_fn)
                    # Añade doc a la BD
                    nuevo_fn_hash_sz = (target_fn, fn_hash_sz[1], fn_hash_sz[2])
                    add_img_catalogo_db(nuevo_fn_hash_sz, user, tag_tipo, media_origen, media_dt)
                    print("NUEVO IMPORTADO: " + target_fn)
                elif nombre_fichero(exists_img['filename']) == nombre_fichero(fn_hash_sz[0]):
                    # Es un fichero que ya esta en la BD (Con el mismo0 nombre)
                    target_fn = os.path.join(dir_rechazados, user, nombre_fichero(fn_hash_sz[0]))
                    mueve_file_con_fecha_crea_dirs(fn_hash_sz[0], target_fn)
                    print("NUEVO RECHAZADO ya existe en BD: " + fn_hash_sz[0])
                else: 
                    # Un fichero con el mismo hash y user existe en BD pero con otro nombre
                    # Hay que revisar manual: ponemos en cuarentena
                    target_fn = os.path.join(dir_cuarentena, user, nombre_fichero(fn_hash_sz[0]))
                    mueve_file_con_fecha_crea_dirs(fn_hash_sz[0], target_fn)
                    print("NUEVO CUARENTENA: " + fn_hash_sz[0])
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
    print_ext_summary(IMPORTAR_NUEVOS_DIR)
    clasificacion_nuevos(IMPORTAR_NUEVOS_DIR, CATALOGO_ROOT_DIR, \
        RECHAZADOS_NUEVOS_DIR, CUARENTENA_NUEVOS_DIR)

if __name__ == "__main__":
    main()