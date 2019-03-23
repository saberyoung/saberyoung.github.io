from __future__ import print_function
from builtins import input
import glob,argparse,time,sys,os

addstr = '<tr align="center"><td>%s</td><td>%s</td><td>%s</td><td>%s<br></td>\n'
addstr1 = '<a href="./%s">%s</a>'

if __name__ == "__main__":
    start_time = time.time()
    parser = argparse.ArgumentParser(description='update web',\
                formatter_class=argparse.ArgumentDefaultsHelpFormatter)       
    parser.add_argument("trigger",help='trigger name')
    parser.add_argument("info",help='trigger informations')    
    parser.add_argument("-d",dest="dir",default='.',help='dir name')
    args = parser.parse_args()

    indexfile1,indexfile2 = '',''
    _indexfull = args.dir+'/index.html'
    for nii,ii in enumerate(open(_indexfull).readlines()):
        if nii <= 13:indexfile1+=ii
        else:indexfile2+=ii

    _filelist,_imglist = [],[]
    for _ff in glob.glob('*'+args.trigger+'*'):
        if '.txt' in _ff:_filelist.append(_ff)
        elif '.png'in _ff:_imglist.append(_ff)
    if len(_filelist)>0 or len(_imglist)>0:
        os.remove(_indexfull)
        indexfilenew = open(_indexfull,'w')
        _fileout,_imgout = '',''
        for nn,_list in zip([0,1],[_filelist,_imglist]):
            for _nll,_ll in enumerate(_list):
                if nn == 0:_fileout+=addstr1%(_ll,_ll)
                if nn == 1:_imgout+=addstr1%(_ll,_ll)
                if _nll<len(_list)-1:                
                    _fileout+='<br>'
                    _imgout+='<br>'    
        indexfile12 = addstr%(args.trigger,args.info,_fileout,_imgout)
        indexfilenew.write('\t'+indexfile1+indexfile12+indexfile2)
        indexfilenew.close()

        os.system('git -C %s add .'%args.dir)
        os.system('git -C %s commit -m "%s"'%(args.dir,args.trigger))
        os.system('git -C %s push'%args.dir)
