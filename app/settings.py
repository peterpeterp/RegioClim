# Copyright (C) 2014 Matthias Mengel and Carl-Friedrich Schleussner
#
# This file is part of wacalc.
#
# wacalc is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation; either version 3 of the License, or (at your option) any later
# version.
#
# wacalc is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License
# along with wacalc; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA




""" database setting file. """


import sys,glob,os,pickle
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import pandas as pd

sys.path.append('/Users/peterpfleiderer/Documents/Projects/country_analysis/country_analysis_scripts/')
try:del sys.modules['country_analysis_obj'] 
except:pass
from country_analysis_obj import country_analysis,plot_map,new_data_object
os.chdir('/Users/peterpfleiderer/Documents/Projects/projection_sharing/app/')


reference_period  = [1980,2000]
projection_period = [2030,2050]
scenarios	= ['rcp45']

os.chdir('/Users/peterpfleiderer/Documents/Projects')

COU={}

COU['SEN']=country_analysis('SEN','/Users/peterpfleiderer/Documents/Projects/country_analysis/SEN/')
COU['SEN'].load_data()

COU['BEN']=country_analysis('BEN','/Users/peterpfleiderer/Documents/Projects/country_analysis/BEN/')
COU['BEN'].load_data()

countrys=COU.keys()

os.chdir('/Users/peterpfleiderer/Documents/Projects/projection_sharing/app/')

indicator_dict={
	'tas':{'long_name':'mean temperature','unit':'$^\circ C$'},
	'pr':{'long_name':'precipitation','unit':'mm'},
	'RX1':{'long_name':'maximal daily precipitation','unit':'mm'},
	'year_RX5':{'long_name':'cumulative 5 day precipitation','unit':'mm'},
	'TXx':{'long_name':'daily maximal temperature','unit':'$^\circ C$'},
	'year_CDD':{'long_name':'maximal dry spell length','unit':'days'},
}

for key in indicator_dict.keys():
	indicator_dict[key]['ylabel']=indicator_dict[key]['long_name']+' ['+indicator_dict[key]['unit']+']'
















