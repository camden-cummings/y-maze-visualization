"""Functions for finding sets of files."""
import os

def find_all_videos_for_tracking(path=None, ext="avi"):
    """Finds all avi files in current working directory, if path given finds all
    avi files in path that aren't output of the algorithm."""
    if path is None:
        path = os.getcwd()

    files_to_read = []
    for ex in os.walk(path):
        for filename in ex[2]:
            if filename[-3:] == ext and not "tracked" in filename and not "checking" in filename \
            and not "examine" in filename and not "output" in filename:
                files_to_read.append(ex[0] + "/" + filename)

    return files_to_read

def find_all_files(path=None, extension="", exclude=[]):
    """Finds all files of a given extension type, starting from either current
    working directory or given path."""
    if path is None:
        path = os.getcwd()

    extension = extension.replace('.', '')
    
    if path[-1] == "/":
        path = path[:-1]
    
    files_to_read = []
    for ex in os.walk(path):
        for filename in ex[2]:
            if filename.split('.')[-1] == extension and (len(exclude) == 0 or not excluded(exclude, filename)):
                files_to_read.append(ex[0] + "/" + filename)

    return files_to_read

def excluded(exclude, filename):
    for ex in exclude:
        if ex in filename:
            return True
    
    return False
    
def find_all_files_by_directory(path=None, extension=""):
    if path is None:
        path = os.getcwd()

    files_to_read = []
    for ex in os.walk(path):
        for filename in ex[2]:
            if extension in filename:
                files_to_read.append(ex[0] + "/" + filename)

    files_to_read.sort(key=lambda fn: fn.split("-")[-3])
    
    rearr_files = []
    new_section = [files_to_read[0]]

    for f_num in range(len(files_to_read)-1):
        if (files_to_read[f_num].split("-")[-3] == files_to_read[f_num+1].split("-")[-3]):
            new_section.append(files_to_read[f_num+1])
        else:
            rearr_files.append(new_section)
            new_section = [files_to_read[f_num+1]]
    
    if new_section not in rearr_files:
        rearr_files.append(new_section)
        
    return rearr_files