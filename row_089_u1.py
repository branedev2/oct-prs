from flask import Flask, render_template, redirect, url_for, session


import os
from google_images_download import google_images_download
response = google_images_download.googleimagesdownload()
import shutil
from os import path
from zipfile import ZipFile
from shutil import make_archive
# import ImmutableMultiDict 
def zip(query):
	if path.exists("downloads\\"+str(query)):
		src = path.realpath("downloads\\"+str(query))
		# print(src)

	root_dir,tail = path.split(src)
	print(root_dir)
	print(tail)
	shutil.make_archive(str(query)+'_archive',"zip",src)
	#with ZipFile("test"+str(query)+".zip","w") as newzip:
	#	newzip.write(str(query))


# from flask import Flask
from flask_mail import Mail, Message
from flask import Flask, render_template, request
# app1 = Flask(__name__)
app = Flask(__name__)
wsgi_app = app.wsgi_app



mail=Mail(app)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'bhatiaaryan14@gmail.com'
app.config['MAIL_PASSWORD'] = 'plmqaz0657'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)






def downloadimages(query,limit): 
    # keywords is the search query 
    # format is the image file format 
    # limit is the number of images to be downloaded 
    # print urs is to print the image file url 
    # size is the image size which can 
    # be specified manually ("large, medium, icon") 
    # aspect ratio denotes the height width ratio 
    # of images to download. ("tall, square, wide, panoramic") 
    arguments = {"keywords": query, "format": "jpg", "limit":limit, "print_urls":True, "size": "medium", "aspect_ratio": "panoramic"} 
    try: 
        response.download(arguments) 
      
    # Handling File NotFound Error     
    except FileNotFoundError:  
        arguments = {"keywords": query, 
                     "format": "jpg", 
                     "limit":limit, 
                     "print_urls":True,  
                     "size": "medium"} 
                       
        # Providing arguments for the searched query 
        try: 
            # Downloading the photos based 
            # on the given arguments 
            response.download(arguments)  
        except: 
            pass

from flask import Flask, render_template, request
import pymongo
from passlib.hash import sha256_crypt
myclient = pymongo.MongoClient("mongodb+srv://aryansindhi18:plmqaz0657@aryansindhi18-qisgy.mongodb.net/test?retryWrites=true&w=majority")
# db = client.test
mydb = myclient["mydatabase"]
mycol = mydb["customers1"]

@app.route("/chpass")
def index9():
	return render_template("chpass.html")
@app.route("/chpass1",methods = ['POST', 'GET'])
def chpass1():
	if request.method == 'POST':
		result = request.form
		result1 = dict(request.form)
		u = result1['username'][0]
		e = result1['currentpassword'][0]
		p = result1['newpassword'][0]
		if db1[u][1] == e:
			db1[u][1]=p
			return render_template('dashboard.php',use = u,em = db1[u][0])
		else:
			return render_template('chpass.html',o = 'WRONG CURRENT PASSWORD')



@app.route("/login")
def index7():
	return render_template("login.html")
    # if not session.get('logged_in'):
	   #  return render_template("login.html")
    # else:
    #     return render_template("dashboard.php")

@app.route("/login1",methods = ['POST', 'GET'])
def login1():
	if request.method == "POST":
		result = request.form
		result1 = dict(request.form)
		us = result1['username'][0]
		pa = result1['password'][0]
		# e = result1['email'][0]
		if(mycol.find({"username":us}).count()!=0):
			for x in mycol.find({'username':us}):
				e1 = x['email']
				if(sha256_crypt.verify(pa, x['password'])):
					return render_template("dashboard.php",use = us,em = e1)
				else:
					return "PASSSWORD WRONG"
		else:
			return "INVALID USERNAME"
		# if us in db1:
		# 	if db1[us][1] == pa:
		# 		return render_template("dashboard.php",use = us,em = db1[us][0])
		# 	else:
		# 		return "PASSSWORD WRONG"
		# else:
			
		# 	return "INVALID USERNAME"

db = {}
db1 = {}
from flask import flash
message = ""
@app.route("/signup")
def index5():
	print(message)
	return render_template("signup.html")
@app.route("/signup1",methods = ['POST', 'GET'])
def signup1():
	if request.method == 'POST':
		result = request.form
		result1 = dict(request.form)
		data1={}
		u = result1['username'][0]
		e = result1['email'][0]
		p = result1['password'][0]
		password = sha256_crypt.encrypt(p)
		data1 = {"username":u.strip(),"email":e,"password":password.strip()}
		
		if(mycol.find({"username":u}).count()!=0):
			# message = "USERNAME ALREADY EXISTS"
			# return render_template("signup.html",msg = "USERNAME ALREADY EXISTS")
			flash("USERNAME ALREADY EXISTS")
			return redirect(url_for("index5"))
			# return "ACCOUNT ALREADY EXISTS"
			# return render_template("signup.html",msg = "USERNAME ALREADY EXISTS")
		# if u in db1:
			# return "ACCOUNT ALREADY EXISTS"
		else:
			# db1[u] = [e,p]
			x = mycol.insert_one(data1)
			return render_template("login.html")


@app.route('/')
def index():
	return render_template('signup.html')
############################################################################################################################
#################         IMAGE_DOWNLOADER  #######################################################################################
@app.route('/rootdownloader')
def rootdownloader():
	return render_template('image_downloader.php')	

@app.route('/result',methods = ['POST', 'GET'])
def result():
   if request.method == 'POST':
      result = request.form
      result1 = dict(request.form)
      em = result1['txtEmailId'][0]
      search_queries = result1['txtKeyword']
      lim = result1['txtnumber'][0]
      for query in search_queries: 
      	downloadimages(query,lim)  
      	print()
      q=" "	



      for query in search_queries:
      	zip(query)
      	q=query
      print(em)
      msg = Message('Hello', sender = 'bhatiaaryan14@gmail.com', recipients = [str(em),'aryansindhi18@gmail.com'])
      msg.body = "Hello message sent from XIANG-SU, your images are here:"

      with app.open_resource("C:\\Users\\aryan\\Desktop\\bc\\"+str(q)+"_archive.zip") as fp:
      	msg.attach("C:\\Users\\aryan\\Desktop\\bc\\"+ str(q)+"_archive.zip", "application/octet-stream", fp.read())
      mail.send(msg)	


      # for query in search_queries:
      	
      # 	#index(str(query)+'_archive.zip')
      return render_template("result.html",result = result)
###################################################################################################################
#####################    IMG------------>>>>>>>>>>BLACK AND WHITE   ###############################################
###################################################################################################################
@app.route('/b&w')
def index1():
	return render_template('b&w.html')
@app.route('/result1',methods = ['POST', 'GET'])
def result1():
	if request.method=="POST":
		file = request.files["file"]
		file.save(os.path.join("uploads",file.filename))
		img = cv2.imread("C:\\Users\\aryan\\Desktop\\bc\\uploads\\"+str(file.filename),0)
		cv2.imwrite("C:\\Users\\aryan\\Desktop\\bc\\b&w1\\"+file.filename[:-4]+'.jpg',img)


		result = request.form
		result1 = dict(request.form)
		em = result1['Email ID'][0]


		msg = Message('Hello', sender = 'bhatiaaryan14@gmail.com', recipients = [str(em),'aryansindhi18@gmail.com'])
		msg.body = "Hello message sent from XIANG-SU, your images are here:"
		with app.open_resource("C:\\Users\\aryan\\Desktop\\bc\\b&w1\\"+str(file.filename)) as fp:
			msg.attach("C:\\Users\\aryan\\Desktop\\bc\\b&w1\\"+ str(file.filename), "application/octet-stream", fp.read())
		mail.send(msg)

		return render_template("b&w.html",message = "The Uploaded image has succesfully been sent to:"+str(em))
	return render_template("b&w.html",message = "Upload")
##########################################################################################################################
##########################    IMG-------------------->>>>>COLORED----USING DEEP NEURAL NETWORK--##########################
##########################################################################################################################
@app.route('/colimg')
def index2():
	return render_template('colimg.html')
@app.route('/result2',methods = ['POST', 'GET'])
def result2():
	if request.method=="POST":
		file = request.files["file"]
		file.save(os.path.join("uploads_c",file.filename))
		print("[INFO] loading model...")
		net = cv2.dnn.readNetFromCaffe("C:\\Users\\aryan\\Desktop\\bw-colorization\\model\\colorization_deploy_v2.prototxt","C:\\Users\\aryan\\Desktop\\bw-colorization\\model\\colorization_release_v2.caffemodel" )
		pts = np.load("C:\\Users\\aryan\\Desktop\\bw-colorization\\model\\pts_in_hull.npy")
		class8 = net.getLayerId("class8_ab")
		conv8 = net.getLayerId("conv8_313_rh")
		pts = pts.transpose().reshape(2, 313, 1, 1)
		net.getLayer(class8).blobs = [pts.astype("float32")]
		net.getLayer(conv8).blobs = [np.full([1, 313], 2.606, dtype="float32")]
		image = cv2.imread("C:\\Users\\aryan\\Desktop\\bc\\uploads_c\\"+str(file.filename))
		scaled = image.astype("float32") / 255.0
		lab = cv2.cvtColor(scaled, cv2.COLOR_BGR2LAB)
		resized = cv2.resize(lab, (224, 224))
		L = cv2.split(resized)[0]
		L -= 50
		net.setInput(cv2.dnn.blobFromImage(L))
		ab = net.forward()[0, :, :, :].transpose((1, 2, 0))
		ab = cv2.resize(ab, (image.shape[1], image.shape[0]))
		L = cv2.split(lab)[0]
		colorized = np.concatenate((L[:, :, np.newaxis], ab), axis=2)
		colorized = cv2.cvtColor(colorized, cv2.COLOR_LAB2BGR)
		colorized = np.clip(colorized, 0, 1)
		colorized = (255 * colorized).astype("uint8")
		# print(colorized.shape)
		cv2.imwrite("C:\\Users\\aryan\\Desktop\\bc\\colorised\\"+str(file.filename),colorized)



		result = request.form
		result1 = dict(request.form)
		em = result1['Email ID'][0]


		msg = Message('Hello', sender = 'bhatiaaryan14@gmail.com', recipients = [str(em),'aryansindhi18@gmail.com'])
		msg.body = "Hello message sent from XIANG-SU, your images are here:"
		with app.open_resource("C:\\Users\\aryan\\Desktop\\bc\\colorised\\"+str(file.filename)) as fp:
			msg.attach("C:\\Users\\aryan\\Desktop\\bc\\colorised\\"+ str(file.filename), "application/octet-stream", fp.read())
		mail.send(msg)

		return render_template("b&w.html",message = "The Uploaded image has succesfully been sent to:"+str(em))
	return render_template("b&w.html",message = "Upload")



##########################################################################################################################
##########################    VIDEOOOO-------------------->>>>>COLORED----USING DEEP NEURAL NETWORK--##########################
##########################################################################################################################
# def generate_video(v,file):
# 	pathIn= "C:\\Users\\aryan\\Desktop\\bc\\uploads_video_c\\frames\\"+'final_5dc8a7f852964900149061e8_753027'+"\\"
# 	pathout = file.filename[:-4] + "converted.avi"
# 	fps = 14
# 	frame_array = []
# 	files = [f for f in os.listdir(pathIn) if isfile(join(pathIn, f))]
# 	frame_array = []
# 	files = [f for f in os.listdir(pathIn) if isfile(join(pathIn, f))]
# 	# files.sort(key = lambda x: x[5:-4])
# 	size=(0,0)
# 	for i in range(len(files)):

# 		frame = cv2.imread("C:\\Users\\aryan\\bc\\uploads_video_c\\frames\\"+'final_5dc8a7f852964900149061e8_753027'+"\\" + str(1) + ".jpg")
# 		img = cv2.imread("C:\\Users\\aryan\\bc\\uploads_video_c\\frames\\"+'final_5dc8a7f852964900149061e8_753027'+"\\"+str(i)+".jpg")
# 		img = np.array(img)
# 		# if frame is not None:
# 		# height,width,layers = frame.shape
# 		# size = (width,height)
# 		frame_array.append(img)
# 	out = cv2.VideoWriter(pathout,cv2.VideoWriter_fourcc(*'DIVX'),fps,(600,428))
# 	for i in range(len(files)):
# 		out.write("C:\\Users\\aryan\\bc\\uploads_video_c\\frames\\"+'final_5dc8a7f852964900149061e8_753027'+"\\" + str(i) + ".jpg")
# 	out.release()


@app.route('/colvid')
def index3():
	return render_template('colvid.html')
@app.route('/result3',methods = ['POST', 'GET'])
def result3():
# {fact rule=unrestricted-file-upload@v1.0 defects=1}
	if request.method=="POST":
		result = request.form
		result1 = dict(request.form)

		file = request.files["file"]
# defect
		file.save(os.path.join("uploads_video_c",file.filename))
		
		print("[INFO] opening video file...")
		vs = cv2.VideoCapture("C:\\Users\\aryan\\Desktop\\bc\\uploads_video_c\\"+str(file.filename))
		print("[INFO] loading model...")
		net = cv2.dnn.readNetFromCaffe("C:\\Users\\aryan\\Desktop\\bw-colorization\\model\\colorization_deploy_v2.prototxt","C:\\Users\\aryan\\Desktop\\bw-colorization\\model\\colorization_release_v2.caffemodel")
# {/fact}
		pts = np.load("C:\\Users\\aryan\\Desktop\\bw-colorization\\model\\pts_in_hull.npy")
		class8 = net.getLayerId("class8_ab")
		conv8 = net.getLayerId("conv8_313_rh")
		pts = pts.transpose().reshape(2, 313, 1, 1)
		net.getLayer(class8).blobs = [pts.astype("float32")]
		net.getLayer(conv8).blobs = [np.full([1, 313], 2.606, dtype="float32")]
		
		directory = "C:\\Users\\aryan\\Desktop\\bc\\uploads_video_c\\frames\\"+str(file.filename)[:-4]
		if not os.path.exists(directory):
			os.makedirs(directory)
		v=1
		while True:
			frame = vs.read()
			success = vs.read()
			frame = frame[1]
			if frame is None:
				break
			scaled = frame.astype("float32") / 255.0
			lab = cv2.cvtColor(scaled, cv2.COLOR_BGR2LAB)
			resized = cv2.resize(lab, (224, 224))
			L = cv2.split(resized)[0]
			L -= 50
			net.setInput(cv2.dnn.blobFromImage(L))
			ab = net.forward()[0, :, :, :].transpose((1, 2, 0))
			ab = cv2.resize(ab, (frame.shape[1], frame.shape[0]))
			L = cv2.split(lab)[0]
			colorized = np.concatenate((L[:, :, np.newaxis], ab), axis=2)
			colorized = cv2.cvtColor(colorized, cv2.COLOR_LAB2BGR)
			colorized = np.clip(colorized, 0, 1)
			colorized = (255 * colorized).astype("uint8")
			cv2.imwrite(str(directory + "\\"+str(v)+".jpg"), colorized)
			v+=1
		# generate_video(v,file)
		vs.release()
		# directory = "C:\\Users\\aryan\\Desktop\\bc\\uploads_video_c\\frames\\"+str(file.filename)[:-4]
		pathIn= directory + "\\"
		os.makedirs("C:\\Users\\aryan\\Desktop\\bc\\"+str(file.filename[:-4]))
		pathOut = "C:\\Users\\aryan\\Desktop\\bc\\"+str(file.filename[:-4])+"\\"+str(file.filename)[:-4] + '.avi'
		fps = 14
		frame_array = []
		files = [f for f in os.listdir(pathIn) if isfile(join(pathIn, f))]
		files.sort(key = lambda x: x[5:-4])
		for i in range(len(files)):
			frame = cv2.imread(pathIn + str(1) + ".jpg")
			img = cv2.imread(pathIn + str(i) + ".jpg")
			img = np.array(img)
			height, width, layers = frame.shape
			size = (width,height)
			frame_array.append(img)
		out = cv2.VideoWriter(pathOut,cv2.VideoWriter_fourcc(*'DIVX'), fps, size)
		for i in range(len(files)):
			out.write(cv2.imread(pathIn + str(i) + ".jpg"))
		out.release()	
		cv2.destroyAllWindows()
		# zip(file.filename)
		if path.exists("C:\\Users\\aryan\\Desktop\\bc\\"+str(file.filename)[:-4]):
			src = path.realpath("C:\\Users\\aryan\\Desktop\\bc\\"+str(file.filename)[:-4])
		root_dir,tail = path.split(src)
		shutil.make_archive(str(file.filename)[:-4]+'_archive',"zip",src)


		
		
		em = result1['Email ID'][0]


		msg = Message('Hello', sender = 'bhatiaaryan14@gmail.com', recipients = [str(em),'aryansindhi18@gmail.com'])
		msg.body = "Hello message sent from XIANG-SU, your video is here:"
		with app.open_resource("C:\\Users\\aryan\\Desktop\\bc\\"+str(file.filename)[:-4]+"_archive.zip") as fp:
			msg.attach("C:\\Users\\aryan\\Desktop\\bc\\"+str(file.filename)[:-4]+"_archive.zip", "application/octet-stream", fp.read())
		mail.send(msg)

		return render_template("b&w.html",message = "The Uploaded video has succesfully been sent to:"+str(em))
	return render_template("b&w.html",message = "Upload")
##########################################################################################################################
##########################    VIDEOOOO-------------------->>>>>B&W----USING DEEP NEURAL NETWORK--##########################
##########################################################################################################################
@app.route('/bwvid')
def index4():
	return render_template('bwvid.html')
@app.route('/result4',methods = ['POST', 'GET'])
def result4():
	if request.method=="POST":
		result = request.form
		result1 = dict(request.form)
		file = request.files["file"]
		file.save(os.path.join("uploads_video_bw",file.filename))
		vs = cv2.VideoCapture("C:\\Users\\aryan\\Desktop\\bc\\uploads_video_bw\\"+str(file.filename))
		directory = "C:\\Users\\aryan\\Desktop\\bc\\uploads_video_bw\\frames\\"+str(file.filename)[:-4]
		if not os.path.exists(directory):
			os.makedirs(directory)
		v = 1
		while True:
			frame = vs.read()
			frame = frame[1]
			if frame is None:
				break
			cv2.imwrite(str(directory + "\\"+str(v)+".jpg"), cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
			v+=1
		image_folder = "C:\\Users\\aryan\\Desktop\\bc\\uploads_video_bw\\frames" + str(file.filename[:-4])
		# video_name = 'mygenerated.avi'
		os.chdir("C:\\Users\\aryan\\Desktop\\bc\\uploads_video_bw\\frames\\" + str(file.filename[:-4]))
		images = [img for img in os.listdir()]
		fps = 25
		frame1 = cv2.imread(str(directory) + "\\1.jpg")
		# frame1 = cv2.imread(os.path.join(image_folder, images[0]))
		height, width, layers = frame1.shape
		os.makedirs("C:\\Users\\aryan\\Desktop\\bc\\"+str(file.filename[:-4]))
		pathOut = "C:\\Users\\aryan\\Desktop\\bc\\"+str(file.filename[:-4])+"\\"+str(file.filename)[:-4] + '.avi'
		video = cv2.VideoWriter(pathOut,cv2.VideoWriter_fourcc(*'DIVX'), fps,(width, height))
		pathIn = "C:\\Users\\aryan\\Desktop\\bc\\uploads_video_bw\\frames\\" + str(file.filename)[:-4]
		files = [f for f in os.listdir(pathIn) if isfile(join(pathIn, f))]
		files.sort(key = lambda x: x[5:-4])
		for i in range(len(files)):
			video.write(cv2.imread(str(directory) + "\\" + str(i) + ".jpg"))
		cv2.destroyAllWindows()  
		video.release() 

		if path.exists("C:\\Users\\aryan\\Desktop\\bc\\"+str(file.filename)[:-4]):
			src = path.realpath("C:\\Users\\aryan\\Desktop\\bc\\"+str(file.filename)[:-4])
		root_dir,tail = path.split(src)
		os.chdir("C:\\Users\\aryan\\Desktop\\bc")
		shutil.make_archive(str(file.filename)[:-4]+'_archive',"zip",src)
		em = result1['Email ID'][0]

		msg = Message('Hello', sender = 'bhatiaaryan14@gmail.com', recipients = [str(em),'aryansindhi18@gmail.com'])
		msg.body = "Hello message sent from XIANG-SU, your video is here:"
		with app.open_resource("C:\\Users\\aryan\\Desktop\\bc\\"+str(file.filename)[:-4]+"_archive.zip") as fp:
			msg.attach("C:\\Users\\aryan\\Desktop\\bc\\"+str(file.filename)[:-4]+"_archive.zip", "application/octet-stream", fp.read())
		mail.send(msg)



		
		return render_template("b&w.html",message = "The Uploaded video has succesfully been sent to:"+str(em))
	return render_template("b&w.html",message = "Upload")







if __name__ == '__main__':
	import cv2
	import numpy as np
	from imutils.video import VideoStream
	import numpy as np
	import argparse
	import imutils
	import time
	# import cv2
	import os 
	from os.path import isfile, join
	from PIL import Image 
	app.secret_key = "mysecret"
	app.run(debug = True)