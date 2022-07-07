import os
import sys
import shutil

if sys.platform.startswith('win'):
    sys.path.append("C:\\work\\02_Pers\\proyectos\\foto_gestor")
else:
    sys.path.append("/home/luis/Documentos/02_projects/fotogest/foto_gestor")
from foto_comun.foto_comun import *
from foto_db.foto_db import *

##
#
##
def borrar_revisado(doc, origen):
    # mover duplicado
    destino = os.path.join(PAPELERA_DIR, nombre_fichero(origen))
    try:
        shutil.move(origen, destino)
        print("MV OK: " + origen + " -> " + destino)
    except:
        print("MV ERROR: " + origen + " -> " + destino)
    # Eliminar documento DB
    ret = del_revisar_db(doc)
    print("DB revisar removed: " + str(ret))      

##
#
##
def backup_token_presente(fA, check_tokens):
    for tk in check_tokens:
        if tk in fA:
            return True
    return False

##
#
##
def procesa_dup_misma_carpeta(doc, fA, fB):
    if backup_token_presente(nombre_fichero_lower(fA), BACKUP_FILES_TOKENS):
        borrar_revisado(doc, fA)
    elif backup_token_presente(nombre_fichero_lower(fB), BACKUP_FILES_TOKENS):
        borrar_revisado(doc, fB)
    else:
        borrar_revisado(doc, fA)

##
#
##
def procesa_dup_distinta_carpeta(doc, fA, fB):
    if backup_token_presente(nombre_carpeta_lower(fA), BACKUP_FOLDER_TOKENS):
        borrar_revisado(doc, fA)
    elif backup_token_presente(nombre_carpeta_lower(fB), BACKUP_FOLDER_TOKENS):
        borrar_revisado(doc, fB)
    else:
        borrar_revisado(doc, fA)

##
# Accedemos a la colecion lista_duplicados: movemos el fichero filename a papelera y eliminamos entrada en BD
##
def main():

    # Analizamos imagenes para cada usuario por separado
    list_revision = get_all_revision_db()
    for revisar in list_revision:

        # procesar si estan en la misma carpeta
        if os.path.dirname(revisar['filename_A']) == os.path.dirname(revisar['filename_B']):
            procesa_dup_misma_carpeta(revisar, revisar['filename_A'], revisar['filename_B'])
        # Si estan en carpetas distintas: Buscamos Carpetas "Peores"
        else:
            procesa_dup_distinta_carpeta(revisar, revisar['filename_A'], revisar['filename_B'])


if __name__ == "__main__":
    main()