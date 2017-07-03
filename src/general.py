
import sys
from os.path import join as pathjoin, abspath, dirname, normpath


def project_root():
    '''
    Gets absolute path of project root

    :return: Returns absolute path string for project root directory
    '''
    return normpath(pathjoin(dirname(abspath(sys.argv[0])), "..")) #gets root of project (moving out of src)

PROJECT_ROOT = project_root()

DEBUG = True

ASSETS_DIR = pathjoin(PROJECT_ROOT, "mock") #should be changed for release