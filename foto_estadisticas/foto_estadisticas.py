import os
import sys

#sys.path.append("C:\\work\\02_Pers\\proyectos\\foto_gestor")
sys.path.append("/home/luis/Documentos/02_projects/fotogest/foto_gestor")
from foto_comun.foto_comun import *
from foto_db.foto_db import *

def main():
    print(" Estadisticas DIRECTORIO")
    print("-------------------------")
    print("Dir: " + ROOT_DIR)
    #exts = set(f.split('.')[-1].upper() for dir,dirs,files in os.walk(ROOT_DIR) for f in files if '.' in f) 
    exts = set(f.split('.')[-1] for dir,dirs,files in os.walk(ROOT_DIR) for f in files if '.' in f) 
    print (str(exts))
    for ext in exts:
        num, tamaño = proc_list_ficheros(get_file_list(ROOT_DIR, [ext]))
        print("Extension {0}:\t{1}\t{2}".format(ext, num, tamaño))

    # Lista estadisticas sobre Directorio
    tamaño_dir = get_directory_size(ROOT_DIR)
    num_ficheros = get_total_file_list(ROOT_DIR)
    print("Totales:\t{0}\t{1}".format(num_ficheros, tamaño_dir))

    num, tamaño = proc_list_ficheros(get_file_list(ROOT_DIR, TIPOS_IMAGEN))
    print(" Imagenes:\t{0}\t{1}".format(num, tamaño))
    num, tamaño = proc_list_ficheros(get_file_list(ROOT_DIR, TIPOS_VIDEO))
    print(" Videos:\t{0}\t{1}".format(num, tamaño))
    num, tamaño = proc_list_ficheros(get_file_list(ROOT_DIR, TIPOS_AUDIO))
    print(" Audios:\t{0}\t{1}".format(num, tamaño))

    # Estadisticas sobre la base de datos
    print("")
    print(" Estadisticas BASE-DATOS")
    print("-------------------------")

    print("Numero total de documentos: " + str(get_all_count_db()))
    print("Numero total de documentos a CATALOGO: " + str(get_media_count_db()))
    print("Numero total de documentos a REVISAR: " + str(get_revisar_count_db()))
    print("Numero total de documentos a BORRAR: " + str(get_borrar_count_db()))
    print("Numero total de documentos DUPLICADOS: " + str(get_duplicados_count_db()))
    for user in USER_LIST:
        print("Usuario:\t" + user)
        for _, tipo in LISTA_TIPOS_CATALOGO:
            print("Tipo:\t\t" + tipo)
            # Numero / tamaño de ficheros / fotos / videos / audios por usuario
            print(" TOTAL:\t\t{0}".format(get_typeuser_count_db(user, tipo)))
            # Numero / tamaño de ficheros en CATALOGO
            print(" CATALOGO:\t{0}".format(get_typeuser_media_count_db(user, tipo)))
            # Numero / tamaño de ficheros a revisar
            print(" REVISAR:\t{0}".format(get_typeuser_revisar_count_db(user, tipo)))
            # Numero / tamaño de ficheros a borrar
            print(" BORRAR:\t{0}".format(get_typeuser_borrar_count_db(user, tipo)))
            # Numero / tamaño de ficheros duplicados dentro usuario
            print(" DUPLICADOS:\t{0}".format(get_typeuser_duplicados_count_db(user, tipo)))

    # Numero / tamaño de ficheros duplicados entre usuarios


    # Comparativa directorio - Base de datos
    
if __name__ == "__main__":
    main()