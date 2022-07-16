import os
import sys

if sys.platform.startswith('win'):
    sys.path.append("C:\\work\\02_Pers\\proyectos\\foto_gestor")
else:
    sys.path.append("/home/luis/Documentos/02_projects/fotogest/foto_gestor")
from foto_comun.foto_comun import *
from foto_db.foto_db import *
from foto_clasificador.foto_clasificador_catologo import *
from foto_estadisticas.foto_estadisticas import *

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

    # Hacemos una clasificacion completa en la BDD devel
    clasificacion_completa_desde_zero(CATALOGO_ROOT_DIR)

    # actualizamos el documento de estadisticas
    actualiza_estadisticas_catalogo()

if __name__ == "__main__":
    main()