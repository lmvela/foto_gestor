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
def borrar_fichero(borr):
    # mover fichero a papelera
    origen = borr['filename']
    destino = os.path.join(PAPELERA_DIR, nombre_fichero(origen))
    try:
        shutil.move(origen, destino)
        print("MV OK: " + origen + " -> " + destino)
        # Eliminar documento DB
        ret = del_borrar_db(borr)
        print("DB borrar removed: " + str(ret))    
    except:
        print("EXCEPTION MV borrar_fichero: " + origen + " -> " + destino)

##
# Accedemos a la colecion lista_duplicados: movemos el fichero filename a papelera y eliminamos entrada en BD
##
def main():
    list_borrar = get_all_borrar_db()
    for borr in list_borrar:
        borrar_fichero(borr)

if __name__ == "__main__":
    main()