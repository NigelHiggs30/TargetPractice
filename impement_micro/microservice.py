import zmq
from PIL import Image
import numpy as np
import json
from numpy import asarray
import cv2 
import json
from json import JSONEncoder


class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)
    
def main():
    #while True:
    #initialize socket connection
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind('tcp://*:2984')

    #receive image data as numpy arrays converted into json
    #this is necessary so that it is condense enough to send through the socket
    secondimage_json = json.loads(socket.recv())
    secondimage = asarray(secondimage_json)
    socket.send(b"thank you for second image!")
    #print(secondimage.shape)
    
    diffarray_json = json.loads(socket.recv())
    #print(type(diffarray_json))
    
    diffarray = asarray(diffarray_json)
    
    

    socket.send(b"thank you for the difference!")
    
    
    #math that adds the difference to the original image
    
    diffthreshold = 0.09*np.max(secondimage)            #Threshold at which to highlight differences used to reduce noise; set to 9% of max.
    baseimage = secondimage.copy()                      #Sets the initial state of output image to the second image of the set 
    for rows in range(diffarray.shape[0]):              #Cycles through all rows in difference array
        for columns in range(diffarray.shape[1]):       #Cycles through all columns in difference array
            #print('row: ',rows, 'column: ', columns)   #Use to confirm indexing works
            if diffarray[rows,columns] > diffthreshold: #If pixel exceeds difference threshold output image is highlighted in that spot 
                baseimage[rows,columns,:] = 0           #Clears original data
                baseimage[rows,columns,1] = diffarray[rows,columns]*5  #Adds highlighted green data 
    output = baseimage  
    
    #send the output as a numpy array wrapped in json
    lets_go = socket.recv()
    print(lets_go)
    socket.send_string(json.dumps(output, cls=NumpyArrayEncoder))
    verification = socket.recv()
 
    
    
if __name__ == "__main__":
    main()