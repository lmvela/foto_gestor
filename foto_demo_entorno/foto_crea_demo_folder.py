import os
import sys

if sys.platform.startswith('win'):
    sys.path.append("C:\\work\\02_Pers\\proyectos\\foto_gestor")
else:
    sys.path.append("/home/luis/Documentos/02_projects/fotogest/foto_gestor")
from foto_comun.foto_comun import *
from foto_db.foto_db import *

def copy_file_crear_dir(src_fpath, dest_fpath):
    os.makedirs(os.path.dirname(dest_fpath), exist_ok=True)
    shutil.copy(src_fpath, dest_fpath)    

##
#
##
def main():

    # Create demo root directory
    if not os.path.isdir(ROOT_DIR_DEMO):
        os.mkdir(ROOT_DIR_DEMO)
    img_user_demo_list = []
    # Primero analizamos imagenes para cada usuario por separado
    for user in USER_LIST:
        img_demo_list = []
        # Analyzamos ficheros por tipo
        for lista_tipos, tag_tipo in LISTA_TIPOS_CATALOGO:
            # Get list {file, hash}
            img_list = get_file_list(CATALOGO_ROOT_DIR + '/' + user + '/', lista_tipos, 1000)
            img_demo_list.extend(img_list)
        img_user_demo_list.append((user, img_demo_list))

    # Copiar todos los ficheros al directorio demo
    for usr, list_el in img_user_demo_list:
        for el in list_el:
            f_tgt = el.replace(ROOT_DIR, ROOT_DIR_DEMO)
            copia_file_crea_dirs(el, f_tgt)

    # Use case: Create duplicate with same name. 
    for usr, list_el in img_user_demo_list:
        for el in list_el:
            f_tgt = el.replace(ROOT_DIR, ROOT_DIR_DEMO)
            f_tgt = f_tgt.replace(usr, usr + "\\" + usr + "_dup_mismo_nombre")
            copia_file_crea_dirs(el, f_tgt)

    # Use case: Create duplicate with different name. 
    for usr, list_el in img_user_demo_list:
        for el in list_el:
            f_tgt = el.replace(ROOT_DIR, ROOT_DIR_DEMO)
            f_tgt = f_tgt.replace(usr, usr + "\\" + usr + "_dup_diff_nombre")
            copia_file_crea_dirs(el, f_tgt)
            f_tgt_pre, f_tgt_ext = os.path.splitext(f_tgt)
            os.rename(f_tgt, f_tgt_pre + "_new_name" + f_tgt_ext)

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


if __name__ == "__main__":
    main()