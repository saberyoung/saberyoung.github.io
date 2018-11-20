description="> multishow "
#########################################################################

import argparse
import glob,os,sys,time,random
from astropy.io import fits as pyfits
from astropy.io import ascii
import matplotlib.pyplot as plt
import pylab as pl
import numpy as np
from astropy.table import Table, Column, vstack
import matplotlib.gridspec as gridspec

if __name__ == "__main__":
    start_time = time.time()
    parser = argparse.ArgumentParser(description=description,\
         formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("file",help='supervised target, npz')    
    parser.add_argument("-n", "--nstamp",dest="nstamp",default=10,
                        type=int,help='size of outplot')
    parser.add_argument("-w", "--web",action="store_true",
                dest='web',default=False,help='store images')
    parser.add_argument("--simbad",dest="simbad",action="store_true",
               default=False,help='')   
    parser.add_argument("--skybot",dest="skybot",action="store_true",
               default=False,help='')  
    parser.add_argument("--eyeball",dest="eyeball",action="store_true",
               default=False,help='')
    parser.add_argument("--eyeball2",dest="eyeball2",action="store_true",
               default=False,help='eyeball stefano')
    args = parser.parse_args()

def check_eye(n,Teye):     
    _index = np.where(Teye['num'] == n)
    _jd = ''
    for ii in _index[0]:
        _jd = Teye['judge'][ii]
    return _jd

def check_simbad(n,catalog,Tsimbad):     
    catone = {}
    for h in header:
        catone[h] = catalog[h][n-1]
    vdist = np.sqrt(((Tsimbad['ra']-catone['X_WORLD_1'])*\
                         np.cos(catone['Y_WORLD_1']*np.pi/180.))**2+\
                        (Tsimbad['dec']-catone['Y_WORLD_1'])**2)*3600.
    ii = np.where(vdist<3.)
    if len(ii[0])>0:
        for i in ii[0]:
            lsimbad ="SIMBAD: vtype=%s dist=%.2f" % \
                (Tsimbad['type'][i],vdist[i])
            print(catone['X_WORLD_1'],catone['Y_WORLD_1'],Tsimbad['ra'][i],Tsimbad['dec'][i],lsimbad)
            return Tsimbad['type'][i]
    return None

def check_skybot(n,catalog,Tskybot):   
    catone = {}
    for h in header:
        catone[h] = catalog[h][n-1]
    sdist = np.sqrt(((Tskybot['ra']-catone['X_WORLD_1'])*\
                      np.cos(catone['Y_WORLD_1']*np.pi/180.))**2+\
                     (Tskybot['dec']-catone['Y_WORLD_1'])**2)*3600.  
    ii = np.argmin(sdist)
    if sdist[ii]<10:
        lskybot ="SKYBOT: {} {} {:.1f}".format(Tskybot['name'][ii],
                                         Tskybot['mag'][ii],sdist[ii])
        print(catone['X_WORLD_1'],catone['Y_WORLD_1'],Tskybot['ra'][ii],Tskybot['dec'][ii],lskybot)
        return Tskybot['name'][ii]
    return None

def check_eye_st(n,catalog,Teye):     
    catone = {}
    for h in header:
        catone[h] = catalog[h][n-1]
    edist = np.sqrt(((Teye['ra']-catone['X_WORLD_1'])*\
                      np.cos(catone['Y_WORLD_1']*np.pi/180.))**2+\
                     (Teye['dec']-catone['Y_WORLD_1'])**2)*3600.  
    ii = np.where(edist<3.)
    if len(ii[0])>0:
        for i in ii[0]:
            leye ="Stefano list: vtype=%s dist=%.2f" % \
                (Teye['ID'][i],edist[i])
            print(catone['X_WORLD_1'],catone['Y_WORLD_1'],Teye['ra'][i],Teye['dec'][i],leye)
            return Teye['ID'][i]
    return None

nstamp = args.nstamp
web = args.web
_storesimbad = args.simbad
_storeskybot = args.skybot
_storeeyeball = args.eyeball
_storeeyeball2 = args.eyeball2

trigger = os.path.basename(args.file).split('_')[0]

if 'full' in args.file:
    _f = np.load(args.file)
    _imglist1,_imglist2,_imglist3,_flaglist = _f['image1'],\
        _f['image2'],_f['image3'],_f['ranking']
    _index = range(len(_imglist1))

    if False:
        _numsimbad = np.load(args.file.replace('full','simbad'))['num']
        _numskybot = np.load(args.file.replace('full','skybot'))['num']
        _tsimbad = np.load(args.file.replace('full','simbad'))['type']
        _tskybot = np.load(args.file.replace('full','skybot'))['type']

elif 'simbad' in args.file:
    _f = np.load(args.file)
    _numlist = _f['num']
    _f = np.load(args.file.replace('simbad','full'))
    _imglist1,_imglist2,_imglist3,_flaglist = _f['image1'],\
        _f['image2'],_f['image3'],_f['ranking']
    _index = _numlist

elif 'skybot' in args.file:
    _f = np.load(args.file)
    _numlist = _f['num']
    _f = np.load(args.file.replace('skybot','full'))
    _imglist1,_imglist2,_imglist3,_flaglist = _f['image1'],\
        _f['image2'],_f['image3'],_f['ranking']
    _index = _numlist

else:sys.exit('##########')

#
if _storesimbad:
    fsimbad = '/home/gwpadova/data02/ML_data/npz/eyeball/global_'+trigger+'_r.simbad'
    if not os.path.exists(fsimbad):
        sys.exit("!!! WARNING: simbad source file not found !!!")
    Tsimbad = Table.read(fsimbad,names=['ra','dec','type','score','pointing'],format='ascii')  
    
#
if _storeskybot:
    fskybot = '/home/gwpadova/data02/ML_data/npz/eyeball/global_'+trigger+'_r.skybot'
    if not os.path.exists(fskybot):
        sys.exit("!!! WARNING: skybot source file not found !!!")
    Tskybot = Table.read(fskybot,names=['xx','name','ra','dec','yy','mag',
               'dist','zz'],exclude_names=['xx','yy','zz'],format='ascii',
                         delimiter='|')
    Tskybot['ra'] *= 15.

#
if _storeeyeball:
    _tmp = 'tmp.dat'
    _Teye1,_Teye2,_Teye3 = [],[],[]
    score = [30,60,90]  
    for _ss in score:
        feye =  '/home/gwpadova/data02/ML_data/npz/eyeball/G184098_selected_'+str(_ss)+'.asc'
        _Teye = Table.read(feye,names=['num','score','judge'],format='ascii')  
        for _ii in range(len(_Teye['num'])):
            _Teye1.append(_Teye['num'][_ii])
            _Teye2.append(_Teye['score'][_ii])
            _Teye3.append(_Teye['judge'][_ii])
    ascii.write([_Teye1, _Teye2, _Teye3], _tmp, names=['num', 'score', 'judge'])
    Teye = Table.read(_tmp,names=['num','score','judge'],format='ascii')  
    os.remove(_tmp)

if _storeeyeball2:
    feye =  '/home/gwpadova/data02/ML_data/npz/eyeball/all_'+str(trigger)+'.tab'
    Teye = Table.read(feye,names=['ID','ra','dec','pointing'],format='ascii')  


#
if trigger in ['G184098']:
    _dir = '/home/gwpadova/data02/PDdiff/'
else:
    _dir = '/home/gwpadova/data01/PDdiff/'
catalog = Table.read(_dir+trigger+'/global/global_'+trigger+'_r.fits')    
header = catalog.colnames
catalog.sort('Ranking')
catalog.reverse()

pl.ion()
fig = plt.figure(figsize=(10,10))
outer = gridspec.GridSpec(nstamp, nstamp, wspace=0.2, hspace=0.1)

if _storesimbad or _storeeyeball or _storeeyeball2 or _storeskybot:
    _X1,_y1,_z1 = [],[],[]
    _X2,_y2,_z2 = [],[],[]
    _X3,_y3,_z3 = [],[],[]

    _X1n,_y1n,_z1n = [],[],[]
    _X2n,_y2n,_z2n = [],[],[]
    _X3n,_y3n,_z3n = [],[],[]

# randomly 
#random.shuffle(_index)
_index = random.sample(_index,1000)

for _num,_nn in enumerate(_index):
    img1 = _imglist1[_nn]
    img2 = _imglist2[_nn]
    img3 = _imglist3[_nn]   
    info = str(_nn) 

    if False:       
        _cc = 0
        if _nn in _numsimbad:
            _cc+=1
            info += ('\n' + str(_tsimbad[np.where(_numsimbad==_nn)[0]]))
        if _nn in _numskybot:
            _cc+=2
            info += ('\n' + str(_tskybot[np.where(_numskybot==_nn)[0]]))

        if _cc == 0:
            _cmap = plt.cm.gray_r
            _color = 'k'
        elif _cc == 2:
            # skybot
            _cmap = 'hot'
            _color = 'orange'
        elif _cc == 1:
            # simbad
            _cmap = 'cool'
            _color = 'b'
        elif _cc == 3:
            _cmap = 'spring'
            _color = 'g'
        else:sys.exit(_cc)

    else:
        _cmap = 'hot'
        _color = 'k'

    if _storesimbad:       
        lsimbad = check_simbad(_nn,catalog,Tsimbad)
        if lsimbad is None:
            _X1n.append(img3)
            _y1n.append(_nn)
            _z1n.append(lsimbad)
        else:
            _X1.append(img3)
            _y1.append(_nn)
            _z1.append(lsimbad)
        info += (':' + str(lsimbad))

    if _storeskybot:       
        lskybot = check_skybot(_nn,catalog,Tskybot)
        if lskybot is None:
            _X2n.append(img3)
            _y2n.append(_nn)
            _z2n.append(lskybot)           
        else:
            _X2.append(img3)
            _y2.append(_nn)
            _z2.append(lskybot)
        info += ('\n '  + str(lskybot))

    if _storeeyeball2:       
        leye2 = check_eye_st(_nn,catalog,Teye)
        if leye2 is None:
            _X2n.append(img3)
            _y2n.append(_nn)
            _z2n.append(leye2)           
        else:
            _X2.append(img3)
            _y2.append(_nn)
            _z2.append(leye2)
        info += ('\n '  + str(leye2))

    if _storeeyeball:       
        leye = check_eye(_nn,Teye)
        if len(leye) > 0:
            _X3.append(img3)
            _y3.append(_nn)
            _z3.append(leye)
        else:
            _X3n.append(img3)
            _y3n.append(_nn)
            _z3n.append(leye)
        info += ('\n ' + str(leye))

#    continue

    step  =  1/float(nstamp)    
    xsize,ysize = step,step  

    inner = gridspec.GridSpecFromSubplotSpec(2, 2,
                   subplot_spec=outer[np.mod(_num,nstamp**2)], wspace=0, hspace=0)

    ax1 = plt.Subplot(fig, inner[0])     
    ax1.text(0,.7,info,color=_color,fontsize=8)
    fig.add_subplot(ax1)

    ax2 = plt.Subplot(fig, inner[1])      
    ax2.imshow(img3,cmap=_cmap)
    fig.add_subplot(ax2)

    ax3 = plt.Subplot(fig, inner[2])      
    ax3.imshow(img1,cmap=_cmap)
    fig.add_subplot(ax3)

    ax4 = plt.Subplot(fig, inner[3])      
    ax4.imshow(img2,cmap=_cmap)
    fig.add_subplot(ax4)
    
    ax1.axis('off')
    ax2.axes.get_xaxis().set_visible(False)
    ax2.axes.get_yaxis().set_visible(False) 
    ax3.axes.get_xaxis().set_visible(False)
    ax3.axes.get_yaxis().set_visible(False) 
    ax4.axes.get_xaxis().set_visible(False)
    ax4.axes.get_yaxis().set_visible(False)

    if np.mod(_num+1,nstamp**2)==0 or _num+1==len(_index):
        if web:
            print(_num+1)
            plt.savefig('stamps/'+str(trigger)+'_'+str(_num+1)+'.png')
            plt.clf()
        else:
            answ = input('..wrong?(split with space, e.g. 1 4 6 ...)')
            for ii in answ.split():
                _w.write(ii + '\n')
            plt.clf()

for _cls,_ss,_X,_y,_z in zip([_storesimbad,_storesimbad,_storeskybot,_storeskybot,_storeeyeball,_storeeyeball],\
                                 ['simbad','nosimbad','skybot','noskybot','eye','noeye'],\
                                 [_X1,_X1n,_X2,_X2n,_X3,_X3n],[_y1,_y1n,_y2,_y2n,_y3,_y3n],[_z1,_z1n,_z2,_z2n,_z3,_z3n]):
    if _cls:
        flag = {}
        flag['X'] = _X
        flag['num'] = _y
        flag['type'] = _z
        np.savez('tmp_'+_ss+'.npz',**flag)
