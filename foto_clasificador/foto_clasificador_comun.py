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
    (r'(\\C360)_([0-9]{4})-([0-9]{2})-([0-9]{2})-([0-9]{2})-([0-9]{2})-([0-9]{2})-[0-9]{3}\.', TAG_ORIGEN_CAMARA), # CAMARA   
    (r'(\\)([0-9]{4})-([0-9]{2})-([0-9]{2}) ([0-9]{2})\.([0-9]{2})\.([0-9]{2})\.', TAG_ORIGEN_CAMARA), # IPAD 
    (r'(IMG|VID)_([0-9]{4})([0-9]{2})([0-9]{2})_([0-9]{2})([0-9]{2})([0-9]{2})', TAG_ORIGEN_CAMARA), 
    (r'(\\PANO)_([0-9]{4})([0-9]{2})([0-9]{2})_([0-9]{2})([0-9]{2})([0-9]{2})', TAG_ORIGEN_CAMARA),  # PANASONIC camara
    (r'(\\)([0-9]{4})([0-9]{2})([0-9]{2})_([0-9]{2})([0-9]{2})([0-9]{2})\.', TAG_ORIGEN_CAMARA),  # Camara Samsung S20FE    
    (r'(VID|IMG)-([0-9]{4})([0-9]{2})([0-9]{2})-WA([0-9]{1})([0-9]{1})([0-9]{1})', TAG_ORIGEN_WAPP),  # Whatsapp
]

## REGEX patterns for filenames without datetime information
pattern_fn_nodtinfo_list = [
    (r'MVI_[0-9]{4}\.', TAG_ORIGEN_CAMARA), 
    (r'P1[0-9]{6}\.', TAG_ORIGEN_CAMARA), 
    (r'DSCN[0-9]{3}\.', TAG_ORIGEN_CAMARA), 
    (r'DSC_[0-9]{4}\.', TAG_ORIGEN_CAMARA), 
    (r'DSC[0-9]{5}\.', TAG_ORIGEN_CAMARA), 
    (r'Imagen [0-9]{3}\.', TAG_ORIGEN_CAMARA), 
    (r'IMG_[0-9]{4}\.', TAG_ORIGEN_CAMARA), 
    (r'IMG [0-9]{4}\.', TAG_ORIGEN_CAMARA), 
    (r'IMG[0-9]{4}\.', TAG_ORIGEN_CAMARA), 
    (r'MOV[0-9]{3}\.', TAG_ORIGEN_CAMARA)
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
        create_dt = os.path.getctime(path_to_file)
        modif_dt = os.path.getmtime(path_to_file)
        if create_dt < modif_dt : ret_dt = create_dt
        else: ret_dt = modif_dt
        return datetime.fromtimestamp(ret_dt)
    else:
        stat = os.stat(path_to_file)
        try:
            return datetime.fromtimestamp(stat.st_birthtime)
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            print("EXCEPTION Creation date analysis: " + path_to_file)
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
                if key in ExifTags.TAGS and CFG_EXIF_LOGS_SCREEN:
                    print(f'{ExifTags.TAGS[key]}:{val}')            
                if key == 0x0132 or key == 0x9003:   #DateTime or DateTimeOriginal
                    return (TAG_DT_ORIGIN_EXIF, datetime.strptime(val, '%Y:%m:%d %H:%M:%S'))
    except:
        print("EXCEPTION EXIF extraction failed: " + fn)
        pass    # Carry on checking other metadata extraction methode

    # If no EXIF: take the file date / time
    if CFG_EXIF_LOGS_SCREEN : print("No EXIF: " + fn)
    return (TAG_DT_ORIGIN_OS, os_creation_date(fn))

##
# Analizar que dispositivo tomo esta imagen
##
def get_fn_source(fn):

    # CHECK if Filename contains date time info:
    for pattern in pattern_fn_dtinfo_list:
        res=re.search(pattern[0], fn)
        if res:
            res_groups = res.groups(1)[1:]  # Remove firs element in tuple. contains discard info
            return create_fn_dt(res_groups), pattern[1]
        
    # Media files without datetime info in the file name.
    # Try to extract the datetime from the file itself (EXIF, OS datetime, other?)
    media_dt = read_fn_dt(fn)
    for pattern in pattern_fn_nodtinfo_list:
        res=re.search(pattern[0], fn)
        if res:
            return media_dt, pattern[1]

    # No info available leave default results
    return media_dt, TAG_ORIGEN_DESCONOCIDO

##
#
##
def get_list_image_hash_sz(user, tag_tipo, root_dir, lista_tipos):
    ret_list = []
    file_list = get_file_list(root_dir, lista_tipos)
    ctr_hash = 0
    ctr_hash_total = len(file_list)
    for filename in file_list:
        hash = calculate_hash(filename)
        size = os.path.getsize(filename)
        ret_list.append((filename, hash, size))
        if ctr_hash % 100 == 0:
            print("{0}:{1} Get Hash: {2}/{3}".format(user, tag_tipo, ctr_hash, ctr_hash_total))
        ctr_hash = ctr_hash + 1
    return ret_list
