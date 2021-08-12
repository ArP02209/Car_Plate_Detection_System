from flask import Flask,redirect,url_for,render_template,request
import urllib.request
import os
from werkzeug.utils import secure_filename
import cv2
import boto3
import Car_Number_Plate_Detection_Code

# Import dependencies

app = Flask(__name__)

UPLOAD_FOLDER = 'static/cars'
 
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/',methods=['GET','POST'])
def home():
    if request.method=='POST':
        # Handle POST Request here
        return render_template('index.html')
    return render_template('index.html')

@app.route('/upload', methods=['GET','POST'])
def upload():
        if request.method=='POST':
            f = request.files['file1']
            #cv2.imwrite("final_img.jpg", f)
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
            ACCESS_KEY = '*****************'
            SECRET_KEY = '********************'
            bucket="task8ml"
            s3_file="user_file.png"

            client_s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,aws_secret_access_key=SECRET_KEY)
            client_s3.upload_file("./static/cars/"+f.filename, bucket, s3_file)
            os.system("curl https://task8ml.s3.ap-south-1.amazonaws.com/user_file.png -O user_file.png")
            os.system("move user_file.png user_car_Image/")
            img = "user_file.png"
            final_detected_number_plate = Car_Number_Plate_Detection_Code.detected_number_plate(img)
            vehicle_info = Car_Number_Plate_Detection_Code.rto(final_detected_number_plate)
            return render_template("index.html", output = vehicle_info)

if __name__ == '__main__':
    #DEBUG is SET to TRUE. CHANGE FOR PROD
    app.run()
