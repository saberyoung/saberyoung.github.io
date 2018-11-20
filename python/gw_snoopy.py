description=">> New automated psf fir version tuned for gw"
################################################################
# EC 2012 Sep 12
################################################################
import os,sys,shutil,subprocess,glob
import time
import argparse
from numpy import *
from pyraf import iraf
from astropy.io import fits
from astropy.table import Table
import gw

if __name__ == "__main__":
    start_time = time.time()

    parser = argparse.ArgumentParser(description=description,\
         formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("img",help="image name")
    parser.add_argument("sncoo",help="SN coordinate (xpix,ypix)")
    parser.add_argument("-x", "--xtasks",dest='xtasks',default='pf',
         help='run p-sf, f-it')
    parser.add_argument("-t", "--threshold",dest="threshold",default=5.,
            type=float,help='Source detection threshold')
    parser.add_argument('-f','--fwhm',dest='fwhm',help='Seeing (FWHM [arcsec]')
    parser.add_argument("-p", "--psfstars",dest="psfstars",default=10,
            type=int,help='Maximum number of psf stars')
    parser.add_argument("-b", "--bkg_par",dest="bkg_par",default='3.,5.,2,2',\
           type=str,help='Bgk fit annulus (in,out) and order (x,y) ')
    parser.add_argument("-r", "--recenter",action="store_true",\
            dest='recenter',default=False,\
            help='Recentering')
    parser.add_argument("-s", "--snrlim",dest="snrlim",default=2.5,
           type=float,help='S/N threshold for limit')
    parser.add_argument("-v", "--verbose",dest="verbose",action="store_true",\
           default=False,help='Enable task progress report')

    args = parser.parse_args()    

iraf.noao(_doprint=0)
iraf.obsutil(_doprint=0)
iraf.digiphot(_doprint=0)
iraf.daophot(_doprint=0)

optlist = gw.read_default()
    
iraf.datapars.datamax = float(optlist['global']['satur_level'])
iraf.photpars.zmag = float(optlist['global']['mag_zeropoint'])

def psffit(_img,fwhm,psfstars,optlist,verbose):

    a1,a2,a3,a4,a5 = int(fwhm+0.5),int(fwhm*2+0.5),int(fwhm*3+0.5),\
        int(fwhm*4+0.5),int(fwhm*5+.5)
    iraf.fitskypars.annulus = a5
    iraf.fitskypars.dannulus = 20
    iraf.photpars.apertures = '%d,%d,%d'%(a3,a4,a5)
#    iraf.datapars.datamin =  0.

    iraf.delete('_psf.ma*,'+_img+'.psf.fit?,_psf.ps*,_psf.gr?,_psf.n*,\
             _psf.sub.fit?',verify=False)
    iraf.phot(_img,'_psf.coo','_psf.mag',interac=False,verify=False,\
                  verbose=False)

    iraf.daopars.psfrad = a4
    iraf.daopars.fitrad = a1
    iraf.daopars.fitsky = 'yes'
    iraf.daopars.sannulus = a4
    iraf.daopars.recenter = 'yes'
    iraf.daopars.varorder = 0
    
    iraf.pstselect(_img,'_psf.mag','_psf.pst',psfstars,interac=False,\
                           verify=False,verbose=verbose)

    iraf.psf(_img,'_psf.mag','_psf.pst',_img+'.psf','_psf.psto',\
                 '_psf.psg',interac=False,verify=False,verbose=False)
    iraf.group(_img,'_psf.mag',_img+'.psf','_psf.grp',verify=False,\
                   verbose=False)
    iraf.nstar(_img,'_psf.grp',_img+'.psf','_psf.nst','_psf.nrj',\
                   verify=False,verbose=False)

    photmag = iraf.txdump("_psf.mag",'xcenter,ycenter,id,mag,merr',\
                  expr='yes',Stdout=1)
    pst = iraf.txdump("_psf.pst",'xcenter,ycenter,id',expr='yes',Stdout=1)
    fitmag = iraf.txdump("_psf.nst",'xcenter,ycenter,id,mag,merr',\
                             expr='yes',Stdout=1)
    return photmag,pst,fitmag

def gw_psf(pointing,dnew,_img,xsn,ysn,seeing,threshold,psfstars,xdim,ydim,
           optlist,verbose):

    distance = 10
    fwhm = seeing/float(optlist['global']['pixel_scale'])

    cparam = gw.runsex(_img,seeing,optlist,threshold,'ascii',verbose,
                     'psf_'+pointing+'_'+dnew) 
    tab = {}
    for k in cparam: tab[k] = []

    csex = '_'.join(['tmp','psf',pointing,dnew])+'.cat'
    tab = Table.read(csex,format='ascii.sextractor')

    xs = tab['X_IMAGE']
    ys = tab['Y_IMAGE']
    magauto = tab['MAG_AUTO']
    fluxrad = tab['FLUX_RADIUS']
    dflux = fluxrad-median(fluxrad)
    fstar = compress(dflux<std(fluxrad),fluxrad)

    ff = open('tmp.cursor','w')
    for i in range(len(xs)):
       #print xs[i],ys[i],fluxrad[i],abs(fluxrad[i]*1.6-fwhm)/fwhm <.5
        dist = sqrt((xsn-xs[i])**2+(ysn-ys[i])**2) # not near SN
        _xs = delete(xs,i)
        _ys = delete(ys,i)
        dist2 = sqrt((_xs-xs[i])**2+(_ys-ys[i])**2)
                                                
        if abs(fluxrad[i]*1.6-fwhm)/fwhm <.5 and dist>distance*fwhm \
                 and min(dist2)>distance*fwhm:  # star, not near other object
            x1,x2 = int(xs[i]-fwhm*3),int(xs[i]+fwhm*3)
            y1,y2 = int(ys[i]-fwhm*3),int(ys[i]+fwhm*3)
            if x1<1: x1=1
            if y1<1: y1=1
            if x2>int(xdim): x2= int(xdim)
            if y2>int(ydim): y2= int(ydim)
            if magauto[i]+30>16.  :  # not saturated
                ff.write('%10.3f %10.3f 1 m \n' % (xs[i],ys[i]))
    ff.close()

    iraf.delete('tmp.lo?,tmp.sta?,tmp.gk?',verify=False)

    psfmout = iraf.psfmeasure(_img,imagecur='tmp.cursor',logfile='tmp.log',\
              radius=int(fwhm),iter=3,display=False,StdoutG='tmp.gki',Stdout=1)
    if verbose: 
        for p in psfmout: print(p)
        #outexa = iraf.imexam(img,1,logfile='tmp.log',imagecur='tmp.cursor',\
        #                     keeplog=True,use_display=False,Stdout=1)

    ff = open('tmp.log')
    righe = ff.readlines()
    xn = [float(righe[3].split()[1])]
    yn = [float(righe[3].split()[2])]
    _fw = [float(righe[3].split()[4])]
    for r in righe[4:-2]:
        if len(r)>0:
            xn.append(float(r.split()[0]))
            yn.append(float(r.split()[1]))
            _fw.append(float(r.split()[3]))
 
    if verbose:
        print('FWHM: ',righe[-1].split()[-1] )
        print(80*"#")
        print("Median FWHM %5.2f +/-%5.2f  nsource=%d " % \
                (median(_fw),std(_fw),len(_fw)) )  

    xns,yns,_fws = [xn[0]],[yn[0]],[_fw[0]]
    for i in range(1,len(xn)):       # eliminate double object identification
        if abs(xn[i]-xn[i-1]) >.2 and abs(yn[i]-yn[i-1])>.2:
            xns.append(xn[i])
            yns.append(yn[i])
            _fws.append(_fw[i])
    fw = []
    ff = open('_psf.coo','w')
    for i in range(len(xns)):
            #print '%10.3f %10.3f %7.2f %6.3f %5.2f' %  \
            #    (xn[i],yn[i],float(_fw[i]),fwhm,min(dist))
        if abs(_fws[i]-fwhm)/fwhm <.3:
            ff.write('%10.3f %10.3f %7.2f \n'%(xns[i],yns[i],float(_fws[i])))
            fw.append(_fws[i])
    ff.close()        ## End automatic selection

    if verbose:
        print(" Median FWHM %5.2f +/-%5.2f  nsource=%d  "\
            % (median(fw),std(fw),len(fw))   )
    fwhm = median(fw)

    photmag,pst,fitmag = psffit(_img,fwhm,psfstars,optlist,verbose)

    radec = iraf.wcsctran(input='STDIN',output='STDOUT',Stdin=photmag,\
         Stdout=1,image=_img,inwcs='logical',outwcs='world',columns="1 2",\
          format='%13.3H %12.2h',min_sig=9,mode='h')[3:]

    idpsf = []
    for i in range(len(pst)):
        idpsf.append(pst[i].split()[2])
    dmag = []
    for i in range(len(radec)):
        ra,dec,idph,magp2,magp3,magp4,merrp2,merrp3,merrp4 = radec[i].split()
        dmag.append(9.99)
        for j in range(len(fitmag)):
            raf,decf,idf,magf,magerrf = fitmag[j].split()
            if idph == idf and idph in idpsf and \
                 magp3 != 'INDEF' and magf != 'INDEF': 
                    dmag[i]= float(magp3)-float(magf)
                    break

    _dmag = compress(array(dmag)<9.99,array(dmag))

    if verbose:
        print('>>> Aperture correction (phot)   %6.3f +/- %5.3f %3d ' % \
         (mean(_dmag),std(_dmag),len(_dmag)))
        if len(_dmag) > 3: 
            _dmag = compress(abs(_dmag-median(_dmag)) < 2*std(_dmag),_dmag) 
            print('>>>         2 sigma rejection)   %6.3f +/- %5.3f %3d  [default]'\
               % (mean(_dmag),std(_dmag),len(_dmag)))

    for i in range(len(dmag)):
        if dmag[i]==9.99: dmag[i] = ''
        else: dmag[i] = '%6.3f' % (dmag[i])

    return mean(_dmag)

def bkg_fit(_xsnp,_ysnp,fsize,fwhm,bkg_ann,bkg_ord):

    xb1 = [int(_xsnp-fwhm*bkg_ann[0]),int(_xsnp-fwhm*bkg_ann[1])]
    xb2 = [int(_xsnp+fwhm*bkg_ann[0]),int(_xsnp+fwhm*bkg_ann[1])]
    yb1 = [int(_ysnp-fwhm*bkg_ann[0]),int(_ysnp-fwhm*bkg_ann[1])]
    yb2 = [int(_ysnp+fwhm*bkg_ann[0]),int(_ysnp+fwhm*bkg_ann[1])]

    for i in [0,1]:
        if xb1[i]<1: xb1[i]=1
        if yb1[i]<1: yb1[i]=1
        if xb2[i]>fsize: xb2[i]=fsize
        if yb2[i]>fsize: yb2[i]=fsize

    iraf.delete('_snbg.fit?,_snsky.fit?,_snskya.fit?,_snsub.fit?',verify=False)

    section= [str(xb1[1])+' '+str(xb1[0])+' '+str(yb1[1])+' '+str(yb2[1]),\
                  str(xb2[0])+' '+str(xb2[1])+' '+str(yb1[1])+' '+str(yb2[1]),\
                  str(yb1[1])+' '+str(yb1[0])+' '+str(xb1[0])+' '+str(xb2[0]),\
                  str(yb2[0])+' '+str(yb2[1])+' '+str(xb1[0])+' '+str(xb2[0])]

    iraf.imsurfit("_snori","_snbg",xorder=bkg_ord[0],yorder=bkg_ord[1],\
            type_output='fit',regions="section",section="STDIN",Stdin=section)

    midpt = iraf.imstat('_snbg''['+str(xb1[0])+':'+str(xb2[0])+','+\
            str(yb1[0])+':'+str(yb2[0])+']',field='mean',Stdout=1)
    iraf.imcopy('_snori','_snsky',verbose=False)
    iraf.imcopy('_snori','_snskya',verbose=False)
    iraf.imcopy('_snbg'+'['+str(xb1[1])+':'+str(xb2[1])+','+str(yb1[1])\
                        +':'+str(yb2[1])+']','_snskya'+'['+str(xb1[1])+\
                       ':'+str(xb2[1])+','+str(yb1[1])+':'+\
                        str(yb2[1])+']',verbose=False)
    iraf.imcopy('_snbg'+'['+str(xb1[0])+':'+str(xb2[0])+','+str(yb1[0])\
                        +':'+str(yb2[0])+']','_snsky'+'['+str(xb1[0])+\
                       ':'+str(xb2[0])+','+str(yb1[0])+':'+\
                        str(yb2[0])+']',verbose=False)
    iraf.imexpr("a -b + c", '_snsub',a='_snori',b='_snsky',\
                    c=float(midpt[1]),verbose=False)
    return bkg_ann,bkg_ord,[xb1,xb2,yb1,yb2]

def snfit(_img,_xsnp,_ysnp,snrlim,recenter,fwhm,bkg_ann,bkg_ord,xyb,
          apcor,verbose):
    
    exptime = 1. # images are normalized to 1sec
 
    a1,a2,a3,a4,a5 = int(fwhm+0.5),int(fwhm*2+0.5),int(fwhm*3+0.5),\
            int(fwhm*4+0.5),int(fwhm*5+.5)
    iraf.fitskypars.annulus = a5
    iraf.photpars.apertures = '%d,%d,%d'%(a2,a3,a5)
    iraf.datapars.datamin =  -200.
    iraf.daopars.psfrad = a4
    iraf.daopars.fitrad = a1
    iraf.daopars.fitsky = 'yes'
    iraf.daopars.sannulus = a4
    iraf.daopars.recenter = recenter
    iraf.daopars.varorder = 1

    ff = open('_sn.coo','w')
    ff.write(str(_xsnp)+" "+str(_ysnp)+'\n')
    ff.close()

    iraf.delete('_sn.or?,_sn.su?,_snres.fit?,_snfit.fit?,_snmodel.fit?,'+\
                   '_snorires.fit?,_sn.al?,_sn.ar?',verify=False)
#    time.sleep(1)

    iraf.phot('_snori','_sn.coo','_sn.ori',verify=False,verbose=verbose)
    iraf.phot('_snsub','_sn.coo','_sn.sub',verify=False,verbose=verbose)
    iraf.allstar('_snsub','_sn.sub',_img+'.psf','_sn.als','_sn.arj',\
                     '_snres',verify=False,verbose=verbose)

    iraf.imarith('_snsub','-','_snres','_snfit')
    iraf.imarith('_snori','-','_snfit','_snorires')
    iraf.imarith('_snfit','-','_snsky','_snmodel')
  
    #  compute SNR
    x1,x2 = int(_xsnp-a5),int(_xsnp+a5)
    y1,y2 = int(_ysnp-a5),int(_ysnp+a5)
    sect = '['+str(x1)+':'+str(x2)+','+str(y1)+':'+str(y2)+']'
    out = iraf.imstat('_snsub'+sect,fields='stddev',Stdout=1)
    stds = float(out[1])
    area = pi*(fwhm/2.)**2
    maglimit =  -2.5*log10(snrlim*area*stds/.5/exptime)+iraf.photpars.zmag 

    ################  

    orimag = iraf.txdump('_sn.ori','mag,merr',expr='yes',Stdout=1)
    phmag = iraf.txdump('_sn.sub','mag,merr',expr='yes',Stdout=1)
    fitmag = iraf.txdump('_sn.als','id,xcenter,ycenter,mag,merr',expr='yes',\
                             Stdout=1)

    omag,oerr = orimag[0].split()[1],orimag[0].split()[4]
    pmag,perr = phmag[0].split()[1],phmag[0].split()[4]

    if len(fitmag):
        fmag,ferr = fitmag[0].split()[3],fitmag[0].split()[4]
        fmag = '{:6.3f}'.format(float(fmag)+apcor)
        xx = '%6.2f' % (float(fitmag[0].split()[1]))
        yy = '%6.2f' % (float(fitmag[0].split()[2]))

        snr = '{:5.1f}'.format((0.50*exptime*(10**-(0.4*(float(fmag)-iraf.photpars.zmag)))/stds/area))

        if maglimit < float(fmag): 
            fmag = '{:6.3f}'.format(maglimit)
            ferr  = '{}'.format(999)
            snr  = '{:5.1f}'.format(snrlim)

    else: 
        xx,yy = 'INDEF','INDEF'
        fmag = '{:6.3f}'.format(maglimit)
        ferr  = '{}'.format(999)
        snr  = '{:5.1f}'.format(snrlim)

    snresult = {'xc':xx,'yc':yy,'mago':omag,'merro':oerr,'magp':pmag,\
                'merrp':perr,'magf':fmag,'merrf':ferr,'snr':snr}

    return snresult

def gw_sn(_img,_xsnt,_ysnt,seeing,snrlim,recenter,bkg_par,apcor,
          optlist,verbose):

    fwhm = seeing//float(optlist['global']['pixel_scale'])
    fsize=80

    x1,x2 = int(_xsnt-fsize/2.),int(_xsnt+fsize/2.)
    y1,y2 = int(_ysnt-fsize/2.),int(_ysnt+fsize/2.)
    _xsnp = _xsnt-x1+1
    _ysnp = _ysnt-y1+1

    iraf.delete('_snori.fit?',verify=False)
    iraf.imcopy(_img+'['+str(x1)+':'+str(x2)+','+str(y1)+':'+str(y2)+']',\
                    '_snori',verbose=False)

    bkg_ann = [float(bkg_par.split(',')[0]),float(bkg_par.split(',')[1])]
    bkg_ord = [int(float(bkg_par.split(',')[2])),\
                   int(float(bkg_par.split(',')[3]))]

    bkg_ann,bkg_ord,xyb = bkg_fit(_xsnp,_ysnp,fsize,fwhm,bkg_ann,bkg_ord)
    snresult = snfit(_img,_xsnp,_ysnp,snrlim,recenter,fwhm,bkg_ann,
                     bkg_ord,xyb,apcor,verbose)

    _xytargets = [str(_xsnp)+' '+str(_ysnp)]
    if verbose:
        iraf.set(stdimage='imt512')
        zcut = iraf.display('_snori',1,xcen=.25,ycen=.25,xsize=0.5,ysize=0.5,\
                   fill=True,erase=True,Stdout=1)
        iraf.tvmark(1,coords="STDIN",mark='circle',number=False,\
                      radii=int(2*fwhm),Stdin=_xytargets,interac=False)
        z1,z2 = int(float(zcut[0].split()[0][3:])),\
                            int(float(zcut[0].split()[1][3:]))
    #iraf.tvmark(1,coords="STDIN",mark='rectangle',\
    #                 length=int(fwhm*bkg_len),Stdin=xytargets,interac=False)
        iraf.display('_snmodel',1,xcen=.25,ycen=.75,xsize=0.5,ysize=0.5,\
                z1=z1,z2=z2,zscale=False,\
                         zrange=False,fill=True,erase=False,Stdout=1)
        iraf.display('_snorires',1,xcen=.75,ycen=.25,xsize=0.5,ysize=0.5,\
                 z1=z1,z2=z2,zscale=False,zrange=False,fill=True,erase=False,
                  Stdout=1)
        iraf.tvmark(1,coords="STDIN",mark='circle',number=False,\
                      radii=int(2*fwhm),Stdin=_xytargets,interac=False)
                        
#    shutil.move('_snoriresi.fits',img+'.res.fits')
    return snresult

if __name__ == "__main__":

    hdr = fits.getheader(args.img+".fits")
    xdim,ydim = hdr['NAXIS1'],hdr['NAXIS2']    

    if args.fwhm: fwhm = args.fwhm*float(optlist['global']['pixel_scale'] )
    else:         fwhm = hdr['FWHM']
 
    xcoo,ycoo =[float(x) for x in args.sncoo.split(',')]

    if 'p' in args.xtasks:
        apcor = gw_psf('xx','xx',args.img,xcoo,ycoo,fwhm,
            args.threshold,args.psfstars,xdim,ydim,optlist,args.verbose)
                        
 #       if args.verbose:
  #          iraf.delete('_psf.fit?',verify=False)
  #          iraf.seepsf(args.img+'.psf','_psf.psf')
  #          iraf.surface('_psf.psf')
  #          raw_input('>>>   return to next .....')

    if 'f' in args.xtasks:
        snresult = gw_sn(args.img,xcoo,ycoo,fwhm,args.snrlim,args.recenter,
                     args.bkg_par,apcor,optlist,args.verbose)
    
        print('>>> mag={}+/-{} snr={}'.format(snresult['magf'],
          snresult['merrf'],snresult['snr']))
    print( "********** Completed in ",int(time.time()-start_time),"sec")

