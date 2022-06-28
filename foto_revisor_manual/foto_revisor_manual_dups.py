import sys
from copy import copy
import os
import cv2
import numpy as np

if sys.platform.startswith('win'):
    sys.path.append("C:\\work\\02_Pers\\proyectos\\foto_gestor")
else:
    sys.path.append("/home/luis/Documentos/02_projects/fotogest/foto_gestor")
from foto_comun.foto_comun import *
from foto_db.foto_db import *

##
#
##
def ResizeWithAspectRatio(image, width=None, height=None, inter=cv2.INTER_AREA):
    dim = None
    (h, w) = image.shape[:2]

    if width is None and height is None:
        return image
    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))

    return cv2.resize(image, dim, interpolation=inter)

##
#
##
def genera_imagen_combinada(img_1, img_2, barra_medio=50):
    h1, w1 = img_1.shape[:2]
    h2, w2 = img_2.shape[:2]

    # Añadir 10 pixels balncos en medio
    img_3 = np.zeros((max(h1, h2), w1+w2+barra_medio, 3), dtype=np.uint8)
    img_3[:,:] = (255,255,255)

    img_3[:h1, :w1, :3] = img_1
    img_3[:h2, w1+barra_medio:w1+w2+barra_medio, :3] = img_2

    return img_3

##
#
##
def muestra_img_recibe_op(imS, user, fn_1, fn_2):

    WindowName=user + " => REF: " + fn_1.replace(FOTO_GEST_ROOT_DIR, "") + " vs DUP: " + fn_2.replace(FOTO_GEST_ROOT_DIR, "")

    # These line will force the window to be on top with focus.
    cv2.namedWindow(WindowName)
    cv2.moveWindow(WindowName, 200, 200)
    cv2.imshow(WindowName, imS)

    # Note waitKey return 0's for arrows in windows platform. Use waitKeyEx
    op_code = cv2.waitKeyEx()   
    print("Key: " + str(op_code))
    op_code = interpreta_op_code_plataforma(op_code)

    # Close window if it has not been closed
    if op_code != -1:
        cv2.destroyWindow(WindowName)      
    return op_code

##
#
##
def procesa_duplicado(dup, fn_delete_list):
    dup_cp_ref = copy(dup['reference'])
    dup_cp_filenames = copy(dup['filenames'])
    print("Ficheros a borrar: " + str(fn_delete_list))

    # modify dup doc according to user selection for deleting    
    if dup['reference'] in fn_delete_list:
        dup_cp_ref=''
    iter_list = copy(dup_cp_filenames)
    for el in iter_list:
        if el in fn_delete_list:
            dup_cp_filenames.remove(el)
    
    # Procesamos los resultados en dup_cp:

    # User quiere borrar este archivo completamente
    if dup_cp_ref=='' and len(dup_cp_filenames)==0:
        # Borra la referencia del catalogo
        del_media_hash_filename_db(dup['hash'], dup['reference'])
        # Borra todos los duplicados
        for el in dup['filenames']:
            add_img_borrar_db(el)
        # Borra el duplicado
        del_dup_db(dup)

    # User quiere borrar las copias de este archivo 
    elif dup_cp_ref!='' and len(dup_cp_filenames)==0:
        # Borra todos los duplicados
        for el in dup['filenames']:
            add_img_borrar_db(el)
        # Borra el duplicado (ya no existen duplicados)
        del_dup_db(dup)

    # User quiere borrar solo algunas copias del archivo
    elif dup_cp_ref!='' and len(dup_cp_filenames)<len(dup['filenames']):
        # Borra los duplicados
        iter_list = copy(dup['filenames'])
        for el in iter_list:
            if el in fn_delete_list:
                add_img_borrar_db(el)
                dup['filenames'].remove(el)
        # Actualizamos el duplicado (tenemos un duplicado todavia con nueva informacion)
        update_dup_db(dup)

    # User quiere borrar la referencia y las copias de este archivo menos una
    elif dup_cp_ref=='' and len(dup_cp_filenames)==1:
        # Borra la antigua referencia
        add_img_borrar_db(dup['reference'])
        # Actualiza la referencia del catalogo
        update_img_filename_db(dup_cp_filenames[0], dup['reference'], dup['hash'])
        # Borra el duplicado (ya no existen duplicados)
        del_dup_db(dup)

    # User quiere borrar la referencia y las copias de este archivo menos varias
    elif dup_cp_ref=='' and len(dup_cp_filenames)>1:
        # Borra la antigua referencia
        add_img_borrar_db(dup['reference'])
        # Actualiza la referencia del catalogo (Cogemos la primera copia como nueva referencia)
        update_img_filename_db(dup_cp_filenames[0], dup['reference'], dup['hash'])
        dup['reference']=dup_cp_filenames[0]
        dup['filenames'].remove(dup['reference'])
        # Actualizamos el duplicado (tenemos un duplicado todavia con nueva informacion)
        update_dup_db(dup)

    else:
        print("ERROR: Gestion duplicados da un caso imprevisto. Revisar arbol de decision")

##
# Funcion principal para procesar duplicados.
# input: usuario y lista de duplicados a procesar
##
def procesa_dups(user, dup_list):

    for dup in dup_list:
        fn_delete_list = []
        for fn in dup['filenames']:
            fn_1 = dup['reference']
            fn_2 = fn
            img_1 = cv2.imread(fn_1)
            img_2 = cv2.imread(fn_2)
            
            if False: # TBD: if img_1==None or img_2==None:
                print("ERROR procesa dups. Imagen NULL: {0} {1}". format(str(img_1), str(img_2)))
            else:
                img_revision = genera_imagen_combinada(img_1, img_2)
                imS = ResizeWithAspectRatio(img_revision, width=960)
                op_code = muestra_img_recibe_op(imS, user, fn_1, fn_2)

                if op_code == CLOSE_REVISION:
                    sys.exit()  

                if op_code == KEEP_RIGHT:
                    fn_delete_list.append(fn_1)
                if op_code == KEEP_LEFT:
                    fn_delete_list.append(fn_2)
                if op_code == KEEP_BOTH:
                    # No hacer nada, mantenemos esto como duplicado
                    pass
                if op_code == KEEP_NONE:
                    fn_delete_list.append(fn_1)
                    fn_delete_list.append(fn_2)
        
        # El usuario ya ha escogido las copias que quiere borrar: procesamos
        if len(fn_delete_list) > 0:
            procesa_duplicado(dup, fn_delete_list)
    return REVISION_FINISHED_OK

##
#
##
def main():

    # Revisamos imagenes para cada usuario por separado
    for user in USER_LIST:
        # Recibe los duplicados para un usuario concreto y procesalos
        dup_list = get_dups_user_db(user, 'IMG')
        op_code = procesa_dups(user, dup_list)

        if op_code == CLOSE_REVISION:
            sys.exit()
        
if __name__ == "__main__":
    main()