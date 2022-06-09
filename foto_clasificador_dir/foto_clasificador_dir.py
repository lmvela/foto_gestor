import hashlib
import glob, os

import sys
sys.path.append('./foto_db/')
from foto_db import * 

def get_image_list(root_dir):
    ret = []
    for filename in glob.iglob(root_dir + '/**/*.jpg', recursive=True):
        ret.append(filename)
    return ret

def calculate_hash(filename):
    ret = ""
    with open(filename,"rb") as f:
        bytes = f.read() 
        ret = hashlib.md5(bytes).hexdigest()
    return ret

def get_list_image_hash(root_dir):
    ret_list = []
    file_list = get_image_list(root_dir)
    for filename in file_list:
        hash = calculate_hash(filename)    
        ret_list.append((filename, hash))
    return ret_list

def main():

    # Show all extensions in dirtree
    exts = set(f.split('.')[-1] for dir,dirs,files in os.walk('.') for f in files if '.' in f) 
    print (str(exts))

    # Get list {file, hash}
    img_hash = get_list_image_hash(".")
    print(str(img_hash))

    # Update info in DB
    for img in img_hash:
        exists_img = img_new_db(img[1])
        if exists_img is None:
            img_add_db(img, "user")
        else:
            img_clear(img[0], exists_img)


if __name__ == "__main__":
    main()