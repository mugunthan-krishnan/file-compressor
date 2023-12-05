import os
from os.path import basename
from flask import Blueprint, render_template, request, send_file
from zipfile import ZipFile
import shutil
import lzma
import certifi
compress = Blueprint('compressfile', __name__)
import gridfs
# Global Variables
filestreams = []
filenames = []
inputFilesSize = {}
compressedzipfiles = './FileCompresser/static/compressedzipfiles'
compressedfiles = './FileCompresser/static/compressedfiles'

def getDatabase():
    from pymongo import MongoClient
    connection_string = 'mongodb+srv://mk2246:Vidyakrishaksh1991@cluster0.edgcizs.mongodb.net/?retryWrites=true&w=majority'
    connection = MongoClient(connection_string, tlsCAFile=certifi.where())
    #database = connection['cs632101f23_026']
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
        # shutil.rmtree(compressedzipfiles, ignore_errors=True)
        # os.mkdir(compressedzipfiles)
        # shutil.rmtree(compressedfiles, ignore_errors=True)
        # os.mkdir(compressedfiles)
    
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
        keys = []
        contents=[]
        # Compress the uploaded files when compress button is clicked.
        if request.form.get("compress"):
            compressor = lzma.LZMACompressor()
            for f in range(0, len(filestreams)):
                compressed_data = compressor.compress(filestreams[f])
                key = fs.put(compressed_data, filename=filenames[f])
                keys.append(key)
                contents.append(fs.get(key).read())
            #createLogFile(filenames, inputFilesSize)
            enabledwnld = True

        # Download the compressed files as a zip file when download file button is clicked.
        if request.form.get("download"):
            # with ZipFile('compressed.zip', 'w') as zipObj:
            #     # Add multiple files to the zip
            #     for f in fs.find(no_cursor_timeout=True):
            #         toBeZippedFileName = f
            #         zipObj.write(toBeZippedFileName, basename(toBeZippedFileName))
            enabledwnld = False
            #filenames.clear()
            filestreams.clear()
            file_path = os.path.join('/tmp', filenames[0])
            with open(file_path, 'w') as f:
                f.write(contents[0])
            return send_file(file_path, as_attachment=True, download_name=f.name)
            # if os.path.isfile(compressedzipfiles+'/compressed.zip'):
            #     downloadFilePath = compressedzipfiles+'/compressed.zip'
            # for f in fs.find({"filename":filenames[0]},no_cursor_timeout=True):
            #     downloadFilePath = f.read()
            #     print(downloadFilePath)
            #     return send_file(downloadFilePath, as_attachment=True, download_name=f.name)

        # Download the log file as a txt file when download log file button is clicked.
        if request.form.get('downloadlogfile'):
            return send_file('./FileCompresser/static/logfile.txt', as_attachment=True, download_name='logfile.txt')

    return render_template('compress.html', enabledwnld=enabledwnld, filenames=filenames)

# Log File Data
def createLogFile(filenames, inputFilesSize):
    logString = 'FILENAME' + '\t\t\t' + 'COMPRESSION RATIO' + '\n'
    for f in filenames:
        original_size = inputFilesSize[f]
        compressed_size = os.path.getsize(compressedfiles+'/'+f)
        compression_ratio = original_size / compressed_size
        logString = logString + f + '\t\t\t' + str(compression_ratio) + '\n'
    with open('./static/logfile.txt', 'w') as lf:
        lf.write(logString)