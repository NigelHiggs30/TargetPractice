from PIL import Image, ImageChops
import numpy as np
from numpy import asarray
import cv2
import os
import zmq
import json
from json import JSONEncoder
import subprocess
import time

#local file path to subprocess module. 
subprocess.__file__

#finds all image in directory ending in .png
def list_iter(folder_dir):
    file_paths = []
    for images in os.listdir(folder_dir):

        if (images.endswith(".png")):
            file_paths.append(images)

    return file_paths

#socket connection image conversion.
class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)

def img_diff():
 
    ##accessing the files.
    img_directory = os.path.dirname(str(__file__))+"\\Img\\"
    #img_list: calls function list_iter(img_directory), returns a list of str file paths
    img_list = list_iter(img_directory)

    #Loop through the list of img file paths in the given directory.
    for x in range(1,len(img_list),2):

        
        img1 = Image.open(img_directory+img_list[x-1])
        img2 = Image.open(img_directory+img_list[x])
        
        data1 = asarray(img1)
        data2 = asarray(img2)

        ##result is used for my if else statement that I use to determine if I should do
        ##any computa   tional transformation.
        result = np.subtract(data1,data2)

        if np.all((result==0))==True:
            #no difference was found between the images, just display the second image
            img2.show()
            
        if np.all((result==0))==False:
           
            diff = ImageChops.difference(img1, img2)
            
            ##we convert the diff into gray scale to reduce the color channel to one dimension
            opencvImg = cv2.cvtColor(np.array(diff),cv2.COLOR_RGB2GRAY)

            ##we calculate the mean and the standard deviation so that we can use it as a condition
            ##for the result variable.
            mean = np.mean(opencvImg)
            std = np.std(opencvImg)

            result = np.where(opencvImg<round(mean)+round(std),0,opencvImg)

            #microservice running in a process.
            p1 = subprocess.Popen(['python', os.path.dirname(str(__file__))+"\\microservice.py"])
            
            ##an extra write so you can see how to filtering works
            cv2.imwrite(os.path.dirname(str(__file__))+"\\Img\\"+'test'+str(x)+'.png', result)

            #socket connection initialized
            context = zmq.Context()
            socket = context.socket(zmq.REQ)
            socket.connect('tcp://localhost:2984')
            print("here")
            
            #sending images to microservice.
            socket.send_string(json.dumps(data2, cls=NumpyArrayEncoder))
            verification = socket.recv()
            print(verification)
            socket.send_string(json.dumps(result, cls=NumpyArrayEncoder))
            verification = socket.recv()
            print(verification)
            
            socket.send(b"expecting the final image now . . . ")
            final_image_json = json.loads(socket.recv())
            finalimage = asarray(final_image_json)
            socket.send(b"thank you for the final image!")
            cv2.imwrite(os.path.dirname(str(__file__))+"\\img\\"+'result'+str(x)+'.png', finalimage)

            rgb_color = cv2.imread(os.path.dirname(str(__file__))+"\\img\\"+'result'+str(x)+'.png')
            image_rgb = cv2.cvtColor(rgb_color, cv2.COLOR_BGR2RGB)

            #final write will save the image in the correct format.
            cv2.imwrite(os.path.dirname(str(__file__))+"\\img\\"+'result'+str(x)+'.png', image_rgb)   
            p1.kill()





























    
