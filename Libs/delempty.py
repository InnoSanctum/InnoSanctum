def finddirs(dirpath: str) -> bool:
    import glob
    from os.path import isdir
    dirlist = [f for f in glob.glob(''.join((dirpath, '\\*'))) if isdir(f)]    
    if len(dirlist):
        return True
    return False     

def findfiles(dirpath: str) -> bool:
    import glob
    from os.path import isfile
    filelist = [f for f in glob.glob(''.join((dirpath, '\\*'))) if isfile(f)]    
    if len(filelist):
        return True
    return False     

def delete_empty_folders(dirpath: str, *, recursive: bool = False, del_root = False) -> int:
    """
    Deletes empty folders within the folder dirpath: string. Return codes: 1 - nothing deleted, 2 - some folders were deleted, 0 - error.
    
    Arguments: 
        recursive   : bool - delete empty folders recursively, False by default;
        del_root    : bool - delete the root folder as well, if it is empty, False by default.
    """
    
    import os
    import os.path
    import glob
    
    if not os.path.exists(dirpath):
        return(0)  # prob. need another exit code
    
    if len(os.listdir(dirpath)):  # dirpath is not empty
        if not finddirs(dirpath): # no folders in dirpath, so there are only files. - no need to delete -> exit with True
            return(1) # exit with code 1 - no empty folders left, only with files
        
        # so, there are folders in dirpath
        if not recursive: # recursive deletion requested
            return(1) # dirpath is not empty - no need to delete - non-recursive -> exit with True
        
        # so, recursive is True...
        
        dirlist = [f for f in glob.glob(''.join((dirpath, '\\*'))) if os.path.isdir(f)]  # filding all 1st level dirs within dirpath
        recheck = False
        
        for dir in dirlist: # looping through them
            if delete_empty_folders(dir, recursive=True, del_root=True) == 2: recheck = True # and deleting empty folders in them. If we delete something -> code 2, 
                                                                                             # so need to recheck root folder for changes               
        if recheck: # now we try to delete empty folders for dirpath again; 
            if del_root:
                delete_empty_folders(dirpath, recursive=True, del_root=True)            
            else:
                delete_empty_folders(dirpath, recursive=True)
            return(2)  # if we've set recheck, then we've deleted something , so retcode = 2  
        return(1)        

    if del_root:
        try: # trying to delete empty folder dirpath
            os.rmdir(dirpath)
        except Exception as e: # failure?
            print(e)
            return(0) # some unknown error
        return(2)
    return(1)        
            
def progressbar(val:int, max: int, *, symbol: str = '*', space: str = '.'):
    percent = int(val*100/max)+1
    print(f'[{percent*symbol}{int(100-percent)*space}] {str(percent).zfill(3)}%', end='\r')

def main():
    pass

if __name__ == '__main__':
    main()