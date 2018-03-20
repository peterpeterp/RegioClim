

# Installation

This project requires python2.7 with the following packages:  
- numpy
- netCDF4
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
- pycountry
- dimarray
- cartopy

```
conda create --name some_name
conda install numpy netCDF4 matplotlib shapely descartes fiona flask flask-wtf gunicorn pandas scipy seaborn
```
the two packages pycountry and dimarray are not found by conda, install them using pip
```
pip install pycountry
pip install dimarray
```
the two packages crtopy is not found by conda either, install it like this:
```
conda install -c conda-forge cartopy
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


# To Do
get rid of double templates. having choices_en and choices_fr is really annoying
