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
def backup_token_in(filename):
    for token_backup in BACKUP_TOKEN_LIST:
        if token_backup in filename:
            return True
    return False

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
# Hay que borrar un filename de un doc de duplicados
##
def procesa_dup_filename(dup, dup_fn):
    del_borrar_fn_dup_db(dup, dup_fn)
    add_img_borrar_db(dup_fn)

##
# Hay que reemplazar el reference de un duplicado y actualizar la lista_media
##
def procesa_dup_reference(dup, new_reference, len_fn_dup):
    add_img_borrar_db(dup['reference'])
    update_reference_dup_db(dup, new_reference)
    update_reference_media_db(dup['hash'], dup['user'], new_reference)
    del_borrar_fn_dup_db(dup, new_reference)
    # Si el dup solo tenia un filename ... se puede borrar el dup completo
    if len_fn_dup == 1:
        del_dup_db(dup)    

##
# Accedemos a la colecion lista_duplicados: movemos el fichero filename a papelera y eliminamos entrada en BD
##
def main():
    list_dups = get_all_duplicados_db()
    for dup in list_dups:
        cp_du_fns = dup['filenames'].copy()
        for dup_fn in dup['filenames']:
            if backup_token_in(dup_fn):
                procesa_dup_filename(dup, dup_fn)
                cp_du_fns.remove(dup_fn)
        # Si no quedan dups: podemos quitar el duplicado de la lista
        # Y ya hemos acabado
        if len(cp_du_fns) == 0:       
            del_dup_db(dup)
        # Aun queda algun fn
        # Miramos si el reference se puede quitar
        else:
            if backup_token_in(dup['reference']):
                # Reemplazamos el reference por el primer fn que tenemos en la lista limpia de backups: cp_du_fns
                procesa_dup_reference(dup, cp_du_fns[0], len(cp_du_fns))
           
    # Print overall result:
    print("AUTO Dup Revisar finished. Remaining dups: " + str(count_duplicados_docs_db()))

if __name__ == "__main__":
    main()