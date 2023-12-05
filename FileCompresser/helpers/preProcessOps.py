def getDatabase():
    from pymongo import MongoClient
    from main import mongoDBURL
    import certifi
    connection_string = mongoDBURL
    connection = MongoClient(connection_string, tlsCAFile=certifi.where())
    database = connection['Cluster0']
    return database

def preProcessOps():
    import gridfs
    database = getDatabase()
    fs = gridfs.GridFS(database)
    for i in fs.find():
        fs.delete(i._id)
    return fs