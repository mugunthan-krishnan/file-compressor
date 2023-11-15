import os
from os.path import basename
from flask import Blueprint, render_template, request, send_file
from zipfile import ZipFile
import shutil
import lzma
compress = Blueprint('compressfile', __name__)

# Global Variables
filestreams = []
filenames = []
inputFilesSize = {}
compressedzipfiles = './FileCompresser/static/compressedzipfiles'
compressedfiles = './FileCompresser/static/compressedfiles'

@compress.route('/compress', methods=['GET','POST'])
def compressPage():
    enabledwnld = False
    # Clear filenames, filestreams and associated folders fpr every run.
    if request.method == "GET":
        filestreams.clear()
        filenames.clear()
        inputFilesSize.clear()
        shutil.rmtree(compressedzipfiles, ignore_errors=True)
        os.mkdir(compressedzipfiles)
        shutil.rmtree(compressedfiles, ignore_errors=True)
        os.mkdir(compressedfiles)
    
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
                output_file = compressedfiles+'/'+filenames[f]
                with open(output_file, 'wb') as fo:
                    fo.write(compressed_data)
            createLogFile(filenames, inputFilesSize)
            enabledwnld = True

        # Download the compressed files as a zip file when download file button is clicked.
        if request.form.get("download"):
            with ZipFile(compressedzipfiles+'/compressed.zip', 'w') as zipObj:
                # Add multiple files to the zip
                for f in filenames:
                    toBeZippedFileName = compressedfiles+'/'+ f
                    zipObj.write(toBeZippedFileName, basename(toBeZippedFileName))
            enabledwnld = False
            filenames.clear()
            filestreams.clear()
            if os.path.isfile(compressedzipfiles+'/compressed.zip'):
                downloadFilePath = compressedzipfiles+'/compressed.zip'
                return send_file(downloadFilePath, as_attachment=True, download_name='compressed.zip')

        # Download the log file as a txt file when download log file button is clicked.
        if request.form.get('downloadlogfile'):
            return send_file('./static/logfile.txt', as_attachment=True, download_name='logfile.txt')

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