########################################################################
# service scripts
########################################################################
import os,sys,subprocess
from numpy import *
import argparse
import configparser
import shlex

gw_scripts = os.path.expandvars("$gw_scripts")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(\
         formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-v", "--verbose",dest="verbose",\
                  action="store_true",default=False,
                  help='Print tasks description')
    args = parser.parse_args()

def aiuto(verbose):
    shell = os.environ["SHELL"]
    if 'bash' in shell:  ff = open(gw_scripts+'/gw.bash')
    elif 'csh' in shell: ff = open(gw_scripts+'/gw.csh')
    righe = ff.readlines()
    print((20*'#'+'   GW scripts  (version '+gw_scripts.split('/')[-2]+")  "+20*"#"))
    for r in righe:
        if 'alias ' == r[:6]:
            if 'bash' in shell: prog = r[len('alias '):r.index('=')]
            if 'csh' in shell:  prog = r.split()[1]
            exec('import '+prog)
            tab = "\t"
            if len(prog)<7: tab +="\t"
            print(prog,tab,end="")
            exec('print('+prog+'.description)')
        elif '#comment' in r:
            print('--',r[8:-1])
    print(80*'#')

def runsex(img,seeing,optlist,threshold,format,verbose,ss):
    fwhm = seeing / float(optlist['global']['pixel_scale'])

    cdef = open(gw_scripts+"/default/default.param") 
    riga = cdef.readlines()
    cparam = []
    for r in riga:
        if r[0] != '#' and len(r.strip())>0: \
           cparam.append(r.split()[0])

    fwlim = array([2.0, 2.75, 3.25, 3.75, 4.5, 6.,8., 10.])
    gconv = ['2.5_5x5', '3.0_7x7','3.5_7x7','4.0_7x7','5.0_9x9',\
             '7.0_17x17','9.0_17x17']
    if fwhm<fwlim[0]:
        usefilter = "N"
        gauss = 'gauss_'+gconv[0]+'.conv'
        if verbose:
          print("!!! WARNING: seeing ["+str(int(fwhm))+\
            " pix] outside gauss filter range. Filter not used.")
    elif fwhm>fwlim[-1]:
        usefilter = "N"
        gauss = 'gauss_'+gconv[-1]+'.conv'
        if verbose:
            print("!!! WARNING: seeing ["+str(int(fwhm))+\
               " pix] outside gauss filter range. Filter not used")
    else:
        i = len(compress(fwlim<fwhm,fwlim))
        gauss = 'gauss_'+gconv[i-1]+'.conv'
        usefilter = "Y"

    if verbose: sex_verbose = 'NORMAL'
    else: sex_verbose = 'QUIET'

    if format == 'fits':
        outformat, outcatext = 'FITS_1.0','fits'
    elif format == 'ascii': 
        outformat, outcatext = 'ASCII_HEAD','cat'

    sexrun = "sex "+img+".fits"+\
       " -catalog_name tmp_"+ss+'.'+outcatext+\
       " -c "+gw_scripts+"default/default.sex"+\
       " -PARAMETERS_NAME "+gw_scripts+"/default/default.param"+\
       " -STARNNW_NAME "+gw_scripts+"/default/default.nnw"+\
       " -FILTER_NAME "+gw_scripts+'/default/'+gauss+\
       " -PIXEL_SCALE "+optlist['global']['pixel_scale']+\
       " -PHOT_APERTURES "+optlist['sextractor']['phot_aperture']+\
       " -ANALYSIS_THRESH  "+\
              str(float(optlist['sextractor']['analysis_thresh'])*threshold)+\
       " -DETECT_MINAREA "+\
               str(float(optlist['sextractor']['detect_minarea'])*fwhm)+\
       " -DETECT_THRESH  "+str(threshold)+\
       " -BACK_SIZE "+optlist['sextractor']['back_size']+\
       " -MAG_ZEROPOINT "+optlist['global']['mag_zeropoint']+\
       " -SATUR_LEVEL "+optlist['global']['satur_level']+\
       " -SEEING_FWHM "+str(seeing)+\
       " -VERBOSE_TYPE "+sex_verbose+\
      " -CATALOG_TYPE "+outformat
    if verbose: print(sexrun)

    pid = subprocess.call(shlex.split(sexrun))

    return cparam

def stilts_run(cmd,task,verbose):

    _cmd = shlex.split(cmd)
    pid = subprocess.Popen(_cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)  
    output,error = pid.communicate()
    if verbose: 
        print('>>>',task)
        print(output.decode())
        print(error.decode())
    if error: 
        if 'Error'==error.decode()[:5]: 
            print(cmd)
            print(error.decode())
            print(20*'!'+' Fatal stilts error: program terminated '+20*'!')
            sys.exit()

def set_default():
    _dir = gw_scripts
    if  os.path.isfile('gw.default'):
        print(">> WARNING: using local gw.default file")
        _dir = ''
    config = configparser.ConfigParser()
    config.read(_dir+'gw.default')

def read_default():       #  read parameter file ###################

    _dir = gw_scripts
    if  os.path.exists('gw.default'):
        _dir = ''
        print('!!! Warning: using local gw.default !!!')
    config = configparser.ConfigParser()
    config.read(_dir+'gw.default')   
#    input(config.sections()) 
    optlist = {}
    for s in config.sections():
        optlist[s] = {}
        for o in config.options(s):
            optlist[s][o] = config.get(s,o)
    return optlist


if __name__ == "__main__":

    aiuto(args.verbose)
    set_default()

