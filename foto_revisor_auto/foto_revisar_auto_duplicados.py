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
def borrar_duplicado(dup):
    # mover duplicado
    origen = dup['filename']
    destino = os.path.join(PAPELERA_DIR, nombre_fichero(origen))
    try:
        shutil.move(origen, destino)
        print("MV OK: " + origen + " -> " + destino)
    except:
        print("MV ERROR: " + origen + " -> " + destino)
    # Eliminar documento DB
    ret = del_dup_db(dup)
    print("DB duplicados removed: " + str(ret))    

##
# Accedemos a la colecion lista_duplicados: movemos el fichero filename a papelera y eliminamos entrada en BD
##
def main():
    list_dups = get_all_duplicados_db()
    for dup in list_dups:
        borrar_duplicado(dup)

if __name__ == "__main__":
    main()