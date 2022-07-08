import os
import sys

if sys.platform.startswith('win'):
    sys.path.append("C:\\work\\02_Pers\\proyectos\\foto_gestor")
else:
    sys.path.append("/home/luis/Documentos/02_projects/fotogest/foto_gestor")
from foto_comun.foto_comun import *
from foto_db.foto_db import *

##
#   Doc de duplicados:
#        rev_doc = {
#            'filenames'  : [fn_hash_sz[0]],
#            'reference'  : existing_img['filename'],
#            'hash'       : fn_hash_sz[1],
#            'user'       : user,
#            'type'       : tipo,
#            'size'       : fn_hash_sz[2]            
#        }    
##
def borrar_duplicado(dup):
    # mover duplicado
    os.makedirs(PAPELERA_DIR, exist_ok=True)
    for origen in dup['filenames']:
        add_img_borrar_db(origen)
    # Eliminar documento DB
    ret = del_dup_db(dup)
    print("DB duplicados removed: " + str(ret))    
    return True

##
# Accedemos a la colecion lista_duplicados: movemos el fichero filename a papelera y eliminamos entrada en BD
##
def main():
    list_dups = get_all_duplicados_db()
    for dup in list_dups:
        borrar_duplicado(dup)
    # Print overall result:
    print("AUTO Dup Revisar finished. Remaining dups: " + str(count_duplicados_docs_db()))

if __name__ == "__main__":
    main()