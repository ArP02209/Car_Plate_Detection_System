#!/usr/bin/env python
# coding: utf-8

# In[17]:


# Import dependencies
import numpy as np
import boto3
import matplotlib.pyplot as plt
import cv2
import re
import os
import requests
import json
import xmltodict
import aws_credentials
carplate_haar_cascade = cv2.CascadeClassifier('./haarcascade_russian_plate_number.xml')


# In[2]:


# Setup function to detect car plate
def carplate_detect(image):
    carplate_overlay = image.copy() 
    carplate_rects = carplate_haar_cascade.detectMultiScale(carplate_overlay,scaleFactor=1.1, minNeighbors=3)
    for x,y,w,h in carplate_rects: 
        cv2.rectangle(carplate_overlay, (x,y), (x+w,y+h), (0,255,0), 5) 
        return carplate_overlay


# In[3]:


def carplate_extract(carplate_img_rgb):
    try:
        carplate_rects = carplate_haar_cascade.detectMultiScale(carplate_img_rgb,scaleFactor=1.1, minNeighbors=5)
        for x,y,w,h in carplate_rects: 
            carplate_img = carplate_img_rgb[y:y+h ,x:x+w] # Adjusted to extract specific region of interest i.e. car license plate
    
        return carplate_img
    except:
    
        
        # Function detects faces and returns the cropped face
        # If no face detected, it returns the input image
    
        gray = cv2.cvtColor(carplate_img_rgb,cv2.COLOR_BGR2GRAY)
        carplate_crop = carplate_haar_cascade.detectMultiScale(gray, 1.3, 5)
    
        if carplate_crop is ():
            return None
    
        # Crop all faces found
        for (x,y,w,h) in carplate_crop:
            carplate_img  = carplate_img_rgb[y:y+h, x:x+w]

        return carplate_img


# In[4]:



# Enlarge image for further processing later on
def enlarge_img(image, scale_percent):
    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)
    dim = (width, height)
    resized_image = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)
    return resized_image


# In[32]:


def detected_number_plate(img):
    # Read car image and convert color to RGB
    carplate_img = cv2.imread('./user_car_Image/{}'.format(img))
    carplate_img_rgb = cv2.cvtColor(carplate_img, cv2.COLOR_BGR2RGB)
    #plt.imshow(carplate_img_rgb)

    # Import Haar Cascade XML file for Russian car plate numbers
    carplate_haar_cascade = cv2.CascadeClassifier('./haarcascade_russian_plate_number.xml')

    detected_carplate_img = carplate_detect(carplate_img_rgb)
    #plt.imshow(detected_carplate_img)

    # Display extracted car license plate image
    carplate_extract_img = carplate_extract(carplate_img_rgb)

    carplate_extract_img = enlarge_img(carplate_extract_img, 150)
    #plt.imshow(carplate_extract_img)

    cv2.imwrite("final_img.jpg", carplate_extract_img)

    ACCESS_KEY = aws_credentials.ACCESS_KEY
    SECRET_KEY = aws_credentials.SECRET_KEY
    bucket="task8ml"
    s3_file="car.png"

    client_s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY)
    client_s3.upload_file("final_img.jpg", bucket, s3_file)


    client_textract = boto3.client('textract', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
    response_textract = client_textract.detect_document_text(
        Document={
            'S3Object': {
                'Bucket': bucket,
                'Name': s3_file,
            }
        }
    )

    try:
        if ("IND" or "ND" or "NND" or "TND") in (response_textract["Blocks"][1]["Text"]):
            return(re.sub("[^0-9A-Z]", "", response_textract["Blocks"][2]["Text"]))
        else:
            p=(re.sub("[^0-9A-Z]", "", (response_textract["Blocks"][1]["Text"]).replace("IND","")))
            if ("NND" or "TND" or "ND") in p:
                return((((re.sub("[^0-9A-Z]", "", response_textract["Blocks"][1]["Text"]).replace("NND","")).replace("TND","")).replace("IND","")).replace("ND",""))
            else:
                return(p)
    except Exception as e:
        return(e)


# In[33]:

"""
os.system("curl https://task8ml.s3.ap-south-1.amazonaws.com/user_file.png -O user_file.png")
os.system("move user_file.png user_car_Image/")
img = "user_file.png"
final_detected_number_plate = detected_number_plate(img)
print(final_detected_number_plate)"""


# In[16]:

def rto(final_detected_number_plate):
    try:
        vehicle_reg_no = final_detected_number_plate #NumberPlate deteted
        username = "Adi@0920" #API_user name
        url = "http://www.regcheck.org.uk/api/reg.asmx/CheckIndia?RegistrationNumber=" + vehicle_reg_no + "&username="+username
        url=url.replace(" ","%20")
        r = requests.get(url)
        #print(r.content)
        n = xmltodict.parse(r.content)#xmltodict. parse() method takes an XML file as input and changes it to Ordered Dictionary. 
        #print(n)
        k = json.dumps(n)
        #print(k)
        df = json.loads(k)
        #print(df)
        l=df["Vehicle"]["vehicleJson"]
        #print(l)
        p=json.loads(l)
        s="\nVehicle Registration Number : "+vehicle_reg_no+"\nOwner name : "+str(p['Owner'])+"\n"+"Car Company : "+str(p['CarMake']['CurrentTextValue'])+"\n"+"Car Model : "+str(p['CarModel']['CurrentTextValue'])+"\n"+"Fuel Type : "+str(p['FuelType']['CurrentTextValue'])+"\n"+"Registration Year : "+str(p['RegistrationYear'])+"\n"+"Insurance : "+str(p['Insurance'])+"\n"+"Vehicle ID : "+str(p['VechileIdentificationNumber'])+"\n"+"Engine No. : "+str(p['EngineNumber'])+"\n"+"Location RTO : "+str(p['Location'])
        return(s)
    except:
        msg="Unable to retrieve vehicle information, plz \nprovide clear image"
        return(msg)


# In[ ]:




