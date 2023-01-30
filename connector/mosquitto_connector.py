import os
import sys
import numpy as np

import paho.mqtt.client as mqtt
import gridfs
from datetime import datetime, timedelta

import cv2 as cv
from PIL import Image 

cwd = os.getcwd()

sys.path.append('/Users/insaindev/source/news/GOC/')
import mongo_helper

# initiate gridfs database
fs = gridfs.GridFS(mongo_helper.mydb)

path = cwd + '/imgs/'
print(path)
# Check whether the specified path exists or not
isExist = os.path.exists(path)
if not isExist:
   # Create a new directory because it does not exist
   os.makedirs(path)

class FrameCapture(object):
    def __init__(self, frame_id, source_id, ticks, processed_flag, datetime_str, meta):
        self.frame_id = frame_id
        self.source_id = source_id
        self.ticks = ticks
        self.processed_flag = processed_flag
        self.datetime_str = datetime_str
        self.meta = meta

    def asdict(self):
        return {'frame_id': self.frame_id, 'source_id': self.source_id, 'ticks': self.ticks, 'processed_flag': self.processed_flag, 'datetime': str(self.datetime_str), 'meta': self.meta}
        
# mosquitto parameters
broker_url = "192.168.101.145"
broker_port = 1883

def on_connect(client, userdata, flags, rc):
    print("Connected With Result Code "+ str(rc))
    
def execute(client, userdata, message):
    try:
        message = message.payload 
        # get frame_id
        frame_id = int.from_bytes(message[0:4],"big")
        # get source_id
        source_id = int.from_bytes(message[4:8],"big")
        # get ticks (Datetime in format "%Y-%m-%d %H:%M:%S")
        ticks = int.from_bytes(message[8:16],"big")
        # frame_bytes
        frame_bytes = message[16:]
        # convert ticks to datetime
        time_converted = datetime(1, 1, 1) + timedelta(microseconds = ticks/10)
        # reformat datetime to correct format
        time = time_converted.strftime("%Y-%m-%d %H:%M:%S")
        
        print("CameraId: " + str(source_id) + " frame_id " + str(frame_id) + " " + str(ticks) + " " + str(type(frame_bytes)))

        # convert ndarray to string
        imageString = str(bytes(frame_bytes))
        
        imgArr = np.array(Image.frombytes('RGB', (800,600), bytes(frame_bytes)))
        img_name = str(source_id) + '_' + str(frame_id)+ '_' + str(ticks) + '.jpg'
        img_path = path + img_name 
        cv.imwrite(img_path, imgArr)    
        cap = cv.VideoCapture(img_path)
        hasFrame, frame = cap.read()
        if (hasFrame):
            print(frame.shape)
            
            #Open the image in read-only format.
            with open(img_path, 'rb') as f:
                contents = f.read()

            #Now store/put the image via GridFs object.
             
             # store the image
            image_id = fs.put(contents, encoding='utf-8')

            # stored image_id
            meta = { 'fs_image_id': image_id, 'shape': frame.shape, 'dtype': str(frame.dtype)}
            
            # instantiate object
            frame_capture =FrameCapture(frame_id=frame_id, source_id=source_id, ticks=ticks, processed_flag=False, datetime_str=time, meta=meta)

            # insert frame_capture to database
            mongo_helper.insertRow(frame_capture.asdict())
            
            # remove image
            os.remove(img_path) 
        cap.release
        
       
        

       

        """
        Store a new image with its meta data into the database:

        # convert ndarray to string
        imageString = image.tostring()

        # store the image
        imageID = fs.put(imageString, encoding='utf-8')

        # create our image meta data
        meta = {
            'name': 'myTestSet',
            'images': [
                {
                    'imageID': imageID,
                    'shape': image.shape,
                    'dtype': str(image.dtype)
                }
            ]
        }

        # insert the meta data
        testCollection.insert_one(meta)

        
        Get the image back:

        # get the image meta data
        image = testCollection.find_one({'name': 'myTestSet'})['images'][0]

        # get the image from gridfs
        gOut = fs.get(image['imageID'])

        # convert bytes to ndarray
        img = np.frombuffer(gOut.read(), dtype=np.uint8)

        # reshape to match the image size
        img = np.reshape(img, image['shape'])
        """
       
        
        # # resize 800*600
        # imgArr = np.array(Image.frombytes('RGB', (800,600), bytes(frame_bytes)))
        # img_name = str(cameraId) + '_' + str(frame_id)+ '_' + str(ticks) + '.jpg'
        # img_path = cwd + '/imgs/' + img_name 
        # cv.imwrite(img_path, imgArr)    
        # cap = cv.VideoCapture(img_path)
        # hasFrame, frame = cap.read()
        # cap.release
        # # # #object classification
        # objectClassification(frame,cameraId,time, img_name)   

        # # remove image
        # os.remove(img_path)    
         
    except (Exception) as error :
        print ("Error ", error)
        
if __name__ == "__main__":    
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = execute
    client.connect(broker_url, broker_port)    
    client.subscribe("inputQueue", qos=0)    
    client.publish(topic="inputQueue", payload="Init...........", qos=0, retain=False)
    client.loop_forever()