from pythonforandroid.recipe import CythonRecipe


class OpenCVRecipe(CythonRecipe):
    version = '4.5.5'
    url = 'https://github.com/opencv/opencv-python/archive/{version}.zip'
    name = 'opencv'
    site_packages_name = 'cv2'
    depends = ['numpy']
    call_hostpython_via_targetpython = False


recipe = OpenCVRecipe()
