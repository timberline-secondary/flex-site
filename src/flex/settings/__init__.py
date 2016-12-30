from .base import *

try:
    # this file will only exists on the production server
    from .production_flexsite import *
except:
    print("***** NO PRODUCTION SETTINGS FOUND     *******")
    print("***** IMPORTING LOCAL SETTINGS         *******")
    from .local import *