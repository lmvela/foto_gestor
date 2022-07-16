import ntpath
import os
import hashlib
import sys
import shutil
import re

if sys.platform.startswith('win'):
    sys.path.append("C:\\work\\02_Pers\\proyectos\\foto_gestor")
else:
    sys.path.append("/home/luis/Documentos/02_projects/fotogest/foto_gestor")
from foto_comun.foto_cfg import *
from foto_db.foto_db import *

##
# Backup token list
##
BACKUP_TOKEN_LIST = ['backup', 'Backup', 'copia']

##
#   CFG Directorios raiz
##
if sys.platform.startswith('win'):
    BASE_DIR = 'C:\\work\\02_Pers\\proyectos\\foto_gestor'
else:
    BASE_DIR = '/media/cavehost_hdd'

if CFG_DEVEL_MODE is True:
    FOTO_GEST_ROOT_DIR = os.path.join(BASE_DIR, '00_fotos_devel') 
    FOTO_GEST_CATALGO_ORIGINAL= os.path.join(os.path.join(BASE_DIR, '00_fotos'), 'catalogo') 
else:
    FOTO_GEST_ROOT_DIR = os.path.join(BASE_DIR, '00_fotos') 

EVENTOS_DIR = 'Eventos'
FECHAS_DIR = 'Fechas'
CATALOGO_ROOT_DIR = os.path.join(FOTO_GEST_ROOT_DIR, 'catalogo')
DESCARTAR_ROOT_DIR = os.path.join(FOTO_GEST_ROOT_DIR, 'descartar')
PAPELERA_DIR = os.path.join(FOTO_GEST_ROOT_DIR, 'papelera')
IMPORTAR_NUEVOS_DIR = os.path.join(FOTO_GEST_ROOT_DIR, 'importar')
RECHAZADOS_NUEVOS_DIR = os.path.join(FOTO_GEST_ROOT_DIR, 'rechazados')
CUARENTENA_NUEVOS_DIR = os.path.join(FOTO_GEST_ROOT_DIR, 'cuarentena')

##
# Tags dispositivo origen de la imagen
##
TAG_ORIGEN_CAMARA = "CAMARA"
TAG_ORIGEN_WAPP = "WAPP"
TAG_ORIGEN_DESCONOCIDO = "DESCONOCIDO"

##
# Lista de Usuarios
##
USER_LIST = ['evd', 'fvd', 'fvg', 'lvg']

##
#   Tipos de medios aceptados en el catalogo
#   {'THM', 'wav', 'jpg', 'MPG', 'rar', 'png', '3gp', 'zip', 'mpo', '3ga', 'gif', 'ARW', 'mpg', 'MOV', 'enc', 'xcf', 'm4v', 'MP4', 'wmv', 'NEF', 'db', 'JPG', 'avi', 'tif', 'mp3', 'AVI', 'bmp', 'm4a', 'webp', 'PDF', 'cr2', 'mov', 'mp4', 'jpeg', 'CR2'}
##
if sys.platform.startswith('win'):
    TIPOS_IMAGEN = ['bmp', 'jpg', 'png', 'mov', 'gif', 'tif', 'enc', 'mpo', 'nef', 'cr2', 'arw', 'webp', 'xcf', 'jpeg']
    TIPOS_VIDEO = ['mov', '3gp', 'wmv', 'm4v', 'mp4', 'mpg', 'avi']
    TIPOS_AUDIO = ['gp3', 'mp3', 'wav', 'm4a', '3ga']
    TIPOS_MINIATURAS = ['thm'] 
else:
    TIPOS_IMAGEN = ['bmp', 'jpg', 'png', 'MOV', 'JPG', 'gif', 'tif', 'enc', 'mpo', 'NEF', 'cr2', 'CR2', 'ARW', 'webp', 'xcf', 'jpeg']
    TIPOS_VIDEO = ['MP4', 'mov', 'AVI', 'MPG', '3gp', 'wmv', 'm4v', 'mp4', 'mpg', 'avi']
    TIPOS_AUDIO = ['gp3', 'mp3', 'wav', 'm4a', '3ga']
    TIPOS_MINIATURAS = ['THM'] 

TAG_TIPO_IMAGEN = 'IMG'
TAG_TIPO_VIDEO = 'VID'
TAG_TIPO_AUDIO = 'AUD'
TAG_TIPO_MINIATURAS = 'MIN'
TAG_TIPO_DESCARTAR = 'DESC'

LISTA_TIPOS_CATALOGO = [
    (TIPOS_IMAGEN, TAG_TIPO_IMAGEN), 
    (TIPOS_VIDEO, TAG_TIPO_VIDEO),
    (TIPOS_AUDIO, TAG_TIPO_AUDIO),
    (TIPOS_MINIATURAS, TAG_TIPO_MINIATURAS)
]

##
#   Tipos de ficheros a descartar
##
TIPOS_PRESENTACIONES = ['psh', 'pxc', 'ppt', 'pps', 'pdf', 'PDF'] 
TIPOS_BACKUP_DATOS = ['enml', 'pub', 'txt']
TIPOS_BACKUP_MEDIA = ['jpg_old', 'JPG_old', 'mp4_old', 'zip', 'jpeg_old', 'rar']
TIPOS_LIMPIAR = ['html', 'ini', 'lnk', 'db']

TAG_TIPO_PRESENTACIONES = 'PRES' 
TAG_TIPO_BACKUP_DATOS = 'DATA'
TAG_TIPO_BACKUP_MEDIA = 'BMEDIA'
TAG_TIPO_LIMPIAR = 'DESC'

LISTA_TIPOS_DESCARTAR = [
    (TIPOS_PRESENTACIONES, TAG_TIPO_PRESENTACIONES),
    (TIPOS_BACKUP_DATOS, TAG_TIPO_BACKUP_DATOS),
    (TIPOS_BACKUP_MEDIA, TAG_TIPO_BACKUP_MEDIA),
    (TIPOS_LIMPIAR, TAG_TIPO_LIMPIAR),
]

##
#   Tokens en los nombres de los ficheros
##
BACKUP_FILES_TOKENS = ['(', ')', 'backup', 'copy', 'copia', '~']
BACKUP_FOLDER_TOKENS = ['backup', 'copy', 'copia']

##
# OP CODE Enum
##
KEEP_RIGHT = 1
KEEP_LEFT = 2
KEEP_BOTH = 3
KEEP_NONE = 4
CLOSE_REVISION = 5
CLOSED_WINDOW = 6
REVISION_FINISHED_OK = 7
SKIP_REVISION = 8

##
# ORIGEN del datetime
##
TAG_DT_ORIGIN_EXIF = 'exif'
TAG_DT_ORIGIN_FN = 'filename'
TAG_DT_ORIGIN_OS = 'os'
TAG_DT_ORIGIN_UNKNOWN = 'unknown'

##
#   Funciones communes
##
if sys.platform.startswith('win'):
    VALID_KEY_REVISOR_MANUAL = {2555904:KEEP_RIGHT, 2424832:KEEP_LEFT, 2490368:KEEP_BOTH, 2621440:KEEP_NONE, 99:CLOSE_REVISION, 27:CLOSE_REVISION, -1:CLOSED_WINDOW}
else:
    VALID_KEY_REVISOR_MANUAL = {65363:KEEP_RIGHT, 65361:KEEP_LEFT, 65362:KEEP_BOTH, 65364:KEEP_NONE, 99:CLOSE_REVISION, 27:CLOSE_REVISION, -1:CLOSED_WINDOW}

##
#
##
def interpreta_op_code_plataforma(op_code):
    return VALID_KEY_REVISOR_MANUAL[op_code]
##
#
##
def print_ext_summary(dir_to_analyze):
    # Show all extensions in dirtree
    exts = set(f.split('.')[-1] for dir,dirs,files in os.walk(dir_to_analyze) for f in files if '.' in f) 
    print (str(exts))

##
#
##
def is_file_whatsapp(fname):
    pattern = re.compile("(AUD|VID|IMG)-[0-9]{8}-WA[0-9]{4}\.[a-z].*")
    return pattern.match(fname)

##
#
##
def copia_file_crea_dirs(src_fpath, dest_fpath):
    os.makedirs(os.path.dirname(dest_fpath), exist_ok=True)
    print("Copy: " + src_fpath + " -> " + dest_fpath)
    shutil.copy2(src_fpath, dest_fpath)

def mueve_file_con_fecha_crea_dirs(src_fpath, dest_fpath):
    os.makedirs(os.path.dirname(dest_fpath), exist_ok=True)
    print("Copy: " + src_fpath + " -> " + dest_fpath)
    shutil.move(src_fpath, dest_fpath)


##
#
##
def crea_carpeta(path):
    if not os.path.exists(path):
        os.makedirs(path)

##
#
##
def nombre_fichero(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def nombre_fichero_lower(path):
    return nombre_fichero(path).lower()

def extension_fichero(path):
    filename, file_extension = os.path.splitext(path)
    return file_extension
    
##
#
##
def nombre_carpeta(path):
    head, tail = ntpath.split(path)
    return ntpath.basename(head)

def nombre_carpeta_lower(path):
    return nombre_carpeta(path).lower()    

##
#
##
def get_total_file_list(root_dir):
    total = 0
    for root, dirs, files in os.walk(root_dir):
        total += len(files)
    return total

##
#
##
def get_file_list(root_dir, lista_tipos, max_len=-1):
    ret = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            ext_fn = extension_fichero(file).replace('.', '')
            if ext_fn in lista_tipos:
                ret.append(os.path.normpath(os.path.join(root, file)))
                if max_len>0 and len(ret)>=max_len:                
                    return ret
    return ret

##
#
##
def get_file_lists(root_dir, listas_tipos, max_len=-1):
    ret = []
    for lista_tipos, tag in listas_tipos:
        for root, dirs, files in os.walk(root_dir):
            for file in files:
                ext_fn = extension_fichero(file).replace('.', '')
                if ext_fn in lista_tipos:
                    ret.append(os.path.normpath(os.path.join(root, file)))
                    if max_len>0 and len(ret)>max_len:                
                        return ret
    return ret

##
#
##
def proc_list_ficheros(file_list):
    size = 0
    for el in file_list:
        size += os.path.getsize(el)
    return len(file_list), size

##
#
##
def calculate_hash(filename):
    ret = ""
    with open(filename,"rb") as f:
        bytes = f.read() 
        ret = hashlib.md5(bytes).hexdigest()
    return ret

##
#
##
def get_directory_size(directory):
    """Returns the `directory` size in bytes."""
    total = 0
    try:
        # print("[+] Getting the size of", directory)
        for entry in os.scandir(directory):
            if entry.is_file():
                # if it's a file, use stat() function
                total += entry.stat().st_size
            elif entry.is_dir():
                # if it's a directory, recursively call this function
                try:
                    total += get_directory_size(entry.path)
                except FileNotFoundError:
                    pass
    except NotADirectoryError:
        # if `directory` isn't a directory, get the file size then
        return os.path.getsize(directory)
    except PermissionError:
        # if for whatever reason we can't open the folder, return 0
        print("EXCEPTION PermissionError Dir size: " + directory)
        return 0
    return total
