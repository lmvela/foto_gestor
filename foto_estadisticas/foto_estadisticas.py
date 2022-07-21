import os
import sys
from datetime import datetime

if sys.platform.startswith('win'):
    sys.path.append("C:\\work\\02_Pers\\proyectos\\foto_gestor")
else:
    sys.path.append("/home/luis/Documentos/02_projects/fotogest/foto_gestor")
from foto_comun.foto_comun import *
from foto_db.foto_db import *


def print_estadisticas_db():
    # Estadisticas sobre la base de datos
    print("")
    print(" Estadisticas BASE-DATOS")
    print("-------------------------")
    print("Lista users en catalogo: " + str(get_users_catalogo_db()))
    print("Numero hash repetidos (cross-user): " + str(count_hash_repetidos_catalogo_db()))
    print("Numero hash repetidos (por user):" + str(count_hash_repetidos_catalogo_por_user_db()))

    print("Total docs:\t\t" + str(count_all_docs_db()))
    print("Total docs CATALOGO:\t{0}/{1}".format(str(count_media_docs_db(), get_size_media_db())))
    count_rev, size_rev = get_count_size_rev_db()
    print("Total docs REVISAR:\t{0}/{1}".format(count_rev, size_rev))
    count_rev, size_rev = get_count_size_dup_db()
    print("Total docs DUPLICADOS:\t{0}/{1}".format(count_rev, size_rev))
    print("Total docs BORRAR:\t{0}".format(str(count_borrar_docs_db())))
    for user in USER_LIST:
        for _, tipo in LISTA_TIPOS_CATALOGO:
            # Numero / tamaño de ficheros / fotos / videos / audios por usuario
            print("")
            print(user + " " + tipo + ":\t\t\t" + str(count_typeuser_docs_db(user, tipo)))
            # Numero / tamaño de ficheros en CATALOGO
            print("-> Catalogo\Dups\Revs\Borrar:\t{0}\{1}\{2}\{3}".format(\
                count_typeuser_media_docs_db(user, tipo),\
                count_typeuser_duplicados_docs_db(user, tipo),\
                count_typeuser_revisar_docs_db(user, tipo),\
                count_typeuser_borrar_docs_db(user, tipo),\
                ))

##
#
##
def actualiza_estadisticas_catalogo():
    count_rev, size_rev = get_count_size_rev_db()
    count_dup, size_dup = get_count_size_dup_db()    
    stats_doc = {
        'datetime'          : datetime.now(),
        'users'             : get_users_catalogo_db(),
        'hash_dup_total'    : count_hash_repetidos_catalogo_db(),
        'hash_dup_user'     : count_hash_repetidos_catalogo_por_user_db(),
        'total_docs'        : count_all_docs_db(),
        'total_media'       : count_media_docs_db(),
        'total_revisar'     : count_rev,
        'total_borrar'      : count_borrar_docs_db(),
        'total_dup'         : count_dup,
        'size_media'        : get_size_media_db(),
        'size_revisar'      : size_rev,
        'size_dup'          : size_dup,
        'user_details'      : get_user_details()
    }    
    # Estadisticas sobre la base de datos
    add_stats_db(stats_doc)

##
#
##
def get_user_details():
    user_det = {}
    for user in USER_LIST:
        user_type_det = {}
        for name, tipo in LISTA_TIPOS_CATALOGO:
            file_type_det = {}
            file_type_det['type_total'] = count_typeuser_docs_db(user, tipo)
            file_type_det['type_media'] = count_typeuser_media_docs_db(user, tipo)
            file_type_det['type_revisar'] = count_typeuser_revisar_docs_db(user, tipo)
            file_type_det['type_borrar'] = count_typeuser_borrar_docs_db(user, tipo)
            file_type_det['type_dup'] = count_typeuser_duplicados_docs_db(user, tipo)
            user_type_det[tipo] = file_type_det
        user_det[user]=user_type_det
    return user_det
    
##
#
##
def print_estadisticas_dir(desc, dir, n_files, s_files, n_aud_files, s_aud_files, n_img_files, \
    s_img_files, n_vid_files, s_vid_files, n_min_files, s_min_files, n_desc_files, s_desc_files):

    print("")
    print(" Estadisticas DIRECTORIO: " + desc)
    print("-----------------------------------------------")

    # Get list of extensions in the catalog
    #exts = set(f.split('.')[-1].upper() for dir,dirs,files in os.walk(CATALOGO_ROOT_DIR) for f in files if '.' in f) 
    exts = set(f.split('.')[-1] for dir,dirs,files in os.walk(dir) for f in files if '.' in f) 

    # Print extension information
    if len(exts) > 0:
        print (str(exts))
    
    # Print number of files per extension
    n_files_ext = 0
    for ext in exts:
        num, tamaño = proc_list_ficheros(get_file_list(dir, [ext]))
        print("Extension {0}:\t{1}\t{2}".format(ext, num, tamaño))
        n_files_ext = n_files_ext + num
    print("Suma Ext:\t\t{0}".format(n_files_ext))

    print("Totales:\t{0}\t{1}".format(n_files, s_files))
    print(" Audios:\t{0}\t{1}".format(n_aud_files, s_aud_files))    
    print(" Imagenes:\t{0}\t{1}".format(n_img_files, s_img_files))
    print(" Videos:\t{0}\t{1}".format(n_vid_files, s_vid_files))
    print(" Miniaturas:\t{0}\t{1}".format(n_min_files, s_min_files))
    print(" Descartar:\t{0}\t{1}".format(n_desc_files, s_desc_files))
    print("N files check: " + str(n_aud_files+n_img_files+n_vid_files+n_min_files+n_desc_files) + "/" + str(n_files))

##
#
##
def get_files_info(root_dir):
    n_files = get_total_file_list(root_dir) 
    s_files = get_directory_size(root_dir)
    n_aud_files, s_aud_files = proc_list_ficheros(get_file_list(root_dir, TIPOS_AUDIO))
    n_img_files, s_img_files = proc_list_ficheros(get_file_list(root_dir, TIPOS_IMAGEN))
    n_vid_files, s_vid_files = proc_list_ficheros(get_file_list(root_dir, TIPOS_VIDEO))
    n_min_files, s_min_files = proc_list_ficheros(get_file_list(root_dir, TIPOS_MINIATURAS))
    n_desc_files, s_desc_files = proc_list_ficheros(get_file_lists(root_dir, LISTA_TIPOS_DESCARTAR))
    return n_files, s_files, n_aud_files, s_aud_files, n_img_files, s_img_files, n_vid_files, s_vid_files, n_min_files, s_min_files, n_desc_files, s_desc_files

##
#
##
def main():
    # Get Catalog files in catalog
    n_files, s_files, n_aud_files, s_aud_files, n_img_files, s_img_files, n_vid_files, s_vid_files, n_min_files, s_min_files, n_desc_files, s_desc_files = \
        get_files_info(CATALOGO_ROOT_DIR)
    print_estadisticas_dir("catalogo", CATALOGO_ROOT_DIR, n_files, s_files, n_aud_files, s_aud_files, n_img_files, s_img_files, n_vid_files, s_vid_files, n_min_files, s_min_files, n_desc_files, s_desc_files)

    # Get Catalog files in catalog
    n_files, s_files, n_aud_files, s_aud_files, n_img_files, s_img_files, n_vid_files, s_vid_files, n_min_files, s_min_files, n_desc_files, s_desc_files = \
        get_files_info(IMPORTAR_NUEVOS_DIR)
    print_estadisticas_dir("importar", IMPORTAR_NUEVOS_DIR, n_files, s_files, n_aud_files, s_aud_files, n_img_files, s_img_files, n_vid_files, s_vid_files, n_min_files, s_min_files, n_desc_files, s_desc_files)

    # Get Catalog files in catalog
    n_files, s_files, n_aud_files, s_aud_files, n_img_files, s_img_files, n_vid_files, s_vid_files, n_min_files, s_min_files, n_desc_files, s_desc_files = \
        get_files_info(CUARENTENA_NUEVOS_DIR)
    print_estadisticas_dir("cuarentena", CUARENTENA_NUEVOS_DIR, n_files, s_files, n_aud_files, s_aud_files, n_img_files, s_img_files, n_vid_files, s_vid_files, n_min_files, s_min_files, n_desc_files, s_desc_files)

    # Get Catalog files in catalog
    n_files, s_files, n_aud_files, s_aud_files, n_img_files, s_img_files, n_vid_files, s_vid_files, n_min_files, s_min_files, n_desc_files, s_desc_files = \
        get_files_info(RECHAZADOS_NUEVOS_DIR)
    print_estadisticas_dir("rechazados", RECHAZADOS_NUEVOS_DIR, n_files, s_files, n_aud_files, s_aud_files, n_img_files, s_img_files, n_vid_files, s_vid_files, n_min_files, s_min_files, n_desc_files, s_desc_files)

    # Get Catalog files in catalog
    n_files, s_files, n_aud_files, s_aud_files, n_img_files, s_img_files, n_vid_files, s_vid_files, n_min_files, s_min_files, n_desc_files, s_desc_files = \
        get_files_info(PAPELERA_DIR)
    print_estadisticas_dir("papelera", PAPELERA_DIR, n_files, s_files, n_aud_files, s_aud_files, n_img_files, s_img_files, n_vid_files, s_vid_files, n_min_files, s_min_files, n_desc_files, s_desc_files)

    # Actualiza tabla estadisticas DB
    actualiza_estadisticas_catalogo()
    # Print por pantalla
    print_estadisticas_db()
    
if __name__ == "__main__":
    main()