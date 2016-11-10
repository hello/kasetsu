from matplotlib.pyplot import *
import numpy as np
from collections import defaultdict
import csv
from datetime import datetime
import matplotlib.dates as mdates

def plot_data(key,x):
    x = np.array(x)


    istart = 720
    iend = istart + 121

    if x.shape[0] < iend:
        return

    tr = range(istart,iend)
    t = x[tr,0]

    light = x[tr,1].astype(float)
    vol = x[tr,5].astype(float) / 1024.0 - 40.0
    mot = x[tr,6].astype(float)

    light[np.where(light < 0)] = 0.0
    vol[np.where(vol < 0)] = 0.0
    vol /= 10.0
    light = light * 256.0 / float(2 ** 16) + 1.0
    light = np.log(light) / np.log(2)

    clf()
    plot(t,light,t,vol,t,mot);
    xlabel('time')
    legend(['light','sound','motion'])
    title(key)
    filename = '%s.png' % key
    gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    grid('on')
    savefig(filename)

f = open('any_sleep_or_wake_2016-01-01.csv000','r')
reader=csv.reader(f)
data = defaultdict(list)
for line in reader:

    dt = datetime.strptime(line[1],'%Y-%m-%d %H:%M:%S')

    x = [dt]

    for i in range(2,len(line)):
        x.append(float(line[i]))

    data[line[0]].append(x)



for key in data:    
    plot_data(key,data[key])
    

