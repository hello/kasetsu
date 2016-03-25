#!/usr/bin/python

import numpy as np
from matplotlib.pyplot import *
#max height to plot (so from hm to hmax)
hmax = 0.5

#max distnace to plot to (hm to xmax)
xmax = 2.5

#num distance ponts to plot    
N = 100

#num heights to plot
M = 5

#height of mics
hm = 0.010#meters

#wavelength of interest
wavelength = 0.30 #meters
    
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

    
    x1 = np.linspace(hm+0.01,xmax,N)

    hs = np.linspace(hmax/M,hmax,M)
    ds = []
    for i2 in range(hs.shape[0]):
        dplushalf = []
        for i1 in range(x1.shape[0]):
            x = x1[i1]
            dh = hs[i2]
            distance = get_distance(x,dh,hm)
            d2 = hm + dh
            dp = np.sqrt((d2*d2 + x*x))
            dplushalf.append(dp + 0.5*wavelength - distance)
        ds.append(dplushalf)
    
    plot(x1,np.array(ds).transpose()); 
    xlabel('horizontal distance');
    ylabel('primary + half  - secondary') 
    title('mic height=%g mm, zero-crossings mean nulls' % (hm * 1000.))
    grid('on')
    legend(['h=%g' % h  for h in hs.tolist()])
    ylim((-0.05,0.2))
    plot([0,xmax],[0,0],'k')
    show()

