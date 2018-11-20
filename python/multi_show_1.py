import glob,os,sys
from astropy.io import fits as pyfits
import matplotlib.pyplot as plt
import pylab as pl
import numpy as np
from scipy import misc
from matplotlib import image

def log_trans(matrix):
#    matrix = np.array(matrix)
#    _mean = np.mean([np.mean(x) for x in matrix])
#    matrix = matrix - _mean
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

fchos = 30
nstamp = 10
showone=True
web = False

_f = np.load('unprocess/G211117/G211117_r_full.npz')

if False:
    _imglist1,_numlist,_flaglist = _f['X'],_f['num'],_f['type']
else:
    _imglist1,_imglist2,_imglist3,_flaglist = _f['image1'],\
        _f['image2'],_f['image3'],_f['ranking']

#_index = np.where(_flaglist==fchos)[0]
_index = range(len(_flaglist))

#input(len(_index))
#if not web:_w = open('eyeball_result/'+str(dchos)+'_eyeball.asc','a')

flag = {}
flag['X']=[]
flag['num']=[]
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
#    for _nn in range(len(_imglist1)):          
    for _nn in [5529]:
        _img1 = _imglist1[_nn]
        _img2 = _imglist2[_nn]
        _img3 = _imglist3[_nn]

        _flag = _flaglist[_nn]
        _img11 = log_trans(_img1)
        _img22 = log_trans(_img2)
        _img33 = log_trans(_img3)

        if True:
            if True:
                plt.figure(0)
                plt1 = plt.subplot(1, 3, 1)
                plt1.imshow(_img1,cmap='hot',interpolation="nearest")
                plt1.set_xlabel('x pixel')
                plt1.set_ylabel('y pixel')

                plt2 = plt.subplot(1, 3, 2)
                plt2.imshow(_img2,cmap='hot',interpolation="nearest")
                plt2.set_xlabel('x pixel')
                plt2.set_ylabel('y pixel')
                
                plt3 = plt.subplot(1, 3, 3)
                plt3.imshow(_img3,cmap='hot',interpolation="nearest")
                plt3.set_xlabel('x pixel')
                plt3.set_ylabel('y pixel')
                input(_nn)
                plt.clf()

            plt.figure(1)
            counts_show(_img3,'','hot')
            input(_nn)
            plt.clf()
#            continue
#            counts_show(_img33,_flag,'hot')
#            input('2')
#            plt.clf()

        flag['X'].append(_img11)      
        print(_nn)
#    for ii in _f.keys():
#        if ii != 'X':flag[ii] = _f[ii]
    np.savez('tmp_log.npz',**flag)
    sys.exit('Done')

if False:
    _index = range(len(_imglist1))

for _num,_nn in enumerate(_index):    
    _img = _imglist1[_nn]
    _flag = _flaglist[_nn]
#    _n = _numlist[_nn]
    
    if True:
        _info = str(_flag)+' '+str(_nn)
    else:
        _info = str(_n)

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
