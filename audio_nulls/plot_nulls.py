#!/usr/bin/python

import numpy as np
from matplotlib.pyplot import *


def eval_func(r,hm,dh,x):
    dp2 = x*x + (hm+dh)*(hm+dh)
    k = 1.0 + dh / hm
    k2 = np.sqrt(r*r - hm*hm + 1e-10)
    the_eval = (1 + k*k) * r*r + 4 *hm * k*k2 - dp2
    the_deriv = 2 * (1 + k*k) * r + 4*k*r * hm / k2

    return the_eval,the_deriv

def get_distance_helper(r,hm,dh):
    k = 1.0 + dh / hm
    r1 = r * k
    return r1 + r

def get_distance(x,dh,hm):
 
    assert(x > hm)
    r = 10
    for i in range(20):
        y,J = eval_func(r,hm,dh,x)
        dr = -y/J
        r += dr

        if r < hm:
            r = hm
            

        if np.abs(y) < 1e-6:
            break

    assert (i < 20)

    
    return get_distance_helper(r,hm,dh)

if __name__ == '__main__':

    hmax = 0.5
    
    #height of mics
    hm = 0.05#meters

    #half wavelength of interest
    half_wavelength = 0.30/2#meters
    
    N = 100
    M = 5
    
    d = np.zeros((N,N))
    x1 = np.linspace(0.15,2.5,N)

    hs = np.linspace(0,hmax,M)
    ds = []
    for i2 in range(hs.shape[0]):
        d = []
        for i1 in range(x1.shape[0]):
            x = x1[i1]
            dh = hs[i2]
            distance = get_distance(x,dh,hm)
            d2 = hm + dh
            dp = np.sqrt((d2*d2 + x*x))
            d.append(dp + half_wavelength - distance)
        ds.append(d)
    
    plot(x1,np.array(ds).transpose()); xlabel('horizontal distance');
    grid('on')
    legend(hs)
    show()

