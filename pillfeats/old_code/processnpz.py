#!/usr/bin/python

from numpy import *
improt 
def get_accel_data_from_file(filename):
    data = load(filename)
    
    y1 = data['arr_0']
    y2 = data['arr_1']
    y3 = data['arr_2']
    
    y = vstack((y1, y2, y3))
    y = y.transpose()
    
    return y
    
    
    
