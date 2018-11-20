import glob,os,sys
from astropy.io import fits as pyfits
import matplotlib.pyplot as plt
import pylab as pl
import numpy as np
from scipy import misc
from matplotlib import image

def log_trans(matrix):
    matrix = np.array(matrix)
    _mean = np.mean([np.mean(x) for x in matrix])
    matrix = matrix - _mean
    sigma = np.std(matrix)
    abs_matrix = abs(matrix)
    norm_matrix = matrix/abs_matrix*np.log(1+abs_matrix/sigma)
    return np.nan_to_num(norm_matrix)

def show_one(n,img,label,nstamp):    
    if n==0:n=nstamp**2
    step  =  1/float(nstamp)    
    xsize,ysize = step,step
    plt.subplots_adjust(wspace=0.0001,hspace=0.0001,bottom=.01,top=0.99,\
               left=0.01,right=0.99)
    plt.subplot(nstamp, nstamp, n) 
    imgshow = plt.imshow(img,cmap=plt.cm.gray_r)
    plt.text(1,6,label,color='red')
    frame1 = plt.gca()
    frame1.axes.get_xaxis().set_visible(False)
    frame1.axes.get_yaxis().set_visible(False)
        
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

# DLT40
dchos,fchos = 'unprocess/G184098/G184098',90
nstamp = 10
showone=False
web = False

_f = np.load(dchos+'_r_full.npz')
_imglist,_flaglist = _f['image3'],_f['ranking']
_index = np.where(_flaglist==fchos)[0]
input(len(_index))
#if not web:_w = open('eyeball_result/'+str(dchos)+'_eyeball.asc','a')

flag = {}
flag['X']=[]
flag['y']=[]

pl.ion()
plt.figure(figsize=(10,10))
if False:
    plt.axes([.01,.01,.99,.99])
    for _image in glob.glob('stamps/'+str(dchos)+'_'+str(fchos)+'_*.png'):
        print(_image)
        pimg = image.imread(_image)
        plt.imshow(pimg)
        answ = input('..wrong?(split with space, e.g. 1 4 6 ...)')
        for ii in answ.split():
            _w.write(ii + '\n')
            plt.clf()
    sys.exit('done')

if showone:
    for _nn in range(len(_flaglist)):    
        _img = _imglist[_nn].reshape(20,20)
        _flag = _flaglist[_nn]
        _img1 = log_trans(_img)
        if False:
            counts_show(_img,_flag,'hot')
            input('...')
            plt.clf()
            counts_show(_img1,_flag,'hot')
            input('...')
            plt.clf()
        flag['X'].append(_img1)      
        print(_nn)
    for ii in _f.keys():
        if ii != 'X':flag[ii] = _f[ii]
    np.savez(str(dchos)+'_log.npz',**flag)
    sys.exit('Done')

for _num,_nn in enumerate(_index):    
    _img = _imglist[_nn].reshape(20,20)
    _flag = _flaglist[_nn]
#    _mag = _f['mag'][_nn]
    _info = str(_nn)#+' '+str(_mag)
    show_one(np.mod(_num+1,nstamp**2),_img,_info,nstamp)
    if np.mod(_num+1,nstamp**2)==0 or _num+1==len(_index):
        if web:
            print(_num)
            plt.savefig('stamps/'+str(dchos)+'_'+str(fchos)+'_'+str(_num)+'.png')
            plt.clf()
        else:
            answ = input('..wrong?(split with space, e.g. 1 4 6 ...)')
            for ii in answ.split():
                _w.write(ii + '\n')
            plt.clf()
