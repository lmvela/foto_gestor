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
def muestra_img_recibe_op(tipo_media, total_dup_fns, current_dup_fn, total_dups, current_dup, imS, user, fn_1, fn_2):

    WindowName=user + " " + tipo_media + " " + str(current_dup) + "/" + str(total_dups) +  " " +\
        str(current_dup_fn) + "/" + str(total_dup_fns) + " " +\
        " => REF: " + fn_1.replace(os.path.join(CATALOGO_ROOT_DIR, user), "") + " vs " + \
        fn_2.replace(os.path.join(CATALOGO_ROOT_DIR, user), "")

    # These line will force the window to be on top with focus.
    cv2.namedWindow(WindowName)
    cv2.moveWindow(WindowName, 200, 200)
    cv2.imshow(WindowName, imS)

    # Note waitKey return 0's for arrows in windows platform. Use waitKeyEx
    if sys.platform.startswith('win'):
        op_code = cv2.waitKeyEx()   
    else:        
        while True:
            op_code = cv2.waitKeyEx(100) # change the value from the original 0 (wait forever) to something appropriate
            if op_code in VALID_KEY_REVISOR_MANUAL and op_code != -1:
                break
            if cv2.getWindowProperty(WindowName, cv2.WND_PROP_VISIBLE) < 1:        
                break   
    print("Key: " + str(op_code))
    op_code = interpreta_op_code_plataforma(op_code)

    # Close window if it has not been closed
    if op_code != CLOSED_WINDOW:
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
def procesa_dups_tipos(user, dup_list, tipo_media):
    current_dup = 0
    for dup in dup_list:
        total_dups = dup_list.retrieved
        fn_delete_list = []
        current_dup = current_dup + 1

        current_dup_fn = 0
        total_dup_fns = len(dup['filenames'])
        for fn in dup['filenames']:
            fn_1 = dup['reference']
            fn_2 = fn
            img_loaded_ok = True
            current_dup_fn = current_dup_fn + 1

            # Recupera imagen para crear imagen combinada de revision
            if tipo_media==TAG_TIPO_IMAGEN or tipo_media==TAG_TIPO_MINIATURAS:
                img_1 = cv2.imread(fn_1)
                img_2 = cv2.imread(fn_2)
            elif tipo_media==TAG_TIPO_VIDEO:
                vidcap_1 = cv2.VideoCapture(fn_1)
                success_1,img_1 = vidcap_1.read()
                vidcap_2 = cv2.VideoCapture(fn_2)
                success_2,img_2 = vidcap_2.read()
                # Si no podemos recuperar los primeros frames del video
                if success_2==False or success_1==False:
                    img_loaded_ok = False
            else:
                # No podemos comparar el resto de tipos.
                img_loaded_ok =False 
            
            if img_loaded_ok == False: 
                print("ERROR procesa dups no es posible. Imagenes: {0} {1}". format(str(fn_1), str(fn_2)))
            else:
                img_revision = genera_imagen_combinada(img_1, img_2)
                imS = ResizeWithAspectRatio(img_revision, width=960)
                op_code = muestra_img_recibe_op(tipo_media, total_dup_fns, current_dup_fn, \
                    total_dups, current_dup, imS, user, fn_1, fn_2)

                if op_code == CLOSE_REVISION:
                    return CLOSE_REVISION  

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
