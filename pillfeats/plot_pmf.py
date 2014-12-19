#!/usr/bin/python
from pylab import *
from numpy import *
import json
import sys

bar_width = 0.30
colors = ['b', 'g', 'r']
opacity = 0.4
names = ['pill energy', 'pill wake counts', 'light change']

def barplot_pmf(pmf, name):
    pmf = array(pmf)
    numstates = pmf.shape[0]
    alphabet_size = pmf.shape[1]
    idx = arange(alphabet_size)
    
    rects = []
    for i in xrange(numstates):
        bar(idx + bar_width*i, pmf[i],bar_width, color=colors[i])
    
    ylim([-0.01,1.0])
    title('probability mass function of ' + name)
    ylabel('probability')
    xlabel('log magnitude, quantized')
    legend(['not on bed', 'on bed, not sleeping', 'on bed, sleeping'])
    #show()
    savefig(name.replace(' ', '_') + '.png')
    close()
    
def process(filename):
    f = open(filename, 'r')
    hmm = json.load(f)
    f.close()
    
    print array(hmm['A'])
    
    obsmodels = hmm['obsmodels']
    for i in range(len(obsmodels)):
        m = obsmodels[i]
        print array(m)
        barplot_pmf(m, names[i])
        
    print array(hmm['pi'])
    
    
    
    
if __name__ == '__main__':
    set_printoptions(precision=3, suppress=True, threshold=np.nan)

    filename = sys.argv[1]
    
    process(filename)
