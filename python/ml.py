import matplotlib
matplotlib.use('Agg')
import pylab
import matplotlib.pyplot as plt
from scipy import misc
from io import StringIO,BytesIO
import base64
import os
os.environ['PYTHON_EGG_CACHE'] = '/tmp'
import argparse
import numpy as np

if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("p1",help="trigger name")
    parser.add_argument("p2",help="filter")
    args = parser.parse_args()

def html_plot(x,y):
    plt.figure(figsize=(10,10))
    pylab.imshow(misc.imread('candidates_public/O1/G211117/G211117_100.png'))
    plt.axis('off')
    pngplot = BytesIO()
    pylab.savefig(pngplot, format='png')
    pylab.close()
    pngplot.seek(0)   
    data_url = base64.b64encode(pngplot.getvalue()).decode('utf-8').replace('\n', '')
    html = '<img alt="sample" src="data:image/png;base64,{0}">'.format(data_url)
    return html

def read(memo):
    return np.load(memo)

memo = read('/data02/padova/ML_data/memory/0_syang.clf')
trigger,num = args.p1,args.p2
html = html_plot(trigger,num)
print(html)
