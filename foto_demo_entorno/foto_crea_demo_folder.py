import os
import sys

if sys.platform.startswith('win'):
    sys.path.append("C:\\work\\02_Pers\\proyectos\\foto_gestor")
else:
    sys.path.append("/home/luis/Documentos/02_projects/fotogest/foto_gestor")
from foto_comun.foto_comun import *
from foto_db.foto_db import *
from foto_estadisticas.foto_estadisticas import *

##
#
##
def crear_foto_devel_set(original_catalogo, devel_catalogo, num_files_devel_set):
    img_user_demo_list = []

    # Primero cogemos N imagenes del catalogo de produccion para crear un catalogo de pruebas
    for user in USER_LIST:
        # Analyzamos ficheros por tipo
        for lista_tipos, tag_tipo in LISTA_TIPOS_CATALOGO:
            # Get list {file, hash}
            img_list = get_file_list(original_catalogo + '/' + user + '/', lista_tipos, num_files_devel_set)
            img_user_demo_list.extend(img_list)

    # Copiar todos los ficheros al directorio demo
    img_user_demo_list_ret = []   
    for img_el in img_user_demo_list:
        f_tgt = img_el.replace(original_catalogo, devel_catalogo)
        copia_file_crea_dirs(img_el, f_tgt)
        img_user_demo_list_ret.append(f_tgt)

    return img_user_demo_list_ret

##
#
##
def crear_foto_devel_dup(img_user_demo_list, dup_folder_name, max_files=0):
    ctr = 0
    for list_el in img_user_demo_list:
        nom_fichero = nombre_fichero(list_el)
        f_tgt = list_el.replace(nom_fichero, dup_folder_name + "\\" + nom_fichero)
        copia_file_crea_dirs(list_el, f_tgt)
        ctr = ctr + 1
        if ctr >=max_files and max_files>0:
            return

##
#
##
def crear_foto_devel_dup_new_name(img_user_demo_list, dup_diff_folder_name, filename_postfix, max_files=0):
    ctr = 0
    for list_el in img_user_demo_list:
        nom_fichero = nombre_fichero(list_el)
        f_tgt_pre, f_tgt_ext = os.path.splitext(nom_fichero)
        f_tgt = list_el.replace(nom_fichero, dup_diff_folder_name + "\\" + f_tgt_pre + filename_postfix + f_tgt_ext)
        copia_file_crea_dirs(list_el, f_tgt)
        ctr = ctr + 1
        if ctr >=max_files and max_files>0:
            return

##
#
##
def main():

    # Pre-requisits 
    # Demo root folder does not exist
    # development DB does not exist
    if CFG_DEVEL_MODE is False:
        print("This script can only run in DEVEL mode. Set CFG_DEVEL_MODE to True")
        return

    # Create root directory
    if not os.path.isdir(FOTO_GEST_ROOT_DIR):
        os.mkdir(FOTO_GEST_ROOT_DIR)

    # Creamos un set duplicado para la validacion: Usamos el catalogo real como fuente
    img_user_demo_list = crear_foto_devel_set(FOTO_GEST_CATALGO_ORIGINAL, CATALOGO_ROOT_DIR, 1000)

    # Use case: Create duplicate with same name. 
    #crear_foto_devel_dup(img_user_demo_list, "dup_mismo_nombre", 100)

    # Use case: Create duplicate with same name. 
    #crear_foto_devel_dup(img_user_demo_list, "dup_mismo_nombre_2", 100)

    # Use case: Create duplicate with different name. 
    #crear_foto_devel_dup_new_name(img_user_demo_list, "dup_diff_nombre", "_new_name", 50)


if __name__ == "__main__":
    main()