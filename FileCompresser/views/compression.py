import os
from flask import Blueprint, render_template, request, send_file
from zipfile import ZipFile
import lzma
import certifi
import gridfs

compress = Blueprint('compressfile', __name__)
# Global Variables
filestreams = []
filenames = []
inputFilesSize = {}
keys = []
contents=[]

def getDatabase():
    from pymongo import MongoClient
    connection_string = 'mongodb+srv://mk2246:Vidyakrishaksh1991@cluster0.edgcizs.mongodb.net/?retryWrites=true&w=majority'
    connection = MongoClient(connection_string, tlsCAFile=certifi.where())
    database = connection['Cluster0']
    return database

database = getDatabase()
fs = gridfs.GridFS(database)

for i in fs.find():
    print(i._id)
    fs.delete(i._id)

@compress.route('/compress', methods=['GET','POST'])
def compressPage():
    enabledwnld = False
    # Clear filenames, filestreams and associated folders fpr every run.
    if request.method == "GET":
        filestreams.clear()
        filenames.clear()
        inputFilesSize.clear()
    
    if request.method == "POST":
        # Upload a file and its metadata.
        if request.form.get("upload"):
            input_file = request.files['file']
            if input_file.filename and input_file.filename not in filenames:
                data = input_file.stream.read()
                filestreams.append(data)
                filenames.append(input_file.filename)
                inputFileSize = {input_file.filename:len(data)}
                inputFilesSize.update(inputFileSize)

        # Compress the uploaded files when compress button is clicked.
        if request.form.get("compress"):
            compressor = lzma.LZMACompressor()
            for f in range(0, len(filestreams)):
                compressed_data = compressor.compress(filestreams[f])
                key = fs.put(compressed_data, filename=filenames[f])
                keys.append(key)
                contents.append(fs.get(key).read())
            
            # Create the files in the tmp directory in Heroku Ephemeral Filesystem
            for i in range(len(filenames)):
                file_path = '/tmp/' + filenames[i]
                with open(file_path, 'wb') as f:
                    f.write(contents[i])
            createLogFile(filenames, inputFilesSize)
            enabledwnld = True

        # Download the compressed files as a zip file when download file button is clicked.
        if request.form.get("download"):
            enabledwnld = False
            filestreams.clear()
            zipfilePath = '/tmp/compressed.zip'
            with ZipFile(zipfilePath, 'w') as zipObj:
                # Add multiple files to the zip
                for f in filenames:
                    toBeZippedFileName = '/tmp/' + f
                    zipObj.write(toBeZippedFileName, os.path.basename(toBeZippedFileName))
            filenames.clear()
            return send_file(zipfilePath, as_attachment=True, download_name='compressed.zip')
        # Download the log file as a txt file when download log file button is clicked.
        if request.form.get('downloadlogfile'):
            return send_file('/tmp/logfile.txt', as_attachment=True, download_name='logfile.txt')

    return render_template('compress.html', enabledwnld=enabledwnld, filenames=filenames)

# Log File Data
def createLogFile(filenames, inputFilesSize):
    logString = 'FILENAME' + '\t\t\t' + 'COMPRESSION RATIO' + '\n'
    for f in filenames:
        original_size = inputFilesSize[f]
        compressed_size = os.path.getsize('/tmp'+'/'+f)
        #compressed_size = 1
        compression_ratio = original_size / compressed_size
        logString = logString + f + '\t\t\t' + str(compression_ratio) + '\n'
    with open('/tmp/logfile.txt', 'w') as lf:
        lf.write(logString)