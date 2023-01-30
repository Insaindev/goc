
class FrameCapture(object):
    def __init__(self, db_image_id, frame_id, source_id, ticks, processed_flag, datetime_str, meta):
        self.db_image_id = db_image_id
        self.frame_id = frame_id
        self.source_id = source_id
        self.ticks = ticks
        self.processed_flag = processed_flag
        self.datetime_str = datetime_str
        self.meta = meta

    def toDict(self):
        return {'db_image_id': self.db_image_id, 'frame_id': self.frame_id, 'source_id': self.source_id, 'ticks': self.ticks, 'processed_flag': self.processed_flag, 'datetime': str(self.datetime_str), 'meta': self.meta}

class DetectedObject(object):
    def __init__(self,object_type_id : int, count: int):
        self.object_type_id = object_type_id
        self.count = count

    def toDict(self):
        return { 'object_type_id': self.object_type_id, 'count': self.count}
    
import os
import sys
import json
import numpy as np
from collections import OrderedDict
import cv2 as cv
import psycopg2
import gridfs
from PIL import Image 

sys.path.append('/Users/insaindev/source/news/GOC/')
import mongo_helper 

# initiate gridfs database
fs = gridfs.GridFS(mongo_helper.mydb)
 
cwd = os.getcwd()

path = cwd + '/imgs/'
detections_path = cwd + '/detections'
# Check whether the specified path exists or not
isExist = os.path.exists(path)
if not isExist:
   # Create a new directory because it does not exist
   os.makedirs(path)
   
# Check whether the specified path exists or not
isExist = os.path.exists(detections_path)
if not isExist:
   # Create a new directory because it does not exist
   os.makedirs(detections_path)

OPENCV_DNN_OPENCL_ALLOW_ALL_DEVICES=1 

available_classes = {}
# enum with allowed detected objects
detectedObject = {'car':1, 'truck':2, 'bus':3, 'bicycle':4, 'person':5}

# Load names of classes
classesFile = "coco.names"
classes = None
with open(classesFile, 'rt') as f:
    classes = f.read().rstrip('\n').split('\n')

# Initialize the parameters
confThreshold = 0.7  #Confidence threshold
nmsThreshold = 0.4   #Non-maximum suppression threshold
inpWidth = 128       #Width of network's input image
inpHeight = 128      #Height of network's input image

# Give the configuration and weight files for the model and load the network using them.
modelConfiguration = "yolov3.cfg"
modelWeights = "yolov3.weights"

net = cv.dnn.readNetFromDarknet(modelConfiguration, modelWeights)
#net.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)
net.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)

#CPU usage
net.setPreferableTarget(cv.dnn.DNN_TARGET_CPU)
#GPU usage
#net.setPreferableTarget(cv.dnn.DNN_TARGET_OPENCL_FP16)

# Get the names of the output layers
def _getOutputsNames(net):
    # Get the names of all the layers in the network
    layersNames = net.getLayerNames()
     # Get the names of the output layers, i.e. the layers with unconnected outputs
    outLayers =  [layersNames[i - 1] for i in net.getUnconnectedOutLayers()]
    return outLayers

# Remove the bounding boxes with low confidence using non-maxima suppression
def _postprocess(frame, outs):
    frameHeight = frame.shape[0]
    frameWidth = frame.shape[1]

    # Scan through all the bounding boxes output from the network and keep only the
    # ones with high confidence scores. Assign the box's class label as the class with the highest score.
    classIds = []
    confidences = []
    boxes = []
    objectClasses = []
    for out in outs:
        for detection in out:
            scores = detection[5:]
            box = detection[0:4] * np.array([frameWidth, frameHeight, frameWidth, frameHeight])
            (centerX, centerY, width, height) = box.astype("int")
            
            # Use the center (x, y)-coordinates to derive the top and left corner of the bounding box
            x = int(centerX - (width / 2))
            y = int(centerY - (height / 2))
            
            classId = np.argmax(scores)
            confidence = scores[classId]
            if confidence >= confThreshold:
                width = int(detection[2] * frameWidth)
                height = int(detection[3] * frameHeight)
                classIds.append(classId)
                confidences.append(float(confidence))
                boxes.append([x, y, int(width), int(height)])
            
    # Perform non maximum suppression to eliminate redundant overlapping boxes with
    # lower confidences.
    indices = cv.dnn.NMSBoxes(boxes, confidences, confThreshold, nmsThreshold)
    #print('indices ', indices)
    for i in indices:
        #i = i[0]
        box = boxes[i]
        x,y,w,h = box
        objectClasses.append(classes[classIds[i]])

        _draw_bounding_box(frame, classIds[i], confidences[i], round(box[0]), round(box[1]), round(box[0]+w), round(box[1]+h))
        
    return objectClasses

COLORS = np.random.uniform(0, 255, size=(len(classes), 3))

def _draw_bounding_box(img, class_id, confidence, x, y, x_plus_w, y_plus_h):
    label = str(classes[class_id]) + ' ' + str(confidence)
    color = COLORS[class_id]
    cv.rectangle(img, (x,y), (x_plus_w, y_plus_h), color, 2)
    cv.putText(img, label, (x-10,y-10), cv.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

def _group_list(lst):       
    res =  [(el, lst.count(el)) for el in lst] 
    return list(OrderedDict(res).items())

def objectClassification(frame,frame_capture):
        detected_objects  = []
        # Get blobs from images        
        blob = cv.dnn.blobFromImage(frame, 1/255, (inpWidth, inpHeight), [0,0,0], 1, crop=False)
         # Sets the input to the network
        net.setInput(blob)
        #  # Runs the forward pass to get output of the output layers
        outs = net.forward(_getOutputsNames(net))     
        #  # Remove the bounding boxes with low confidence
        results = _postprocess(frame, outs)
        #  #Print grouped results based on classId
        grpResult = _group_list(results)        

        # iterate all grouped objects and try to classificate them
        for tplResult in grpResult:
            #split key and value
            #key => objectTypeId
            #value => count of objects
            objectType,objectsCount = tplResult
            
            # instantiate detectoobject class with variables
            det_obj = DetectedObject(object_type_id=int(available_classes[objectType]), count=int(objectsCount))
            
            # add clsas to list
            detected_objects.append(det_obj.toDict())

        # init frame_capture meta
        frame_capture.meta = detected_objects

        return frame_capture.toDict()
            
if __name__ == '__main__':
       
    # create class generator from classes (coco.names)
    myEnumStrings = ( (x, i) for i, x in enumerate(classes))
    # generate dictionary <objectname:object_identifier>
    available_classes = {key: value for (key, value) in myEnumStrings}
    
    # get oldest 10 images from mongodb database
    frames = mongo_helper.getNotProcessedFrames(1)
    
    # iterate throught frames
    # frame_id, source_id, ticks, processed_flag, datetime_str, meta
    for frame in frames:
        
        # initiate collection row variables
        frame_id = frame['frame_id']
        source_id = frame['source_id']
        ticks = frame['ticks']
        processed_flag = frame['processed_flag']
        datetime_str = frame['datetime']
        stored_image_id = frame['meta']['fs_image_id']
        stored_image_shape = frame['meta']['shape']
        
        # set image row to processed
        mongo_helper.setProcessed(stored_image_id)
    
        # get the image from gridfs
        gOut = fs.get(stored_image_id)
        
        # convert to Image PIL and save it
        captured_img = Image.open(gOut)
        
        # init whole img name with path
        img_path = path + str(stored_image_id)+'_img.jpg'
        captured_img.save(img_path)
        
        # capture frame to opencv
        cap = cv.VideoCapture(img_path)
        hasFrame, frame = cap.read()
        cap.release()
        
        # instantiate captured frame variables
        frame_capture = FrameCapture(db_image_id= stored_image_id, frame_id=frame_id, source_id=source_id, ticks=ticks, processed_flag=True, datetime_str=datetime_str, meta='')

        # objects classification
        detected_objects = objectClassification(frame,frame_capture)
        
        # printout result
        print('DEECTED ', str(detected_objects))
        
        # remove image
        os.remove(img_path)
        
         