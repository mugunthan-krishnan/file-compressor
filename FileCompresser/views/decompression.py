import io
import os
from flask import Blueprint, render_template, request, send_file
import shutil
import lzma
decompress = Blueprint('decompressfile', __name__)

# Global Variables
decompressedzipfiles = './FileCompresser/static/decompressedzipfiles'
decompressedfiles = './FileCompresser/static/decompressedfiles'

@decompress.route('/decompress', methods=['GET','POST'])
def decompressPage():
    enabledwnld = False
    if request.method == "GET":
        shutil.rmtree(decompressedzipfiles)
        os.mkdir(decompressedzipfiles)
        shutil.rmtree(decompressedfiles)
        os.mkdir(decompressedfiles)
    
    if request.method == "POST":
        if request.form.get("decompress"):
            input_file = request.files['file']
            if input_file.filename.find('.zip'):
                input_file.save(decompressedzipfiles+'/decompressedzip.zip')
                shutil.unpack_archive(decompressedzipfiles+'/decompressedzip.zip', decompressedfiles)

                for dirName, subdirList, fileList in os.walk(decompressedfiles):
                    print(dirName)
                for fname in fileList:
                    print('\t%s' % fname)
                
                print(fileList)
        #     data = input_file.stream.read()
        #     decompresser = lzma.LZMADecompressor()
        #     compressed_data = decompresser(data)
        #     output_file = './static/decompressedfiles/decompressed.txt'
        #     with open(output_file, 'wb') as f:
        #         f.write(compressed_data)
        #     enabledwnld = True
        # if request.form.get("download"):
        #     if os.path.isfile('./static/decompressedfiles/decompressed.txt'):
        #         downloadFilePath = './static/decompressedfiles/decompressed.txt'
        #         return send_file(downloadFilePath, as_attachment=True, download_name='decompressed_file.txt')
    return render_template('decompress.html', enabledwnld=enabledwnld)