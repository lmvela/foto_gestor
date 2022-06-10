import ntpath
import glob 
import os
import hashlib

ROOT_DIR = './foto_root'
USER_LIST = ['evd', 'lvg']

TIPOS_IMAGEN    = ['jpg', 'png']
TIPOS_VIDEO     = ['mpg']
TIPOS_AUDIO     = ['mp3']
LISTA_TIPOS     = [
    (TIPOS_IMAGEN, 'IMG'), 
    (TIPOS_VIDEO, 'VID'),
    (TIPOS_AUDIO, 'AUD')
]

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
