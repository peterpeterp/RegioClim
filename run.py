#from flask import Flask
from app import app

#app = Flask(__name__)
##Bootstrap(app)
app.config.from_object('config')
#app.debug = True

if __name__ == "__main__":
    app.debug = True
    app.run()
