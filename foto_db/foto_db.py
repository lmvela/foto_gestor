import ssl
from pymongo import DeleteOne, MongoClient
import sys
import pprint

##
# Conecta a DB y devuelve la coleccion
##
# En sistema windows conectar a DB de test (local)
if sys.platform.startswith('win'):
    client = MongoClient(port=27017)
# En sistema Linux conectar a la DB NAS
else:
    client=MongoClient("mongodb://mongodb:mongodb@localhost:27017/?authSource=admin&readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false")
db=client.clasificador_foto

##
#
##
def get_hash_repetidos_catalogo_db():
    pipeline = [
        {"$group": { "_id": "$hash", "count": {"$sum": 1}}},
        {"$match": { "count": {"$gt": 1}}}
    ]
    #pprint.pprint(list(db.lista_media.aggregate(pipeline)))
    return len(list(db.lista_media.aggregate(pipeline)))

def get_hash_repetidos_catalogo_por_user_db():
    pipeline = [      
        {"$group": { "_id": {"hash":"$hash", "user":"$user"}, "count": {"$sum": 1}}},
        {"$match": { "count": {"$gt": 1}}}
    ]
    pprint.pprint(list(db.lista_media.aggregate(pipeline)))
    return len(list(db.lista_media.aggregate(pipeline)))

def get_users_catalogo_db():
    return db.lista_media.distinct("user")

##
# Devuelva la lista de duplicados en el catalogo
##
def get_all_duplicados_db():
    return db.lista_duplicados.find();

##
#   Borrar un documento de la lista de duplicados
##
def del_dup_db(dup):
    return db.lista_duplicados.delete_one(dup)

##
#   Borrar un documento de la lista de revision
##
def del_revisar_db(dup):
    return db.lista_revision.delete_one(dup)

##
# Devuelva la lista de duplicados en el catalogo
##
def get_all_revision_db():
    return db.lista_revision.find();

##
#
##
def get_all_count_db():
    ctr =db.lista_media.count_documents({})
    ctr+=db.lista_borrar.count_documents({})
    ctr+=db.lista_duplicados.count_documents({})
    ctr+=db.lista_revision.count_documents({})
    return ctr

def get_media_count_db():
    return db.lista_media.count_documents({})

def get_duplicados_count_db():
    return db.lista_duplicados.count_documents({})

def get_revisar_count_db():
    return db.lista_revision.count_documents({})

def get_borrar_count_db():
    return db.lista_borrar.count_documents({})

def get_typeuser_count_db(user, tipo):
    ctr =db.lista_media.count_documents({'user': user, 'type': tipo})
    ctr+=db.lista_borrar.count_documents({'user': user, 'type': tipo})
    ctr+=db.lista_duplicados.count_documents({'user': user, 'type': tipo})
    ctr+=db.lista_revision.count_documents({'user': user, 'type': tipo})
    return ctr

def get_typeuser_media_count_db(user, tipo):
    return db.lista_media.count_documents({'user': user, 'type': tipo}) 

def get_typeuser_revisar_count_db(user, tipo):
    return db.lista_revision.count_documents({'user': user, 'type': tipo})    

def get_typeuser_borrar_count_db(user, tipo):
    return db.lista_borrar.count_documents({'user': user, 'type': tipo})

def get_typeuser_duplicados_count_db(user, tipo):
    return db.lista_duplicados.count_documents({'user': user, 'type': tipo})


def img_new_db(new_hash, user):
    return db.lista_media.find_one({'hash': new_hash, 'user': user})

def img_add_db(img_hash, user, tag_tipo):
    img_doc = {
        'filename' : img_hash[0],
        'hash' : img_hash[1],
        'size' : img_hash[2],
        'user' : user,
        'type' : tag_tipo
    }
    result=db.lista_media.insert_one(img_doc)
    print("Add new image {0} to db: {1}".format(str(img_doc), str(result.inserted_id)))

def img_borrar(img_filename, exists_img_Filename):
    ret=db.lista_borrar.find_one({'filename': img_filename})
    if ret is None:
        img_doc = {
            'filename' : img_filename,
        }    
        result=db.lista_borrar.insert_one(img_doc)
        print("Imagen {0} => Coleccion Borrar: {1}".format(str(img_doc), str(result.inserted_id)))
    else:
        print("Imagen ya esta en Coleccion Borrar: " + str(ret))

def img_replace_img_db(nuevo_filename, existing_img, user):
    if existing_img is None:
        print("ATENCION, no existe referencia para reemplazar con nuevo filename {0}".format(nuevo_filename))
    else:
        # Reemplazar con el nuevo nombre
        old_filename = existing_img['filename']
        existing_img['filename']=nuevo_filename       
        result = db.lista_media.update({'_id':existing_img['_id']}, {"$set": existing_img}, upsert=False)
        print("Reemplazado filename {0} con filename {1}: {2}".format(old_filename, nuevo_filename, str(result.inserted_id)))
        # Añadir nuevo nombre a duplicados
        img_duplicado_db(old_filename, existing_img)

def img_revision_db(nuevo_filename, existing_filename, user, tipo):
    ret=db.lista_revision.find_one({'filename_A': nuevo_filename, 'filename_B': existing_filename})
    if ret is None:
        rev_doc = {
            'filename_A' : nuevo_filename,
            'filename_B' : existing_filename,
            'user'       : user,
            'type'       : tipo
        }    
        result=db.lista_revision.insert_one(rev_doc)
        print("Imagenes {0} => Coleccion Revision: {1}".format(str(rev_doc), str(result.inserted_id)))
    else:
        print("Imagenes ya estan en Coleccion Revision: " + str(ret))    

def img_duplicado_db(nuevo_filename, existing_img, user, tipo):
    ret=db.lista_duplicados.find_one({'filename': nuevo_filename, 'reference': existing_img})
    if ret is None:
        rev_doc = {
            'filename' : nuevo_filename,
            'reference' : existing_img['filename'],
            'user'       : user,
            'type'       : tipo            
        }    
        result=db.lista_duplicados.insert_one(rev_doc)
        print("Imagen {0} => Coleccion Duplicados: {1}".format(str(rev_doc), str(result.inserted_id)))
    else:    
        print("Imagen duplicada ya esta en Coleccion Duplicados: {0}".format(str(ret)))

def img_existing_ok_db(exists_img):
    print("Imagen en BD => Actualizar contadores {0}".format(exists_img['filename']))
