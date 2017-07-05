
import sys
from datetime import datetime
from os.path import join as pathjoin, abspath, dirname, normpath, exists as pathexists
from os import listdir, makedirs
import shutil


def project_root():
    '''
    Gets absolute path of project root

    :return: Returns absolute path string for project root directory
    '''
    return normpath(pathjoin(dirname(abspath(sys.argv[0])), "..")) #gets root of project (moving out of src)

def nowstr():
    return datetime.utcnow().strftime("%Y%m%d%H%M%S")

def move_dir(from_dir, to_dir):
    for file in listdir(from_dir):
        from_file = pathjoin(from_dir, file)
        to_file = pathjoin(to_dir, file)
        shutil.move(from_file, to_file)

def mkdir(directory):
    if not pathexists(directory):
        makedirs(directory)

PROJECT_ROOT = project_root()

DEBUG = True

ASSETS_DIR = pathjoin(PROJECT_ROOT, "mock") #should be changed for release