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
    os.mkdir(ROOT_DIR_DEMO)

    #

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