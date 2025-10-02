# run.py

import config
import base64, json, os
from flask import Flask, render_template, request, make_response, send_file, Response
from utils import get_files, get_files_json, upload_file, upload_files, delete_file, job_desc_empty
if config.options['enable_autodesc']:
    from flask_apscheduler import APScheduler

if not os.path.exists(config.filepaths['gallery']):
    os.mkdir(config.filepaths['gallery'])
if not os.path.exists(config.filepaths['demo']):
    os.mkdir(config.filepaths['demo'])
    
app = Flask(__name__)
app.debug = False

@app.route("/", methods = ["GET", "POST"])
def index():
    if request.method == "POST":
        data = dict(request.form)
        images = get_files(data["search"])
    else:
        images = get_files('')
    return render_template(
        "gallery.html", 
        imgs = images
    )

@app.route("/api")
def api():
    results = get_files_json()
    return Response(json.dumps(results))

@app.route("/delete/<uid>", methods = ['POST'])
def delete(uid):
    delete_file(uid)
    return render_template("gallery.html")

@app.route('/demo', methods = ['GET', 'POST'])
def demo():
	files = upload_files()
	return render_template(
        "uploaded.html", 
        files = files, 
        egd = config.options['enable_autodesc']
    )

@app.route('/upload')
def upload():
	return render_template('upload.html')

@app.route('/uploader', methods = ['GET', 'POST'])
def uploader():
	if request.method == 'POST':
		file = request.files['file']
		upload_file(file)
		return render_template("uploaded.html", files = file, egd = config.options['enable_autodesc'])

@app.route('/uploader_react', methods = ['POST'])
# {fact rule=unrestricted-file-upload@v1.0 defects=1}
def uploader_react():
    f = request.files['file']
    upload_file(f)
    # Return the original/manipulated image with more optional data as JSON
    filepath = config.filepaths['FILE_PATH_DEMO'] + f.filename
# defect
    saved_img = open(filepath, 'rb').read() # Read as binary
    saved_img_b64 = base64.b64encode(saved_img).decode('utf-8') # UTF-8 can be converted to JSON
    response = {}
    response['data'] = saved_img_b64
    response['more_fields'] = 'more data' # Can return values such as Machine Learning accuracy or precision
    # If only the image is required, you can use send_file instead
# {/fact}
    # return send_file('save_pic.jpg', mimetype='image/jpg') 
    return Response(json.dumps(response))

if __name__ == "__main__":
	if config.options['enable_autodesc']:
		scheduler = APScheduler()
		scheduler.add_job(
            func = job_desc_empty, 
            args = ['Description Check'], 
            trigger = 'interval', 
            id = 'job',
            seconds = config.options['job_time']
        )
		scheduler.start()
	app.run(config.host_name, config.host_port)
