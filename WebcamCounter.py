#!/usr/bin/env python
# coding: utf-8

# Einkommentieren, falls nur CPU genutzt werden soll

#import os
#os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

import predict
import numpy as np
import cv2
import urllib
from datetime import datetime
import boto3
import json
import ssl
import os

ssl._create_default_https_context = ssl._create_unverified_context

class PeopleCounter:
    def get_image(self, url, id):
        resp = urllib.request.urlopen(url)
        self.image = np.asarray(bytearray(resp.read()), dtype="uint8")
        #if self.img is not None:
        self.image = cv2.imdecode(self.image, -1)
        filename = "/tmp/"+ str(id) + ".jpg"
        status = cv2.imwrite(filename, self.image)
        print("Image written to file-system : ",status)
        directory = r'/tmp'
        print(os.path.join(directory, filename))            
        pred = predict.main(os.path.join(directory, filename))
        peoplecount = len([x for x in pred if x["probability"]>0.5]) 
        print(predict.main(os.path.join(directory, filename)))
        print("count of people : ",peoplecount) 
        return peoplecount


if __name__ == '__main__':
    with open("webcam_list.json","r") as f:
        webcams = json.load(f)
    pc = PeopleCounter()
    for cam in webcams:
        print(cam)
        try:
            cam['Personenzahl'] =  pc.get_image(cam['URL'], cam['ID'])
            cam['Stand'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            print(cam["Name"]+" :"+str(cam["Personenzahl"]))        
        except urllib.error.HTTPError as e:
            print(cam["Name"]+" :"+'The server couldn\'t fulfill the request.')
            print('Error code: ', e.code)
        except urllib.error.URLError as e:
            print(cam["Name"]+" :"+'We failed to reach a server.')
            print('Reason: ', e.reason)
        except:
            pass
            #print("Unexpected error:", sys.exc_info()[0])

    client_s3 = boto3.client("s3" )

    response = client_s3.put_object(
        Bucket="sdd-s3-bucket",
        Body=json.dumps(webcams),
       Key=f"webcamdaten/{datetime.now().strftime('%Y/%m/%d/%H')}webcamdaten-customvision.json"
     )
    
    #directory = r'/tmp'
    #for filename in os.listdir(directory):
    #    if filename.endswith(".jpg"):
    #        print(os.path.join(directory, filename))
    #        s3 = boto3.resource('s3')
    #        s3.Bucket('sdd-s3-bucket').upload_file(os.path.join(directory, filename), f"webcampictures/{datetime.now().strftime('%Y/%m/%d/%H')}" + "/" + filename)  
    #    else:
    #        continue
    
