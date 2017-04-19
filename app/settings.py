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
countrys 	= ['BEN']

os.chdir('/Users/peterpfleiderer/Documents/Projects')

COU={}

COU['BEN']=country_analysis('BEN','/Users/peterpfleiderer/Documents/Projects/country_analysis/')
COU['BEN'].load_from_tar('/Users/peterpfleiderer/Documents/Projects/country_analysis/BEN.tar.gz')

indicators  = list(set([data.var_name for data in COU['BEN']._DATA]))


os.chdir('/Users/peterpfleiderer/Documents/Projects/projection_sharing/app/')




















