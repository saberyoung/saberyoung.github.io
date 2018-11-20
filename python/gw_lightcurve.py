description="Measure accurate light curve for one object"
#########################################################################
import matplotlib
matplotlib.use('Agg')
import pylab
from io import StringIO,BytesIO
import base64
import os,sys,glob,shutil,time
os.environ['PYTHON_EGG_CACHE'] = '/tmp'
os.environ['HOME'] = '/tmp'

import subprocess
import argparse
import numpy as np
from astropy.io import fits
from astropy.table import Table

from stsci.tools import capable
capable.OF_GRAPHICS = False
from pyraf import iraf

import zscale
import sqlconn

import gw

optlist = gw.read_default()
#--------------------------------------------------------------------
wsize = 25
fixedap = 15
bkg_par = '3.,5.,2,2'

#optlist['hotpants']['nrx'] = '1'
#optlist['hotpants']['nry'] = '1'
#optlist['hotpants']['nsx'] = '11'
#optlist['hotpants']['nsy'] = '11'
#optlist['hotpants']['ko'] = '0'
#--------------------------------------------------------------------

iraf.noao(_doprint=0)
iraf.obsutil(_doprint=0)
iraf.digiphot(_doprint=0)
iraf.daophot(_doprint=0)

if __name__ == "__main__":
    start_time = time.time()

    parser = argparse.ArgumentParser(description=description,\
         formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("trigger",help="trigger name")
    parser.add_argument("filter",help="filter",choices=["g","r","i"])
    parser.add_argument("-p","--pointing",dest="pointing",
                        help='pointing number')
    parser.add_argument("coo",\
      help="candidate number or coordinates (hh:mm:ss or deg or _x,_y  pixels)")
    parser.add_argument("-n", "--nomask",dest="nomask",action="store_true",\
           default=False,help='Do not use bad pixel mask in hotpants')
    parser.add_argument("--size",dest="size",type=int,\
           default=1500,help='image section size')
    parser.add_argument("-s", "--snrlim",dest="snrlim",default=2.5,
           type=float,help='S/N threshold for limit')
    parser.add_argument("--recenter",action="store_true",\
            dest='recenter',default=False,help='recentering')
    parser.add_argument("-r",dest='reflist',help="reference association:"+
          " l-ate,e-arly [l]",choices=['l','e'])
    parser.add_argument("-x", "--xtasks",dest='xtasks',default='tdspfl',
         help='run t-rim, d-iff, s-how img, p-sf, f-it, l-ight curve')
    parser.add_argument("-v", "--verbose",dest="verbose",action="store_true",\
           default=False,help='Enable task progress report')

    args = parser.parse_args()


######################                     copy section
def trim_image(datain,dataou,trigger,filtro,pointing,dnew,trim_sect,tmp_dir,\
                    bpm,verbose): 
   
    print('    Trimming '+dnew)
    fdir_n = datain+trigger+'/'+dnew+'/'
    fdir_r = dataou+trigger+'/'+dnew+'/'
    if trigger == 'GW170814':
        fnew = '_'.join(['G297595','VST',filtro,dnew.replace('-',''),'gw',pointing])
    else:
        fnew = '_'.join([trigger,'VST',filtro,dnew.replace('-',''),pointing])
    infile = fdir_n+fnew
    outfile = '_'.join([tmp_dir,filtro,pointing,dnew])
    iraf.delete(outfile+'*.fits',verify=False)      
#    iraf.imcopy(infile+trim_sect,outfile,verbose=verbose)
    os.system('imcopy '+infile+'.fits'+trim_sect+' '+outfile+'.fits')  
    if bpm:
        bfile = fdir_r+'_'.join([trigger,'VST',filtro,dnew.replace('-',''),'gw',pointing])+'.bpm'
#        iraf.imcopy(bfile+trim_sect,outfile+'.bpm',verbose=verbose)
        os.system('imcopy '+bfile+'.fits'+trim_sect+' '+outfile+'.bpm.fits')  

def gw_diff(dnew,dref,filtro,pointing,seeing,optlist,nomask,tmp_dir,
                verbose):
    
    print('    Difference '+dnew+' - '+dref)

    max_seeing = max(seeing[dnew],seeing[dref])
    max_fwhm = max_seeing/float(optlist['global']['pixel_scale'] )
    return
    # hotpants parameters
    tuthresh = float(optlist['global']['satur_level'])  
                               # upper valid data count, template 
    tucthresh = tuthresh*0.9 # upper valid data count for kernel, template 
    iuthresh = tuthresh        # upper valid data count, image
    iucthresh = tucthresh      # upper valid data count for kernel, image 
    return
    rkernel = int(1.5*max_fwhm)# convolution kernel half width 
    rkernel = max(7,rkernel)   #       minimum
    rkernel = min(15,rkernel)  #       maximum
    radius = int(2.0*max_fwhm) # HW substamp to extract around each centroid 
    radius = max(10,radius)    #       minimum
    radius = min(20,radius)    #       maximum
    return
    sconv = '1'                # all regions convolved in same direction (0)
    normalize = 't'     #normalize to (t)emplate, (i)mage, or (u)nconvolved (t)

    fnew = '_'.join([tmp_dir,filtro,pointing,dnew])
    fref = '_'.join([tmp_dir,filtro,pointing,dref])
    fdiff = '_'.join([tmp_dir,filtro,pointing,'diff',dnew])
    if os.path.exists(fdiff+'.fits'): os.remove(fdiff+'.fits')
    iraf.delete('_conv.fit?',verify=False)
    if seeing[dnew] < seeing[dref]: 
        conv = ' -oci '+'_'.join([tmp_dir,filtro,pointing,dnew,'conv.fits'])
    else: conv = ''
    if nomask: mm = ""
    else: mm= " -imi "+fnew+".bpm.fits -tmi "+fref+".bpm.fits"
    return
    hotpants = "hotpants -inim "+fnew+".fits -tmplim "+fref+".fits"+mm+\
       ' -outim '+fdiff+'.fits '+\
      " -omi "+fdiff+".bpm"+".fits"+\
      ' -nrx '+optlist['hotpants']['nrx']+' -nry '+optlist['hotpants']['nry']+\
      ' -nsx '+optlist['hotpants']['nsx']+' -nsy '+optlist['hotpants']['nsy']+\
      ' -ko '+optlist['hotpants']['ko']+\
      ' -bgo '+optlist['hotpants']['bgo']+\
      ' -r '+str(rkernel)+' -rss '+str(radius)+\
      ' -tu '+str(tuthresh)+' -tuk '+str(tucthresh)+\
      " -tl -150 -il -150 "+\
      ' -iu '+str(iuthresh)+' -iuk '+str(iucthresh)+\
      ' -sconv -n '+normalize+conv

    if verbose: print(hotpants)
    pid = subprocess.Popen(hotpants,shell=True,stdout=subprocess.PIPE,\
                               stderr=subprocess.PIPE)
    
    output,error = pid.communicate()
    if verbose: print(output,error)

    pid = subprocess.Popen("modhead "+fdiff+".fits FWHM "+\
               str(max_seeing),shell=True,stdout=subprocess.PIPE) 
    output,error = pid.communicate()
    if error: print(error)

##########################################################################

def read_data(datain,dataou,trigger,filtro,_coo,reflist,\
                  size,verbose):
                                                         # read observations
#    filelist = dataou+trigger+'/'+trigger+'_'+filtro+'.reflist'
#    if not os.path.exists(filelist):
#        print('!!! ERROR: file',filelist,'not found !!!')
#        sys.exit()       

    if not reflist: reflist='l'
    if ',' not in _coo:
        tab = Table.read(dataou+trigger+'/global/global_'+trigger+"_"+\
                         filtro+'.fits',format='fits')
        tab.sort('Ranking')
        tab.reverse()  
       
        nn = int(_coo)-1
        sncoo = [tab['X_WORLD_1'][nn],tab['Y_WORLD_1'][nn]]
        snpix = [tab['X_IMAGE_1'][nn],tab['Y_IMAGE_1'][nn]]
        pointing = str(int(tab['ra'][nn]))+'_'+str(int(tab['dec'][nn]))
        search = tab['search'][nn]
        print('>>> {} {} n={} x={:.1f} y={:.1f} p={} search={}'.format(trigger,
              filtro,_coo,snpix[0],snpix[1],pointing,search))

        if search=='N': reflist='e'
        else: reflist = 'l'

    dlist = []
    # all_list
    command = ["select * from difflist_"+trigger]      
    data1 = sqlconn.query(command,sqlconn.conn)
    all_list = {}  
    for r in data1: 
        epochlist = []       
        for rr in range(len(r)):
            if 'epoch' in list(r.keys())[rr]:
                try:
                    epochlist.append(r[list(r.keys())[rr]].split('/')[4]) 
                except:pass   
        dnlist,d_ref = sorted(epochlist)[:-1],sorted(epochlist)[-1]      
        for dnew in dnlist:
            _p,_d,_r = str(r['ra0'])+'_'+str(r['dec0']),dnew,d_ref
            if _p not in all_list: all_list[_p] = {}
            all_list[_p][_d] = _r

    for ddd in all_list[pointing].keys():dlist.append(ddd)
 
#    ff = open(filelist)
#    righe = ff.readlines()
#    for r in righe:
#        _p,_d,_r = r.split()[0],r.split()[1],r.split()[5]
#        if _p ==  pointing: 
#            dlist.append(_d)
#            _dref = _r
    dlist.sort()
    kklist = []
    for ddd in all_list[pointing].values():kklist.append(ddd)
    _dref = kklist[0]

    if reflist =='l': dref = _dref
    elif reflist == 'e':
        dref = dlist[0]
        dlist = dlist[1:]+[_dref]
  
    fdir_n = datain+trigger+'/'+dref+'/'
    if trigger == 'GW170814':
        fref = '_'.join(['G297595','VST',filtro,dref.replace('-',''),'gw',pointing])
    else:
        fref = '_'.join([trigger,'VST',filtro,dref.replace('-',''),pointing])
    infile = fdir_n+fref    
                                    # convert coordinates depending on format  
    if ',' in _coo:
        coo = [_coo.split(',')[0], _coo.split(',')[1]]
        if '_' == coo[0][0]: 
            snpix = [float(coo[0][1:]),float(coo[1][1:])]
            _radec = iraf.wcsctran(input="STDIN",output="STDOUT",\
                 Stdin=[str(snpix[0])+' '+str(snpix[1])],Stdout=1,image=infile,\
                 inwcs='logical',outwcs='world',column="1 2",\
                 format="%12.3H %12.3")[3:]
            radec = _redec[0].split()
            sncoo = [iraf.real(radec[0])*15,iraf.real(radec[1])]
        else:
            if ':' in coo[0]:
                sncoo = [iraf.real(coo[0])*15.,iraf.real(coo[1])]
                _pixcoo = iraf.wcsctran(input="STDIN",output="STDOUT",\
                 Stdin=[str(sncoo[0])+' '+str(sncoo[1])],Stdout=1,image=infile,\
                 inwcs='world',outwcs='logical',column="1 2",\
                 units="degrees degrees")[3:]
                pixcoo = _pixcoo[0].split()
                snpix = [float(pixcoo[0]),float(pixcoo[1])]
  
    xc,yc = snpix[0],snpix[1]
    hdr = fits.getheader(infile+'.fits')
    xdim,ydim = hdr['NAXIS1'],hdr['NAXIS2']
    mjd = {dref:(hdr['MJDSTART']+hdr['MJDEND'])/2.}
    seeing = {dref:hdr['FWHM']}

    x1,x2 = int(xc-size/2.),int(xc+size/2.)
    y1,y2 = int(yc-size/2.),int(yc+size/2.)

    if x1<1: x1,x2 = 1,size
    if y1<1: y1,y2 = 1,size
    if x2>xdim-1: x1,x2 = xdim-size-1,xdim-1
    if y2>ydim-1: y1,y2 = ydim-size-1,ydim-1

    xycoo = [snpix[0]-x1+1,snpix[1]-y1+1]

    trim_sect='['+str(x1)+':'+str(x2)+','+str(y1)+':'+str(y2)+']'

    print(' SN:  ra={:.9f} dec={:.9f} pix x={:.1f} y={:.1f}'.format(sncoo[0],\
         sncoo[1],snpix[0],snpix[1]))
    print("    trim=",trim_sect)

    for dnew in dlist:
        fdir_n = datain+trigger+'/'+dnew+'/'
        if trigger =='GW170814':
            fnew = '_'.join(['G297595','VST',filtro,dnew.replace('-',''),'gw',pointing])
        else:
            fnew = '_'.join([trigger,'VST',filtro,dnew.replace('-',''),pointing])
        infile = fdir_n+fnew    
        hdr = fits.getheader(infile+'.fits')
        mjd[dnew] = (hdr['MJDSTART']+hdr['MJDEND'])/2.
        seeing[dnew] = hdr['FWHM']

    return reflist,pointing,sncoo,snpix,xycoo,dlist,dref,mjd,seeing,trim_sect

    ###########

def show_one_diff(img,xcoo,ycoo,wsize,dnew,color):

    imgnew = fits.open(img+'.fits')
    x1,x2 = int(xcoo-wsize),int(xcoo+wsize)
    y1,y2 = int(ycoo-wsize),int(ycoo+wsize)
    img = imgnew[0].section[y1:y2,x1:x2]
    z1,z2 = zscale.zscale(img)
    imgshow = pylab.imshow(img[::-1],cmap=pylab.cm.gray_r,vmin=z1,vmax=z2)
    if dnew: pylab.text(1,wsize*2-1,dnew,color=color)

def show_all_diff(dlist,dref,filtro,pointing,xycoo,trim_sect,tmp_dir,
                  reflist,full,verbose):
    
    if full: k = 2
    else: k = 4
    n = len(dlist)+1
    pylab.ion()
    pylab.figure(figsize=(1.5*n,1.5*k))
    pylab.subplots_adjust(wspace=0.0001,hspace=0.0001,bottom=.1,top=0.95,\
               left=0.1,right=0.98)

    istart = 0
    for d in sorted(dlist+[dref]):
        istart += 1
        pylab.subplot(k,n,istart)
        img =  '_'.join([tmp_dir,filtro,pointing,d])
        show_one_diff(img,xycoo[0],xycoo[1],wsize,d,'k')
        frame1 = pylab.gca()
        frame1.axes.get_xaxis().set_visible(False)
        frame1.axes.get_yaxis().set_visible(False)

    if reflist=='e': istart+=1
    for dnew in sorted(dlist):
        istart += 1
        pylab.subplot(k,n,istart)
        dimg =  '_'.join([tmp_dir,filtro,pointing,'diff',dnew])
        show_one_diff(dimg,xycoo[0],xycoo[1],wsize,"",'k')
        frame1 = pylab.gca()
        frame1.axes.get_xaxis().set_visible(False)
        frame1.axes.get_yaxis().set_visible(False)
        
    if full: input('...')

def make_psf(filtro,pointing,dlist,dref,seeing,xycoo,size,tmp_dir,
             verbose):

    for dnew in dlist:
        maxseeing = max(seeing[dnew],seeing[dref])
        dimg = '_'.join([tmp_dir,filtro,pointing,dnew])

        apcor = gw_snoopy.gw_psf(pointing,dnew,dimg,xycoo[0],xycoo[1],
                 seeing[dnew],5.,10,size,size,optlist,verbose)
        iraf.hedit(dimg+".psf",'apcor',apcor,add=True,verify=False,\
                           show=verbose) 
        print ('>>> made psf for epoch',dnew) 

        #if verbose:
        #    iraf.delete('_psf.fit?',verify=False)
        #    iraf.seepsf(dimg+'.psf','_psf.psf')
        #    iraf.surface('_psf.psf')
        #    raw_input('>>>   return to next .....')
        if os.path.exists(dimg+"_conv.fits"):
            dimg = dimg+"_conv"
            apcor = gw_snoopy.gw_psf(pointing,dnew,dimg,xycoo[0],xycoo[1],
                 maxseeing,5.,10,size,size,optlist,verbose)
            
            iraf.hedit(dimg+".psf",'apcor',apcor,add=True,verify=False,\
                           show=verbose) 
            print ('>>> made psf for epoch',dnew,'convolved') 

        fdiff = '_'.join([tmp_dir,filtro,pointing,'diff',dnew])
        shutil.copy(dimg+".psf.fits",fdiff+'.psf.fits')


    dimg = '_'.join([tmp_dir,filtro,pointing,dref])
    apcor = gw_snoopy.gw_psf(pointing,dref,dimg,xycoo[0],xycoo[1],
                seeing[dref],5.,10,size,size,optlist,verbose)

    #if verbose:
    #    iraf.delete('_psf.fit?',verify=False)
    #    iraf.seepsf(dimg+'.psf','_psf.psf')
    #    iraf.surface('_psf.psf')
    #    raw_input('>>>   return to next .....')

    iraf.hedit(dimg+".psf",'apcor',apcor,add=True,verify=False,\
                           show=verbose) 
    print ('>>> made psf for epoch',dref)
 
def fit_psf(trigger,filtro,pointing,coo,dlist,dref,seeing,mjd,xycoo,snrlim,
       recenter,size,tmp_dir,verbose):

    print('date         jd      magsource    '+\
             '  magsdiff        magfit      SNR')        
    gg = open(tmp_dir+trigger+'_'+filtro+"_"+pointing+"_"+str(coo)+'.lc','w')
    gg.write('# date      jd         xc       yc      magsource     '+\
                     '  magsdiff    magfit        SNR \n')

    for dnew in dlist:
        maxseeing = max(seeing[dnew],seeing[dref])
        dimg = '_'.join([tmp_dir,filtro,pointing,'diff',dnew])
            # aperture and psf fit measure on difference 
        hdr = fits.getheader(dimg+".psf.fits")
        apcor = hdr['apcor']        
        snres = gw_snoopy.gw_sn(dimg,xycoo[0],xycoo[1],maxseeing,\
                snrlim,recenter,bkg_par,apcor,optlist,verbose)

        print(' %s %9.3f' % (dnew,mjd[dnew]),end='')
        for m in 'opf':
            print(' %7s %5s' % (snres['mag'+m],snres['merr'+m]),end='')
        print(' '+snres['snr'])

        gg.write(' %s %9.3f' % (dnew,mjd[dnew]))
        for m in 'opf':
            gg.write(' %7s %5s' % (snres['mag'+m],snres['merr'+m]))
        gg.write(' '+snres['snr']+'\n')
        if verbose: raw_input('psf fit on '+dnew)
        time.sleep(1)  # wait for some subprocess to complete ?????

    print('#original   '+60*'-')
    gg.write('#original   '+60*'-'+'\n')
    for dnew in dlist+[dref]:
        fimg = '_'.join([tmp_dir,filtro,pointing,dnew])
        hdr = fits.getheader(fimg+".psf.fits")
        apcor = hdr['apcor']        
        snres = gw_snoopy.gw_sn(fimg,xycoo[0],xycoo[1],seeing[dref],\
               snrlim,recenter,bkg_par,apcor,optlist,verbose)

        print(' %s %9.3f' % (dref,mjd[dnew]),end='')
        for m in 'opf':
            print(' %7s %5s' % (snres['mag'+m],snres['merr'+m]),end='')
        print(' '+snres['snr'])

        gg.write(' %s %9.3f' % (dref,mjd[dnew]))
        for m in 'opf':
            gg.write(' %7s %5s' % (snres['mag'+m],snres['merr'+m]))
        gg.write(' '+snres['snr']+ '\n')
    gg.close()

def read_snlc(trigger,filtro,pointing,coo,tmp_dir):

    gg = open(tmp_dir+trigger+'_'+filtro+"_"+pointing+"_"+str(coo)+'.lc')
    righe = gg.readlines()
    dated,mjdd,magd,magerrd = [],[],{},{}
    dateo,mjdo,mago,magerro = [],[],{},{}

    for x in ['orig','diff','fit']:
        magd[x],magerrd[x] = [],[]
        mago[x],magerro[x] = [],[]

    for i,r in enumerate(righe):
        if 'original' in r: 
            ii = i
            break

    for r in righe[1:ii]:
        dated.append(r.split()[0])
        mjdd.append(float(r.split()[1]))
        for i,x in enumerate(['orig','diff','fit']):
            _mag,_merr = r.split()[2*i+2],r.split()[2*i+3]
            if _mag != "INDEF": _mag=float(_mag)
            if _merr != "INDEF": _merr=float(_merr)
            magd[x].append(_mag)
            magerrd[x].append(_merr)

    for r in righe[ii+1:]:
        dateo.append(r.split()[0])
        mjdo.append(float(r.split()[1]))
        for i,x in enumerate(['orig','diff','fit']):
            _mag,_merr = r.split()[2*i+2],r.split()[2*i+3]
            if _mag != "INDEF": _mag=float(_mag)
            if _merr != "INDEF": _merr=float(_merr)
            mago[x].append(_mag)
            magerro[x].append(_merr)

    mjdd,mjdo = np.array(mjdd),np.array(mjdo)
    for x in ['orig','diff','fit']:
        magd[x],magerrd[x] = np.array(magd[x]),np.array(magerrd[x])
        mago[x],magerro[x] = np.array(mago[x]),np.array(magerro[x])

    return dated,mjdd,magd,magerrd,dateo,mjdo,mago,magerro

def plot_lightcurve(trigger,filtro,pointing,sncoo,snpix,coo,tmp_dir,full):

    dated,mjdd,magd,magerrd,dateo,mjdo,mago,magerro = \
        read_snlc(trigger,filtro,pointing,coo,tmp_dir)

    pho =  mjdo-np.min(mjdo)
    phd =  mjdd-np.min(mjdo) 

    if full: pylab.ion()
    else:    pylab.subplot(212)

    ii = magerrd['fit']<999
    pylab.errorbar(phd[ii],magd['fit'][ii],\
          yerr=[magerrd['fit'][ii],magerrd['fit'][ii]],fmt='o',mfc='b',mec='b',\
                           label='diff')
    if False in ii.tolist():
        yerru = np.zeros(len(phd[np.invert(ii)]))
        yerrl = yerru-.3
        pylab.errorbar(phd[np.invert(ii)],magd['fit'][np.invert(ii)],\
                    yerr=[yerrl,yerru],ecolor='k',uplims=True,fmt='o',\
                    mec='b',mfc='b')  

    ii = magerro['fit']<999
    pylab.errorbar(pho[ii],mago['fit'][ii],\
          yerr=[magerro['fit'][ii],magerro['fit'][ii]],fmt='o',mfc='r',mec='r',\
                           label='orig')
    if False in ii.tolist():
        yerru = np.zeros(len(pho[np.invert(ii)]))
        yerrl = yerru-.3
        pylab.errorbar(pho[np.invert(ii)],mago['fit'][np.invert(ii)],\
                    yerr=[yerrl,yerru],ecolor='k',uplims=True,fmt='o',\
                    mec='r',mfc='r')  

#    pylab.legend(numpoints=1)
    pylab.ylim(np.max((np.max(mago['fit']),np.max(magd['fit'])))+.5,
               np.min((np.min(mago['fit']),np.min(magd['fit'])))-.5)
    pylab.xlim(-10,np.max(pho)+10)
    pylab.ylabel(filtro+' [abmag]')
    pylab.xlabel('phase [days]')
    if ',' not in coo: pylab.figtext(.1,.96,'n={}'.format(coo),fontsize=14)
    pylab.figtext(.25,.96,'{} {} {} ra={:.9f} dec={:.9f}'.format(trigger,filtro,pointing,sncoo[0],sncoo[1]),fontsize=14)

#    input('...')
#    gg = tmp_dir+trigger+'_'+filtro+"_"+pointing+"_"+str(coo)+'.png'
#    pylab.savefig(gg)

def light_curve(datain,dataou,trigger,filtro,coo,snrlim,recenter,
                reflist,xtasks,nomask,size,tmp_dir,verbose):
  
    reflist,pointing,sncoo,snpix,xycoo,dlist,dref,mjd,seeing,trim_sect =\
        read_data(datain,dataou,trigger,filtro,coo,reflist,size,verbose)

    if 's' in xtasks and 'l' in xtasks: full = False
    else: full = True

    if 't' in xtasks:                               # TRIM images #
        for dnew in dlist+[dref]:
            trim_image(datain,dataou,trigger,filtro,pointing,dnew,trim_sect,
                       tmp_dir,True,verbose) 
    if 'd' in xtasks:                          # compute DIFF  ##
        for dnew in dlist:
            gw_diff(dnew,dref,filtro,pointing,seeing,optlist,nomask,
                        tmp_dir,verbose)

    if 's' in xtasks: 
        show_all_diff(dlist,dref,filtro,pointing,xycoo,trim_sect,tmp_dir,
                  reflist,full,verbose)

    if 'p' in xtasks:                             # PSF ####
        make_psf(filtro,pointing,dlist,dref,seeing,xycoo,size,tmp_dir,
                 verbose)

    if 'f' in xtasks:                             # FIT  ###
        fit_psf(trigger,filtro,pointing,coo,dlist,dref,seeing,mjd,xycoo,
                snrlim,recenter,size,tmp_dir,verbose)

    if 'l' in xtasks:  # PLOT light curve  #############################
        plot_lightcurve(trigger,filtro,pointing,sncoo,snpix,coo,tmp_dir,full)

if __name__ == "__main__":

    datain = "/data01/VSTin/"
    dataou = "/data01/padova/PDdiff/"
 
    tmp_dir = './'
#    pylab.plot([1,1],[1,1],'o')
    light_curve(datain,dataou,args.trigger,args.filter,
         args.coo,args.snrlim,args.recenter,args.reflist,args.xtasks,
         args.nomask,args.size,tmp_dir,args.verbose)

    pngplot = BytesIO()
    pylab.savefig(pngplot, format='png')
    pylab.close()
    pngplot.seek(0)   
    data_url = base64.b64encode(pngplot.getvalue()).decode('utf-8').replace('\n', '')
    print('<img alt="sample" src="data:image/png;base64,{0}">'.format(data_url))

#    if  args.xtasks == 'tdspfl':
#        thrash = glob.glob('_*')
#        thrash += glob.glob('tmp*')
#        for t in thrash: os.remove(t)

#    print( "********** Completed in ",int(time.time()-start_time),"sec")
