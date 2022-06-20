import ntpath
import glob 
import os
import hashlib
import sys
import shutil
import re

if sys.platform.startswith('win'):
    sys.path.append("C:\\work\\02_Pers\\proyectos\\foto_gestor")
else:
    sys.path.append("/home/luis/Documentos/02_projects/fotogest/foto_gestor")
from foto_db.foto_db import *

##
#   CFG Directorios raiz
##
if sys.platform.startswith('win'):
    ROOT_DIR = 'C:\\work\\02_Pers\\proyectos\\foto_gestor\\foto_root'
    ROOT_DIR_DEMO = 'C:\\work\\02_Pers\\proyectos\\foto_gestor\\foto_root_demo'
else:
    ROOT_DIR = '/media/cavehost_hdd/00_fotos'
    ROOT_DIR_DEMO = '/media/cavehost_hdd/00_fotos'

CATALOGO_ROOT_DIR = os.path.join(ROOT_DIR, 'catalogo')
DESCARTAR_ROOT_DIR = os.path.join(ROOT_DIR, 'descartar')
PAPELERA_DIR = os.path.join(ROOT_DIR, 'papelera')


##
# Lista de Usuarios
##
USER_LIST = ['evd', 'fvd', 'fvg', 'lvg']

##
#   Tipos de medios aceptados en el catalogo
##
if sys.platform.startswith('win'):
    TIPOS_IMAGEN = ['bmp', 'jpg', 'png', 'mov', 'gif', 'tif', 'enc', 'mpo', 'nef', 'cr2', 'arw', 'webp', 'xcf']
    TIPOS_VIDEO = ['mov', '3gp', 'wmv', 'm4v', 'mp4', 'mpg', 'avi']
    TIPOS_AUDIO = ['gp3', 'mp3', 'wav', 'm4a', '3ga']
    TIPOS_MINIATURAS = ['thm'] 
else:
    TIPOS_IMAGEN = ['bmp', 'jpg', 'png', 'MOV', 'JPG', 'gif', 'tif', 'enc', 'mpo', 'NEF', 'cr2', 'CR2', 'ARW', 'webp', 'xcf']
    TIPOS_VIDEO = ['MP4', 'mov', 'AVI', 'MPG', '3gp', 'wmv', 'm4v', 'mp4', 'mpg', 'avi']
    TIPOS_AUDIO = ['gp3', 'mp3', 'wav', 'm4a', '3ga']
    TIPOS_MINIATURAS = ['THM'] 

LISTA_TIPOS_CATALOGO = [
    (TIPOS_IMAGEN, 'IMG'), 
    (TIPOS_VIDEO, 'VID'),
    (TIPOS_AUDIO, 'AUD'),
    (TIPOS_MINIATURAS, 'MIN')
]

##
#   Tipos de ficheros a descartar
##
TIPOS_PRESENTACIONES = ['psh', 'pxc', 'ppt', 'pps'] 
TIPOS_BACKUP_DATOS = ['enml', 'pub', 'txt']
TIPOS_BACKUP_MEDIA = ['jpg_old', 'JPG_old', 'mp4_old', 'zip', 'jpeg_old']
TIPOS_LIMPIAR = ['html', 'ini', 'lnk']

LISTA_TIPOS_DESCARTAR = [
    (TIPOS_PRESENTACIONES, 'PRS', 'presentaciones'),
    (TIPOS_BACKUP_DATOS, 'DAT', 'backup_datos'),
    (TIPOS_BACKUP_MEDIA, 'BMD', 'backup_media'),
    (TIPOS_LIMPIAR, 'LIM', 'papelera'),
]

##
#   Tokens en los nombres de los ficheros
##
BACKUP_FILES_TOKENS = ['(', ')', 'backup', 'copy', 'copia', '~']
BACKUP_FOLDER_TOKENS = ['backup', 'copy', 'copia']

##
#   Funciones communes
##

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
    shutil.copy(src_fpath, dest_fpath)

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
    for tipo in lista_tipos:
        for filename in glob.iglob(root_dir + '/**/*.' + tipo, recursive=True):
            ret.append(os.path.normpath(filename))
            if max_len>0 and len(ret)>max_len:
                break
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
        return 0
    return total
