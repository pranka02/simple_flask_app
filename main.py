import json
import os
import io
import utils
from functools import reduce
from flask import Flask, flash, request, redirect, url_for, render_template,send_from_directory, session
from werkzeug.utils import secure_filename
from flask_basicauth import BasicAuth
from flask_httpauth import HTTPBasicAuth

allowed_ext = set(['json'])

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['upload_path'] = 'uploads'
app.config['static_path'] = 'static'
app.config['output_path'] = 'output'
app.config['input_filename'] ='input.json'
app.config['output_filename'] ='output.json'


# Authorisation
auth = BasicAuth(app)

app.config['BASIC_AUTH_USERNAME'] = 'User'
app.config['BASIC_AUTH_PASSWORD'] = 'Revolut'

basic_auth = BasicAuth(app)

@app.route('/')
@basic_auth.required
def index():
    return render_template('index.html')

# Helper functions
@app.route('/uploads/<filename>')
def uploaded_file(filename):
	return send_from_directory(app.config['upload_path'],filename)

def allowed_file(filename):
    return '.' in filename and \
			filename.rsplit('.', 1)[1].lower() in allowed_ext

def file_exists(file_path,filename):
    exists = os.path.isfile(os.path.join(file_path,filename))
    if exists:
        return True
    else:
        return False

def strip_space(inp_str):
    new_list = list(((inp_str.replace(" ", "")).strip()).split(',')) 
    for i in range(len(new_list)):
        if not new_list[i] :
            new_list.pop(i)
    return new_list


def save_json_file(nest_dict):
    filename = secure_filename(app.config['output_filename'])
    output_filepath = os.path.join(app.config['output_path'],filename)
    with open(output_filepath, 'w') as fp:
         json.dump(nest_dict, fp)
    return


@app.route('/output/<filename>',methods=['GET','POST'])
@basic_auth.required
def download_output_file(filename):
    if request.method =='POST' and 'Download':
        return send_from_directory(app.config['output_path'],filename )



@app.route('/', methods=['GET','POST'])
@basic_auth.required
def upload_input_file():
    if request.method == 'POST' and 'input':
        # check if the post request has the file part
        if 'input' not in request.files:
            flash('Please select a file to upload')
            return redirect(url_for('index'))
        file = request.files['input']
       
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):

        	file.filename =app.config['input_filename']
        	filename = secure_filename(file.filename)
        	file.save(os.path.join(app.config['upload_path'],filename))
        	flash('File uploaded successfully !')
        	return redirect(url_for('index'))
            
        else:
       		flash('Format not supported. Please upload a file in .json format.')
        	return redirect(url_for('index'))  
        redirect(url_for('uploaded_file',filename=filename))
    return


@app.route('/output', methods=['GET','POST'])
@basic_auth.required
def nest_dictionary():
    params_list = request.form['input']

    if params_list is not None :
        if file_exists(app.config['upload_path'], app.config['input_filename']):
            data = utils.json_parser(os.path.join(app.config['upload_path'],app.config['input_filename']))
        else:
            flash('No input file found')
            return redirect(url_for('index'))
        if not data:
            flash('Empty file uploaded')
            return redirect(url_for('index'))

        key_levels = strip_space(params_list)
        all_levels = list(data[0].keys())

        if not key_levels:
            flash('Space cannot be entered as parameters. Enter "none" for no nesting')
            return redirect(url_for('index'))

        elif len(key_levels)==1 and key_levels[0].lower()=="none":
            save_json_file(data)
            return render_template("output.html",result = data,params =params_list)

        elif len(key_levels) > len(all_levels) or all(x not in all_levels for x in key_levels):
            flash('Nesting level keys not found in flat dictionary')
            return redirect(url_for('index'))


        elif len(key_levels) <=len(all_levels):
            nested_dict = utils.make_nested_dictionary(data,all_levels,key_levels)

            save_json_file(nested_dict)
            return render_template("output.html",result = nested_dict,params =params_list)
    else:
            flash('Please enter nesting parameters.')
            return redirect(url_for('index'))


if __name__ == '__main__':
	app.run(host="127.1.1.0",port=7770,debug=True)