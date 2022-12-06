# import modules
from PIL import Image
from PIL import ImageChops
import numpy as np
from numpy import asarray
import cv2
import os
import zmq
import json
from json import JSONEncoder



##this is a directory traversal function, collects and returns all relevant
##paths for images in folder.
def list_iter(folder_dir):
    '''
    below is a list and for loop
    folder_dir = "path_to_images"

    return file_paths = ["img1.png","img2.png".....]
    '''
    
    file_paths = []
    for images in os.listdir(folder_dir):
 
        # check if the image ends with png
        if (images.endswith(".png")):
            file_paths.append(images)
            
    return file_paths

class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)


def img_diff():
    '''
    this function is directly called and will process all image pairs
    in a folder starting from 1 -> N entries of photos.
    will produce a final result that will write to the same image
    folder and store those images as resultx.png
    
    '''

    ##img_directory: this will need to have a file path that leads to where images are stored
    ##example file path: img_directory = "C:/Users/PRO/AppData/Local/Programs/Python/Python36/CS 361/Assignment 5/Img/"
    #img_directory = "c:/users/pro/appdata/local/programs/python/python36/cs 361/impement_micro/img/"

    img_directory = os.path.dirname(str(__file__))+"\\Img\\"

    ##img_list: calls function list_iter(img_directory), returns a list of str file paths ["user/file/path1","user/file/path2"....] 
    img_list = list_iter(img_directory)


    '''For loop traverses through img_list, the loop will step through the list 2 at a time,
        We want to work with 2 images at a time for comparison.

        
    '''
    for x in range(1,len(img_list),2):

        '''
            img1 = opencv_frame_x.png
            img2 = opencv_frame_x+1.png
            will will return as pill object
        '''
        
        img1 = Image.open(img_directory+img_list[x-1])
        img2 = Image.open(img_directory+img_list[x])
        
        '''
            data1 & data2 are PIL objects we will convert into numpy array objects.
            asarry = numpy function
        '''
        data1 = asarray(img1)
        data2 = asarray(img2)

        ##result is used for my if else statement that I use to determine if I should do
        ##any computational transformation.
        result = np.subtract(data1,data2)

        if np.all((result==0))==True:
            #no difference was found between the images, just display the second image
            img2.show()
            
        if np.all((result==0))==False:
            '''
                The numpy.all(result==0) function found that there is a differnece between the
                images. 

            
            varibale diff: contains the actual difference between the images as opposed to
            if there is a difference which is why we recompute the this by using img1 & img2

            '''
            diff = ImageChops.difference(img1, img2)
            
            ##we convert the diff into gray scale to reduce the color channel to one dimension
            opencvImg = cv2.cvtColor(np.array(diff),cv2.COLOR_RGB2GRAY)

            ##we calculate the mean and the standard deviation so that we can use it as a condition
            ##for the result variable.
            mean = np.mean(opencvImg)
            std = np.std(opencvImg)

            '''
                result is a numpy array that will go through opencvImg and search for values in the
                img that are less than the mean + the standard deviation because we want to remove all
                values to the left of are theoretical histogram. 
                
            '''
            result = np.where(opencvImg<round(mean)+round(std),0,opencvImg)



            #################connection code for microservice5
            #socket connection initialized
            context = zmq.Context()
            socket = context.socket(zmq.REQ)
            socket.connect('tcp://localhost:2984')
            print("here")
            
            #send the images
            socket.send_string(json.dumps(data2, cls=NumpyArrayEncoder))
            verification = socket.recv()
            print(verification)
            socket.send_string(json.dumps(result, cls=NumpyArrayEncoder))
            verification = socket.recv()
            print(verification)
            
            #receive the resultant
            socket.send(b"Expecting the final image now . . . ")
            final_image_json = json.loads(socket.recv())
            finalimage = asarray(final_image_json)
            socket.send(b"thank you for the final image!")
            cv2.imwrite(os.path.dirname(str(__file__))+"\\Img\\"+'test.png', finalimage)


img_diff()







