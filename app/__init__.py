# -*- coding: utf-8 -*-
import os,sys
print('importing')
print(hasattr(sys, 'real_prefix'))
print(sys.executable)

os.system('which python')

from flask import Flask

import sys
if sys.version_info.major < 3:
    reload(sys)
sys.setdefaultencoding('utf8')

app = Flask(__name__)
app.config.from_object('config')



from app import views
from app import forms

#from flask import Flask

#app = Flask(__name__)
#app.config.from_object('config')

#from app import views


#from .models import db
#from .views import tracking

#app = Flask(__name__)
#app.config.from_object('config')
