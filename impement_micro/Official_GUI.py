from asyncio import subprocess
from mimetypes import init
from re import L
import PySimpleGUI as sg
import os
import cv2
from PIL import Image
import difference_between_img
import glob

import subprocess

#home directory for imgs
img_directory =  os.path.dirname(str(__file__))+"\\Img\\"


# ----------- Create the 3 layouts this Window will display -----------
layout1 = [
        [sg.Text("OpenCV Demo", size=(60, 1), justification="center")],
        [sg.Image(filename="", key="-IMAGE-")],
        [sg.Button("Picture", size=(10, 1))],
        [sg.Text("Picture allows the user to snap a photo from camera feed")],
        [sg.Button("Difference", size=(10,1))],
        [sg.Text("Difference calculates the difference between two photos")],
        [sg.Button("Exit", size=(10, 1))],
    ]


file_list_column = [
    [
        sg.Text("Image Folder"),
        sg.In(size=(25, 1), enable_events=True, key="-FOLDER-"),
        sg.FolderBrowse(initial_folder=img_directory),
    ],
    [
        sg.Listbox(
            values=[], enable_events=True, size=(40, 20), key="-FILE LIST-"
        )
    ],
    [sg.Button("Display",size=(10,1))],
    [sg.Button("Clear",size=(10,1))]
]

# For now will only show the name of the file that was chosen
image_viewer_column = [
    
    [sg.Text(size=(40, 1), key="-TOUT-")],
    [sg.Image(key="-IMAGE-")],
]



layout2 = [
    [
        sg.Column(file_list_column),
        sg.VSeperator(),
        sg.Column(image_viewer_column)

    ]

]


# ----------- Create actual layout using Columns and a row of Buttons
layout = [[sg.Column(layout1, key='-COL1-'), sg.Column(layout2, visible=False, key='-COL2-')],
          [sg.Button('Cycle Layout'),sg.Text("Alternate between taking a picture and saved results")]]

window = sg.Window('Target Practice Demo', layout,location = (300,100))


layout = 1  # The currently visible layout
#camera feed
cap = cv2.VideoCapture(0)

img_counter = 0

while True:
    event, values = window.read(timeout=20)
    
    
    if event in (None, 'Exit'):
        break

    ret, frame = cap.read()
    #sg.popup_yes_no("Would you like an ")

    if event == "Picture":
        img_name = "opencv_frame_{}.png".format(img_counter)

        cv2.imwrite(img_directory+"/"+img_name, frame)
        print("{} written!".format(img_name))
        img_counter += 1
        
    if event=="-FOLDER-":
        folder = values["-FOLDER-"]
        try:
            file_list = os.listdir(folder)
        except:
            file_list = []

        fnames = [
            f
            for f in file_list
            if os.path.isfile(os.path.join(folder, f))
            and f.lower().endswith((".png", ".gif"))
        ]
        window["-FILE LIST-"].update(fnames)
        window["-TOUT-"].update("click Img link and Display to view or Clear to delete all")

        
        
    if event == "Display":
        try:
            filename = os.path.join(
                values["-FOLDER-"], values["-FILE LIST-"][0]
            )
            display_img = Image.open(filename)
            display_img.show()
            
        except:
            pass
        
    if event == "Difference":
        try:
            difference_between_img.img_diff()
            print("complete")
        except:
            pass

    if event == "Clear":
        user_event = sg.popup_yes_no('Delete all?')
        if user_event == "No":
            pass
        else:
            removing_files = glob.glob(img_directory+"/"+"*.png")
            for x in removing_files:
                os.remove(x)
        
        

    if event == 'Cycle Layout':
        window[f'-COL{layout}-'].update(visible=False)
        layout = layout + 1 if layout < 2 else 1
        window[f'-COL{layout}-'].update(visible=True)
        window["-TOUT-"].update("""By pressing Browse users can open local Img folder.""")
           
    imgbytes = cv2.imencode(".png", frame)[1].tobytes()
    window["-IMAGE-"].update(data=imgbytes)


    
window.close()


















