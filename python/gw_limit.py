import matplotlib
matplotlib.use('Agg')
import pylab
from io import StringIO,BytesIO
import base64
import os
os.environ['PYTHON_EGG_CACHE'] = '/tmp'
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("p1",help="trigger name")
    parser.add_argument("p2",help="filter")
    args = parser.parse_args()

def html_plot(x,y):
    pylab.plot([x,x],[y,y],'.')
    pngplot = BytesIO()
    pylab.savefig(pngplot, format='png')
    pylab.close()
    pngplot.seek(0)   
    data_url = base64.b64encode(pngplot.getvalue()).decode('utf-8').replace('\n', '')
    html = '<img alt="sample" src="data:image/png;base64,{0}">'.format(data_url)
    return html

p1,p2 = args.p1,args.p2
html = html_plot(p1,p2)
print(html)
