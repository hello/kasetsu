from matplotlib.pyplot import *
import numpy as np
import sys
import json
import base64


def plot_2d(x,the_title):
    X,Y = np.meshgrid(range(x.shape[1]),range(x.shape[0]))

    print np.max(x),np.min(x)
    pcolormesh(Y.transpose(),X.transpose(),x.transpose())
    xlabel('time (15ms frames)')
    ylabel('mel bins') 
    title(the_title)
    show()


f = open(sys.argv[1],'r')

s = f.read()
f.close()
datas = s.split("}")

for data in datas:
    if len(data) <= 2:
        continue

    tmp = data + "}"
    jdata = json.loads(tmp)
    n = jdata['num_cols']
    bindata = base64.b64decode(jdata['payload'])
    x = np.fromstring(bindata,dtype=np.int8)
    istart = x.shape[0] % n
    x2 = x[istart::].reshape((x.shape[0]/n,n))
    plot_2d(x2,jdata['id'])
