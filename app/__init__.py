from flask import Flask

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

