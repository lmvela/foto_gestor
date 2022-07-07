from PIL import Image, ExifTags
from datetime import datetime
import os
import sys
import re

if sys.platform.startswith('win'):
    sys.path.append("C:\\work\\02_Pers\\proyectos\\foto_gestor")
else:
    sys.path.append("/home/luis/Documentos/02_projects/fotogest/foto_gestor")
from foto_comun.foto_comun import *
from foto_db.foto_db import *

##
# CONSTANTS
##

## REGEX patters for filenames with datetime information in 7 groups: (discard)(4:year)(2:mes)(2:dia) (2:h)(2:m)(2:s)
pattern_fn_dtinfo_list = [   
    r'(\\C360)_([0-9]{4})-([0-9]{2})-([0-9]{2})-([0-9]{2})-([0-9]{2})-([0-9]{2})-[0-9]{3}\.', # CAMARA   
    r'(\\)([0-9]{4})-([0-9]{2})-([0-9]{2}) ([0-9]{2})\.([0-9]{2})\.([0-9]{2})\.',  # IPAD 
    r'(IMG|VID)_([0-9]{4})([0-9]{2})([0-9]{2})_([0-9]{2})([0-9]{2})([0-9]{2})',
    r'(\\PANO)_([0-9]{4})([0-9]{2})([0-9]{2})_([0-9]{2})([0-9]{2})([0-9]{2})', # PANASONIC camara
    r'(\\)([0-9]{4})([0-9]{2})([0-9]{2})_([0-9]{2})([0-9]{2})([0-9]{2})\.', # Camara Samsung S20FE    
    r'(VID|IMG)-([0-9]{4})([0-9]{2})([0-9]{2})-WA([0-9]{1})([0-9]{1})([0-9]{1})', # Whatsapp
]

## REGEX patterns for filenames without datetime information
pattern_fn_nodtinfo_list = [
    r'MVI_[0-9]{4}\.',
    r'P1[0-9]{6}\.',
    r'DSCN[0-9]{3}\.',
    r'DSC_[0-9]{4}\.',
    r'DSC[0-9]{5}\.',
    r'Imagen [0-9]{3}\.',
    r'IMG_[0-9]{4}\.',
    r'IMG [0-9]{4}\.',
    r'IMG[0-9]{4}\.',
    r'MOV[0-9]{3}\.'
]

##
#
##
def create_fn_dt(res_groups):
    dttime_ints = [int(x) for x in res_groups]
    return (TAG_DT_ORIGIN_FN, datetime(dttime_ints[0], dttime_ints[1], dttime_ints[2], dttime_ints[3], dttime_ints[4], dttime_ints[5]))

##
#
##
def os_creation_date(path_to_file):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if sys.platform.startswith('win'):
        return datetime.fromtimestamp(os.path.getctime(path_to_file))
    else:
        stat = os.stat(path_to_file)
        try:
            return datetime.fromtimestamp(stat.st_birthtime)
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return datetime.fromtimestamp(stat.st_mtime)

##
#
##
def read_fn_dt(fn):
    try:
        # First try EXIF info
        img = Image.open(fn)
        img_exif = img.getexif()
        if img_exif is not None:
            for key, val in img_exif.items():
                if key in ExifTags.TAGS:
                    print(f'{ExifTags.TAGS[key]}:{val}')            
                if key == 0x0132 or key == 0x9003:   #DateTime or DateTimeOriginal
                    return (TAG_DT_ORIGIN_EXIF, datetime.strptime(val, '%Y:%m:%d %H:%M:%S'))
    except:
        pass    # Carry on checking other metadata extraction methode

    # If no EXIF: take the file date / time
    print("No EXIF: " + fn)
    return (TAG_DT_ORIGIN_OS, os_creation_date(fn))

##
#
##
def get_fn_source(fn):

    # CHECK if Filename contains date time info:
    for pattern in pattern_fn_dtinfo_list:
        res=re.search(pattern, fn)
        if res:
            res_groups = res.groups(1)[1:]  # Remove firs element in tuple. contains discard info
            return create_fn_dt(res_groups), TAG_ORIGEN_CAMARA
        
    # Media files without datetime info in the file name.
    # Try to extract the datetime from the file itself (EXIF, OS datetime, other?)
    media_dt = read_fn_dt(fn)
    for pattern in pattern_fn_nodtinfo_list:
        res=re.search(pattern, fn)
        if res:
            return media_dt, TAG_ORIGEN_CAMARA     

    # No info available leave default results
    return media_dt, TAG_ORIGEN_DESCONOCIDO

##
#
##
def clasificacion_completa_desde_zero(dir_a_clasificar):
    
    # Primero analizamos imagenes para cada usuario por separado
    for user in USER_LIST:
        # Analyzamos ficheros por tipo (tipos de catalogo)
        for lista_tipos, tag_tipo in LISTA_TIPOS_CATALOGO:
            # Get list {file, hash, size}
            dir_list_img = os.path.join(dir_a_clasificar, user)
            img_hash_list = get_list_image_hash_sz(dir_list_img, lista_tipos)

            # Update info in DB
            for fn_hash_sz in img_hash_list:
                # Retorna un doc de lista_media
                exists_img = get_media_hash_user_db(fn_hash_sz[1], user)
                print('Existing img {0} is {1}'.format(fn_hash_sz[0], str(exists_img)))

                if exists_img is None:
                    # Es un fichero nuevo que no existe en BD
                    media_dt, media_origen = get_fn_source(fn_hash_sz[0])
                    add_img_catalogo_db(fn_hash_sz, user, tag_tipo, media_origen, media_dt)
                elif exists_img['filename'] == fn_hash_sz[0]:
                    # Es un fichero que ya esta en la BD
                    img_existing_ok_db(exists_img)
                else: 
                    # Es un posible duplicado, procesalo          
                    proc_duplicado(fn_hash_sz, exists_img, user, tag_tipo)

        # Analyzamos ficheros por tipo (tipos a descartar)
        for lista_tipos, tag_tipo in LISTA_TIPOS_DESCARTAR:
            # Get list {file, hash, size}
            dir_list_img = os.path.join(dir_a_clasificar, user)
            img_hash_list = get_list_image_hash_sz(dir_list_img, lista_tipos)

            # Update info in DB
            for fn_hash_sz in img_hash_list:
                add_fn_descartar_db(fn_hash_sz, user, tag_tipo)


##
#
##
def get_list_image_hash_sz(root_dir, lista_tipos):
    ret_list = []
    file_list = get_file_list(root_dir, lista_tipos)
    for filename in file_list:
        hash = calculate_hash(filename)
        size = os.path.getsize(filename)
        ret_list.append((filename, hash, size))
    return ret_list

##
#
##
def proc_duplicado(fn_hash_sz, existing_img, user, tipo):
    if nombre_fichero(fn_hash_sz[0]) != nombre_fichero(existing_img['filename']):
        # ATENCION: Mismo hash pero distinto nombre: Hay que analizar manualmente
        add_img_revision_db(fn_hash_sz, existing_img['filename'], user, tipo)
    else:
        # se trata de un duplicado
        add_img_duplicado_db(fn_hash_sz, existing_img, user, tipo)
        
##
#
##
def es_img_mejor(nuevo_filename, viejo_filename):
    # Regla1: Conservar imagenes en el directorio Eventos
    if "Eventos" in nuevo_filename and "Eventos" not in viejo_filename:
        return True
    return False

##
#
##
def main():
    print_ext_summary(CATALOGO_ROOT_DIR)
    clasificacion_completa_desde_zero(CATALOGO_ROOT_DIR)

if __name__ == "__main__":
    main()