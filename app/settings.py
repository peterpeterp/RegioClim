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
import pandas as pd


import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


countrys=['BEN','SEN']

indicators = ['tas','pr','RX1','year_RX5','TXx','year_CDD']
indicator_dict={
	'tas':{'long_name':'mean temperature','unit':'$^\circ C$','seasons':['year','dry','wet']},
	'pr':{'long_name':'precipitation','unit':'mm','seasons':['year','dry','wet']},
	'RX1':{'long_name':'maximal daily precipitation','unit':'mm','seasons':['year','dry','wet']},
	'TXx':{'long_name':'daily maximal temperature','unit':'$^\circ C$','seasons':['year','dry','wet']},
	'year_RX5':{'long_name':'cumulative 5 day precipitation','unit':'mm','seasons':['year']},
	'year_CDD':{'long_name':'maximal dry spell length','unit':'days','seasons':['year']},
}

for key in indicator_dict.keys():
	indicator_dict[key]['ylabel']=indicator_dict[key]['long_name']+' ['+indicator_dict[key]['unit']+']'

scenario='rcp45'

regions={
	'SEN':['Kaolack', 'Fatick', 'Kolda', 'Tambacounda', 'Dakar', 'Saint-Louis', 'Matam', 'Kedougou', 'Louga', 'Sedhiou', 'Thies', 'SEN', 'Diourbel', 'Kaffrine', 'Ziguinchor'],
	'BEN':['Borgou', 'Collines', 'BEN', 'Mono', 'Kouffo', 'Atlantique', 'Donga', 'Plateau', 'Atakora', 'Alibori', 'Littoral', 'Oueme', 'Zou']
}


reference_period  = [1986,2006]
projection_period = [2030,2050]
periods	= ['2020-2040','2040-2060','2','1.5']

period_dict	= {
	'2020-2040':'2020-2040',
	'2040-2060':'2040-2060',
	'2':'2 deg global warming',
	'1.5':'1.5 deg global warming',
}




