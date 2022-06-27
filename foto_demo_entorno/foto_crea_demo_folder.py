import os
import sys

if sys.platform.startswith('win'):
    sys.path.append("C:\\work\\02_Pers\\proyectos\\foto_gestor")
else:
    sys.path.append("/home/luis/Documentos/02_projects/fotogest/foto_gestor")
from foto_comun.foto_comun import *
from foto_db.foto_db import *
from foto_clasificador_dir.foto_clasificador_dir import *
from foto_estadisticas.foto_estadisticas import *

def copy_file_crear_dir(src_fpath, dest_fpath):
    os.makedirs(os.path.dirname(dest_fpath), exist_ok=True)
    shutil.copy(src_fpath, dest_fpath)    

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
def crear_foto_devel_dup(img_user_demo_list):
    for list_el in img_user_demo_list:
        nom_fichero = nombre_fichero(list_el)
        f_tgt = list_el.replace(nom_fichero, "dup_mismo_nombre\\" + nom_fichero)
        copia_file_crea_dirs(list_el, f_tgt)

##
#
##
def crear_foto_devel_dup_new_name(img_user_demo_list):
    for list_el in img_user_demo_list:
        nom_fichero = nombre_fichero(list_el)
        f_tgt_pre, f_tgt_ext = os.path.splitext(nom_fichero)
        f_tgt = list_el.replace(nom_fichero, "dup_diff_nombre\\" + f_tgt_pre + "_new_name" + f_tgt_ext)
        copia_file_crea_dirs(list_el, f_tgt)

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
    img_user_demo_list = crear_foto_devel_set(FOTO_GEST_CATALGO_ORIGINAL, CATALOGO_ROOT_DIR, 10)

    # Hacemos una clasificacion completa en la BDD devel
    clasificacion_completa_desde_zero(CATALOGO_ROOT_DIR)

    # actualizamos el documento de estadisticas
    actualiza_estadisticas_catalogo()
    
    # Use case: Create duplicate with same name. 
    crear_foto_devel_dup(img_user_demo_list)

    # Hacemos una clasificacion completa en la BDD devel
    clasificacion_completa_desde_zero(CATALOGO_ROOT_DIR)    

    # actualizamos el documento de estadisticas
    actualiza_estadisticas_catalogo()

    # Use case: Create duplicate with different name. 
    crear_foto_devel_dup_new_name(img_user_demo_list)

    # Hacemos una clasificacion completa en la BDD devel
    clasificacion_completa_desde_zero(CATALOGO_ROOT_DIR)    

    # actualizamos el documento de estadisticas
    actualiza_estadisticas_catalogo()

'''

    # Use case: Create duplicate with same name. In whatsapp folder. 
    for usr, list_el in img_user_demo_list:
        for el in list_el:
            f_tgt = el.replace(ROOT_DIR, ROOT_DIR_DEMO)
            f_tgt = f_tgt.replace(usr, usr + "\\" + usr + "_dup_whatsapp")
            copia_file_crea_dirs(el, f_tgt)            

    # Use case: Create duplicate with same name. In Sent folder. 
    for usr, list_el in img_user_demo_list:
        for el in list_el:
            f_tgt = el.replace(ROOT_DIR, ROOT_DIR_DEMO)
            f_tgt = f_tgt.replace(usr, usr + "\\" + usr + "_dup_whatsapp\\Sent")
            copia_file_crea_dirs(el, f_tgt)            

    # Use case: Create whatsapp like naming
    for usr, list_el in img_user_demo_list:
        for el in list_el:
            f_tgt = el.replace(ROOT_DIR, ROOT_DIR_DEMO)
            f_tgt = f_tgt.replace(usr, usr + "\\" + usr + "_dup_diff_nombre")
            copia_file_crea_dirs(el, f_tgt)
            f_tgt_pre, f_tgt_ext = os.path.splitext(f_tgt)
            os.rename(f_tgt, f_tgt_pre + "_new_name" + f_tgt_ext)            
'''

if __name__ == "__main__":
    main()