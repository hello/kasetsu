from flask import Flask,request,send_from_directory
app = Flask(__name__,static_url_path='')

@app.route('/')
def get_root_dir():
   return ''

@app.route('/raw/<path:path>')
def get_raw_file(path):
    return send_from_directory('raw',path)
