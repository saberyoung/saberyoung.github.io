description="> supervised machine learning function "
#########################################################################
import argparse
import os,glob,sys,time,datetime
import numpy as np
from sklearn.externals import joblib
from jd_calculator import datetime_to_jd
import matplotlib
matplotlib.use('Agg')
import pylab as pl
import matplotlib.pyplot as plt
from scipy import misc
from io import StringIO,BytesIO
import base64
os.environ['PYTHON_EGG_CACHE'] = '/tmp'


if __name__ == "__main__":
    start_time = time.time()
    parser = argparse.ArgumentParser(description=description,\
         formatter_class=argparse.ArgumentDefaultsHelpFormatter) 
    parser.add_argument("file",help='predict file')
    parser.add_argument("number",help='number') 
    parser.add_argument("-u","--usr",default='syang',help='usr for the memory')        
    parser.add_argument("--jd",dest="jd",help='memory from which jd to use')   
    args = parser.parse_args()

#########################################################################
def change_label(yy):
    if yy == 'real':return 'bogus'
    elif yy =='bogus':return 'real'
    else:sys.exit('wrong!')

def hist(prob,flag,ydiff):   
    pp = []
    for ii in range(len(prob)):pp.append(prob[ii][0])
    pp=np.array(pp)

    r_real = pp[np.where(flag=='real')]
    r_bogus = pp[np.where(flag=='bogus')]  

    plt.figure(1)
    plt.hist(r_real, 50, histtype='step', color='r', label='real')
#        plt.hist(pp, 50, histtype='step', color='g', label='all')   
    plt.hist(r_bogus, 50, histtype='step', color='k', label='bogus')   
#        plt.plot([ydiff,ydiff],[0,1200],'--')
    plt.legend(prop={'size': 10})
    plt.xlabel('Hypothesis')
    plt.ylabel('Frequency')   
    #   MDR,FPR
    return len(np.where(r_real>ydiff)[0])/len(np.where(flag=='real')[0]),\
        len(np.where(r_bogus<ydiff)[0])/len(np.where(flag=='bogus')[0])    

def counts_show(X,label,cmap1): 
    # 1
    sub1 = plt.subplot(1, 2, 1)
    _sub1 = sub1.imshow(X,cmap=cmap1,interpolation="nearest")
    cbar = plt.colorbar(_sub1,fraction=0.046,pad=0)
    sub1.set_xlabel('x pixel')
    sub1.set_ylabel('y pixel')
    
    # 2
    sub2 = plt.subplot(1, 2, 2)
    nn=0
    list1,list2 = [],[]
    for ii in X:
        for jj in ii:
            nn+=1
            list1.append(jj)
            list2.append(nn)
    sub2.plot(list2,list1,'y.-')
    sub2.set_xlabel('pixel')
    sub2.set_ylabel('normalized counts')

    plt.subplots_adjust(left=.1, wspace=0.45, top=0.9)
    sub1.set_title(label, fontsize=14, fontweight='bold')
    sub2.set_ylim(-2.,2.5) 

#####################################################################################

if __name__ == "__main__":       
   
    memodir = '/data02/padova/ML_data/memory/'
    _usr = args.usr
    _file = args.file

    # decide read memory
    if args.jd is None:        
        _clflist = glob.glob(memodir+'*'+_usr+'.clf')
        _clfdone = []
        for _clf in _clflist:
            if os.path.basename(_clf).split('_')[0].isdigit():
                _clfdone.append(int(os.path.basename(_clf).split('_')[0]))
        _clf = max(_clfdone)    
    elif args.jd.isdigit():
        _clf = int(args.jd)
    else:sys.exit('wrong jd!')

    memo_clf = memodir+str(_clf)+'_'+_usr+'.clf'        
    print(memo_clf,'chosen as memory!\n')
    if not os.path.exists(memo_clf):sys.exit('do ml_memory first')

    clf = joblib.load(memo_clf)        
    memo = np.load(_file)

    X_test = memo['X'].reshape(memo['X'].shape[0], -1)
    y_test = memo['y']

    print(X_test)
    sys.exit()

    y_pred = clf.predict(X_test)               
    y_prob = clf.predict_proba(X_test)       

    counts_show(X_test[_ii].reshape(20,20),_info,'hot')                  
