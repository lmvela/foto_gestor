import sys
from copy import copy

if sys.platform.startswith('win'):
    sys.path.append("C:\\work\\02_Pers\\proyectos\\foto_gestor")
else:
    sys.path.append("/home/luis/Documentos/02_projects/fotogest/foto_gestor")
from foto_comun.foto_comun import *
from foto_db.foto_db import *
from foto_revisor_manual.foto_revisor_manual_comun import *

##
#
##
def main():

    # Revisamos imagenes para cada usuario por separado
    for user in USER_LIST:
        # Recibe los duplicados para un usuario concreto / tipo de media y procesalos
        # Imagenes
        dup_list = get_revs_user_type_db(user, TAG_TIPO_IMAGEN)
        op_code = procesa_dups_tipos(user, dup_list, TAG_TIPO_IMAGEN)
        if op_code == CLOSE_REVISION:
            sys.exit()
        # Video
        dup_list = get_revs_user_type_db(user, TAG_TIPO_VIDEO)
        op_code = procesa_dups_tipos(user, dup_list, TAG_TIPO_VIDEO)
        if op_code == CLOSE_REVISION:
            sys.exit()
        # Miniaturas
        dup_list = get_revs_user_type_db(user, TAG_TIPO_MINIATURAS)
        op_code = procesa_dups_tipos(user, dup_list, TAG_TIPO_MINIATURAS)
        if op_code == CLOSE_REVISION:
            sys.exit()

        # AUDIOS no los procesamos manualmente

        
if __name__ == "__main__":
    main()