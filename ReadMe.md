Author: Peter Pfleiderer <peter.pfleiderer@climateanalytics.org>
License: GNU General Public License v3.0

# Installation

This project requires python2.7 with the following packages:  
- numpy
- netCDF4
- basemap
- matplotlib
- shapely
- descartes
- fiona
- flask
- flask-wtf
- gunicorn
- pandas
- scipy
- seaborn
- unidecode
- pycountry
- dimarray


```
conda create --name some_name
conda install numpy netCDF4 matplotlib shapely descartes fiona flask flask-wtf pandas scipy seaborn unidecode cartopy
```
the two packages pycountry and dimarray are not found by conda, install them using pip
```
pip install pycountry dimarray uwsgi
```
you would also need the git repositories "country_analysis_scripts" and "wlcalculator"
clone them into the same directory where RegioClim is located or change the path in the respective files (might be tedious)
```
git clone https://github.com/peterpeterp/country_analysis
git clone https://gitlab.pik-potsdam.de/mengel/wlcalculator.git
```

# Testing

move into the porject directory (cd RegioClim)
activate your python environment (source activate some_name)
run the following command:
```
python run.py
```
in your browser the test-website will be available on http://127.0.0.1:5000



# uwsgi --socket 0.0.0.0:8003 --protocol=http -w wsgi:app
