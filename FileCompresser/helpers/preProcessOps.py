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

def empty_tmp_folder():
    import os
    import shutil
    tmp_folder = '/tmp'

    # Iterate over files in /tmp and remove them
    for filename in os.listdir(tmp_folder):
        file_path = os.path.join(tmp_folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Error while deleting {file_path}: {e}")

def preProcessOps():
    import gridfs

    database = getDatabase()
    fs = gridfs.GridFS(database)
    for i in fs.find():
        fs.delete(i._id)
    return fs