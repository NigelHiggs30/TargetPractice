import os

#exact file path to test.py
print( __file__)

##now lets get the parent directory
test = str(__file__)
print("parent:   ", os.path.dirname(str(__file__)))
