import ntpath
import glob 
import os
import hashlib

##
#   CFG Directorios raiz
##
ROOT_DIR = '/media/cavehost_hdd/00_fotos/catalogo'
DESCARTAR_ROOT_DIR = '/media/cavehost_hdd/00_fotos/descartar'
USER_LIST = ['evd', 'fvd', 'fvg', 'lvg']

##
#   Tipos de medios aceptados en el catalogo
##
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
#   Funciones communes
##
def crea_carpeta(path):
    if not os.path.exists(path):
        os.makedirs(path)

def nombre_fichero(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def get_total_file_list(root_dir):
    total = 0
    for root, dirs, files in os.walk(root_dir):
        total += len(files)
    return total

def get_file_list(root_dir, lista_tipos):
    ret = []
    for tipo in lista_tipos:
        for filename in glob.iglob(root_dir + '/**/*.' + tipo, recursive=True):
            ret.append(os.path.normpath(filename))
    return ret

def proc_list_ficheros(file_list):
    size = 0
    for el in file_list:
        size += os.path.getsize(el)
    return len(file_list), size

def calculate_hash(filename):
    ret = ""
    with open(filename,"rb") as f:
        bytes = f.read() 
        ret = hashlib.md5(bytes).hexdigest()
    return ret

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
