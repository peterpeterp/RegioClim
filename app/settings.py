# -*- coding: utf-8 -*-

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

ind_dict={
	'tas':{'unit':'$^\circ C$','seasons':['year','dry','wet']},
	'pr':{'unit':'mm','seasons':['year','dry','wet']},
	'RX1':{'unit':'mm','seasons':['year','dry','wet']},
	'TXx':{'unit':'$^\circ C$','seasons':['year','dry','wet']},
	'year_RX5':{'unit':'mm','seasons':['year']},
	'year_CDD':{'unit':'days','seasons':['year']},	
}

lang_dict={'fr':{
	'tas':'température moyenne',
	'pr':'précipitation cumulée',
	'RX1':'précipitation quotidienne maximale',
	'TXx':'température quotidienne maximale',
	'year_RX5':'précipitation maximale cumulées en 5 jours',
	'year_CDD':'duré maximal de période aride',
	'year':'annuel',
	'dry':'saison sèche',
	'wet':'saison humide'
	},
	'en':{
	'tas':'mean temperature',
	'pr':'precipitation',
	'RX1':'maximal daily precipitation',
	'TXx':'daily maximal temperature',
	'year_RX5':'maximal cumulative 5 day precipitation',
	'year_CDD':'maximal dry spell length',	
	'year':'annual',
	'dry':'dry season',
	'wet':'wet season'
	}
}

scenarios=['rcp45']

regions={
	'SEN':['Kaolack', 'Fatick', 'Kolda', 'Tambacounda', 'Dakar', 'Saint-Louis', 'Matam', 'Kedougou', 'Louga', 'Sedhiou', 'Thies', 'SEN', 'Diourbel', 'Kaffrine', 'Ziguinchor'],
	'BEN':['Borgou', 'Collines', 'BEN', 'Mono', 'Kouffo', 'Atlantique', 'Donga', 'Plateau', 'Atakora', 'Alibori', 'Littoral', 'Oueme', 'Zou']
}


reference_period  = [1986,2006]
projection_period = [2030,2050]
periods_beginner	= ['2020-2040','2040-2060']
periods_advanced	= ['2020-2040','2040-2060','2','1.5']

period_dict	= {
	'2020-2040':'2020-2040',
	'2040-2060':'2040-2060',
	'2':'2 deg global warming',
	'1.5':'1.5 deg global warming',
}




