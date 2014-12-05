#!/usr/bin/python

from matplotlib import pyplot
import pylab
from mpl_toolkits.mplot3d import Axes3D

def plot3(a,b,c,mark='o',col='r'):

  pylab.ion()
  fig = pylab.figure()
  ax = Axes3D(fig)
  ax.scatter(a, b, c,marker=mark,color=col)
