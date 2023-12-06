"""
    Purpose:    The purpose of this script is to get mongo database connection
                and clear the grid file system collection of previous files.
"""

def getDatabase():
    from pymongo import MongoClient
    from main import mongoDBURL
    import certifi
    connection = MongoClient(mongoDBURL, tlsCAFile=certifi.where())
    database = connection['Cluster0']
    return database

def preProcessOps():
    import gridfs
    database = getDatabase()
    fs = gridfs.GridFS(database)
    for i in fs.find():
        fs.delete(i._id)
    return fs