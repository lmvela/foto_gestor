import ssl
from pymongo import DeleteOne, MongoClient
import sys
import pprint
from bson.objectid import ObjectId
from datetime import datetime
import os

if sys.platform.startswith('win'):
    sys.path.append("C:\\work\\02_Pers\\proyectos\\foto_gestor")
else:
    sys.path.append("/home/luis/Documentos/02_projects/fotogest/foto_gestor")
from foto_comun.foto_cfg import *

##
# Conecta a DB y devuelve la coleccion
##
# En sistema windows conectar a DB de test (local)
if sys.platform.startswith('win'):
    client = MongoClient(port=27017)
# En sistema Linux conectar a la DB NAS
else:
    client=MongoClient("mongodb://mongodb:mongodb@localhost:27017/?authSource=admin&readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false")

##
# Usar DB de produccion o de desarrollo
##
if CFG_DEVEL_MODE is True:
    db=client.clasificador_foto_devel 
else:
    db=client.clasificador_foto


###################################################################################################################
# ADD methods
##

##
# Añade una estadistica nueva
##
def add_stats_db(stats):
    result=db.lista_estadisticas.insert_one(stats)
    print("DB-ADDED new stats {0} to db: {1}".format(str(stats), str(result.inserted_id)))    

##
# Añade una imagen nueva al catalogo
##
def add_img_catalogo_db(img_hash, user, tag_tipo, media_origen, media_dt):
    filename, file_extension = os.path.splitext(img_hash[0])
    img_doc = {
        'filename' : img_hash[0],
        'extension' : file_extension,
        'hash' : img_hash[1],
        'size' : img_hash[2],
        'user' : user,
        'type' : tag_tipo,
        'source' : media_origen,
        'datetime' : media_dt[1],
        'datetime_origen' : media_dt[0],
        'clasif_datetime' : datetime.now() 
    }
    result=db.lista_media.insert_one(img_doc)
    print("DB-ADDED new image {0} to db: {1}".format(str(img_doc), str(result.inserted_id)))

##
# Añade una imagne a la coll borrar
##
def add_img_borrar_db(img_filename):
    ret=db.lista_borrar.find_one({'filename': img_filename})
    if ret is None:
        img_doc = {
            'filename' : img_filename,
        }    
        result=db.lista_borrar.insert_one(img_doc)
        print("Imagen {0} => Coleccion Borrar: {1}".format(str(img_doc), str(result.inserted_id)))
    else:
        print("Imagen ya esta en Coleccion Borrar: " + str(ret))

##
#   Añade una imagen para revision.
#   Check si ya tenemos un doc => push a la lista de filenames
#   Sino crea un doc inicial
##
def add_img_revision_db(fn_hash_sz, existing_filename, user, tipo):
    ret=db.lista_revision.find_one({'hash': fn_hash_sz[1]})
    if ret is None:
        rev_doc = {
            'filenames'  : [fn_hash_sz[0]],
            'reference'  : existing_filename,
            'hash'       : fn_hash_sz[1],
            'user'       : user,
            'type'       : tipo,
            'size'       : fn_hash_sz[2]
        }    
        result=db.lista_revision.insert_one(rev_doc)
        print("ADDED Imagenes {0} => Coleccion Revision: {1}".format(str(rev_doc), str(result.inserted_id)))
    elif fn_hash_sz[0] not in ret['filenames']:
        result=db.lista_revision.update_one({'hash': fn_hash_sz[1]}, {'$push': {'filenames': fn_hash_sz[0]}})
        print("UPDATED Imagenes {0} => Coleccion Revision: {1}".format(str(ret), str(result.acknowledged)))
    else:
        print("Imagen para revisar ya estan en Coleccion Revision: " + str(ret))    

##
#   Añade una imagen a duplicados.
#   Check si ya tenemos un doc => push a la lista de filenames
#   Sino crea un doc inicial
##
def add_img_duplicado_db(fn_hash_sz, existing_img, user, tipo):
    ret=db.lista_duplicados.find_one({'hash': fn_hash_sz[1]})
    if ret is None:
        rev_doc = {
            'filenames'  : [fn_hash_sz[0]],
            'reference'  : existing_img['filename'],
            'hash'       : fn_hash_sz[1],
            'user'       : user,
            'type'       : tipo,
            'size'       : fn_hash_sz[2]            
        }    
        result=db.lista_duplicados.insert_one(rev_doc)
        print("ADDED Imagen {0} => Coleccion Duplicados: {1}".format(str(rev_doc), str(result.inserted_id)))
    elif fn_hash_sz[0] not in ret['filenames']:
        result=db.lista_duplicados.update_one({'hash': fn_hash_sz[1]}, {'$push': {'filenames': fn_hash_sz[0]}})
        print("UPDATED Imagen {0} => Coleccion Duplicados: {1}".format(str(ret), str(result.acknowledged)))
    else:    
        print("Imagen duplicada ya esta en Coleccion Duplicados: {0}".format(str(ret)))


###################################################################################################################
# SIZE CALCULATIONS methods
##
def get_size_media_db():
    pipeline = [
        { "$match": {} }, 
        { "$group": { "_id": None, "sum": {"$sum": "$size"}}}
    ]

    results = db.lista_media.aggregate(pipeline)
    try:
        record = results.next()
    except StopIteration:
        print("get_size_media_db: empty cursor")

    #pprint.pprint(record['sum'])
    return record['sum']

def get_size_rev_db():
    pipeline = [
        { "$match": {} }, 
        { "$group": { "_id": None, "sum": {"$sum": "$size"}}}
    ]

    results = db.lista_revision.aggregate(pipeline)
    try:
        record = results.next()
    except StopIteration:
        print("get_size_media_db: empty cursor")

    #pprint.pprint(record['sum'])
    return record['sum']

def get_size_dup_db():
    pipeline = [
        { "$match": {} }, 
        { "$group": { "_id": None, "sum": {"$sum": "$size"}}}
    ]

    results = db.lista_duplicados.aggregate(pipeline)
    try:
        record = results.next()
        pprint.pprint(record['sum'])
        return record['sum']
    except StopIteration:
        print("get_size_media_db: empty cursor")
        return 0

###################################################################################################################
# COUNT methods
##
def count_all_docs_db():
    ctr =db.lista_media.count_documents({})
    ctr+=db.lista_borrar.count_documents({})
    ctr+=db.lista_duplicados.count_documents({})
    ctr+=db.lista_revision.count_documents({})
    return ctr

def count_media_docs_db():
    return db.lista_media.count_documents({})

def count_duplicados_docs_db():
    return db.lista_duplicados.count_documents({})

def count_revisar_docs_db():
    return db.lista_revision.count_documents({})

def count_borrar_docs_db():
    return db.lista_borrar.count_documents({})

def count_typeuser_docs_db(user, tipo):
    ctr =db.lista_media.count_documents({'user': user, 'type': tipo})
    ctr+=db.lista_borrar.count_documents({'user': user, 'type': tipo})
    ctr+=db.lista_duplicados.count_documents({'user': user, 'type': tipo})
    ctr+=db.lista_revision.count_documents({'user': user, 'type': tipo})
    return ctr

def count_typeuser_media_docs_db(user, tipo):
    return db.lista_media.count_documents({'user': user, 'type': tipo}) 

def count_typeuser_revisar_docs_db(user, tipo):
    return db.lista_revision.count_documents({'user': user, 'type': tipo})    

def count_typeuser_borrar_docs_db(user, tipo):
    return db.lista_borrar.count_documents({'user': user, 'type': tipo})

def count_typeuser_duplicados_docs_db(user, tipo):
    return db.lista_duplicados.count_documents({'user': user, 'type': tipo})

def count_hash_repetidos_catalogo_db():
    pipeline = [
        {"$group": { "_id": "$hash", "count": {"$sum": 1}}},
        {"$match": { "count": {"$gt": 1}}}
    ]
    #pprint.pprint(list(db.lista_media.aggregate(pipeline)))
    return len(list(db.lista_media.aggregate(pipeline)))

def count_hash_repetidos_catalogo_por_user_db():
    pipeline = [      
        {"$group": { "_id": {"hash":"$hash", "user":"$user"}, "count": {"$sum": 1}}},
        {"$match": { "count": {"$gt": 1}}}
    ]
    #pprint.pprint(list(db.lista_media.aggregate(pipeline)))
    return len(list(db.lista_media.aggregate(pipeline)))

###################################################################################################################
# GET methods
##

##
#   Devuelve la lista de users en el catalogo
##
def get_users_catalogo_db():
    return db.lista_media.distinct("user")

##
# Devuelva la lista de duplicados en el catalogo
##
def get_all_duplicados_db():
    return db.lista_duplicados.find();

##
# Devuelva la lista de revision en el catalogo
##
def get_all_revision_db():
    return db.lista_revision.find();

##
# Devuelve la lista de duplicados para un user en concreto
##
def get_dups_user_db(user):
    return db.lista_duplicados.find({ "user": { "$eq": user }})

##
# Devuelve la lista de duplicados para un user y un tipo de datos en concreto
##
def get_dups_user_type_db(user, type):
    return db.lista_duplicados.find({ "user": { "$eq": user }, "type": { "$eq": type }})

##
# Devuelve un doc con un hash y un user determinado
##
def get_media_hash_user_db(hash, user):
    return db.lista_media.find_one({'hash': hash, 'user': user})

##
# Devuelve un doc con un hash y un filename determinado
##
def get_media_hash_filename_db(hash, filename):
    return db.lista_media.find_one({'hash': hash, 'filename': filename})

###################################################################################################################
# DEL methods
##

##
#   Borrar un documento del catalogo. Basado en su hash y filename
##
def del_media_hash_filename_db(hash, filename):
    media_doc = db.lista_media.find_one({'hash': hash, 'filename': filename})
    if media_doc is None:
        print("DELETE ERROR: Borrando un media doc inexistente en BD:{0} {1} ".format(filename, hash))
    else:
        add_img_borrar_db(filename)
        db.lista_media.delete_one(media_doc)
        print("DELETE: Borrado un media doc:{0} {1} ".format(filename, hash))

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

###################################################################################################################
# UPDATE methods
##

##
#   Dado un filename / hash de un doc en el media, actualiza el filename
##
def update_img_filename_db(nuevo_filename, old_filename, hash):
    existing_img = get_media_hash_filename_db(hash, old_filename)
    if existing_img is None:
        print("ATENCION, no existe referencia para reemplazar con nuevo filename {0}".format(nuevo_filename))
    else:
        # Reemplazar con el nuevo nombre
        existing_img['filename']=nuevo_filename       
        result=db.lista_media.update_one({'_id':existing_img['_id']}, {"$set": existing_img}, upsert=False)
        print("Reemplazado filename {0} con filename {1}: {2}".format(old_filename, nuevo_filename, str(result.upserted_id)))

##
#  Actualizamos informacion duplicado
##
def update_dup_db(dup):
    result=db.lista_duplicados.delete_one({'_id': dup['_id']})
    print("UPDATE delete Duplicado: {0}".format(str(result.deleted_count)))
    rev_doc = {
            'filenames'  : dup['filenames'],
            'reference'  : dup['reference'],
            'hash'       : dup['hash'],
            'user'       : dup['user'],
            'type'       : dup['type'],           
    }    
    result=db.lista_duplicados.insert_one(rev_doc)
    print("UPDATE insert Duplicado: {0}".format(str(result.inserted_id)))


###################################################################################################################
# MISC methods
##
def img_existing_ok_db(exists_img):
    print("Imagen en BD => Actualizar contadores {0}".format(exists_img['filename']))
