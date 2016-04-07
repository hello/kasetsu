#!/usr/bin/python
from matplotlib.pyplot import *
from keras.models import model_from_json
import sys
import raw_data

def get_data():
    labels_file = 'labels_sleep_2016-01-01_2016-03-02.csv000'
    raw_data_files = ['2016-01-04.csv000']

    return raw_data.load_data(raw_data_files,labels_file)

def dostuff():
    configdata = None
    with open(sys.argv[1] + '.json','r') as f:
        configdata= f.read()
    if configdata == None:
        print 'could not read config file'
        sys.exit(0)
        
    model = model_from_json(configdata)

    model.load_weights(sys.argv[1] + '.h5')

    print 'getting data...'
    data = get_data();

    dt = []
    for d in data:
        dt.append(len(d[0]))

    timesteps = np.median(dt)
    data_dim = len(d[0][0])
    nb_classes = len(d[1][0])

    data2 = []
    for d in data:
        if len(d[0]) == timesteps:
            data2.append(d)

    #concatenate all the classes
    xx = []
    ll = []
    for x,l in data2:
        xx.append(x)
        ll.append(l)

    xx = np.array(xx)
    ll = np.array(ll)

    print xx.shape
    print ll.shape

    print "found %d user-days" % len(data2)
    print "T=%d,N=%d,L=%d" % (timesteps,data_dim,nb_classes)

    p = model.predict(xx)

    for i in range(p.shape[0]):
        y = p[i]
        x = xx[i]
        l = ll[i]
        plot(y[:,1]*10.);plot(x); title('%d' % i)
        show()
        

if __name__ == '__main__':
    dostuff()
    
