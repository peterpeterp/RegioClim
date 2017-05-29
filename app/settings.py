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

datasets=['CORDEX_BC','CMIP5_BC']

season_dict={
	'SEN':['Jun-Sep','year'],
	'BEN':['Apr-Jul','year']
}

ind_dict={
	'tas':{'unit':'$^\circ C$','time_step':'monthly'},
	'pr':{'unit':'mm','time_step':'monthly'},
	'RX1':{'unit':'mm','time_step':'monthly'},
	'TXx':{'unit':'$^\circ C$','time_step':'monthly'},
	'year_RX5':{'unit':'mm','time_step':'yearly'},
}

lang_dict={'fr':{
	'tas':'température moyenne',
	'pr':'précipitation',
	'RX1':'précipitation quotidienne maximale',
	'TXx':'température quotidienne maximale',
	'year_RX5':'précipitation maximale cumulées en 5 jours',
	'year_CDD':'duré maximal de période aride',
	'year':'annuel',
	'Apr-Jul':'Apr-Jul',
	'Jun-Sep':'Jun-Sep'
	},
	'en':{
	'tas':'mean temperature',
	'pr':'precipitation',
	'RX1':'maximal daily precipitation',
	'TXx':'daily maximal temperature',
	'year_RX5':'maximal cumulative 5 day precipitation',
	'year_CDD':'maximal dry spell length',	
	'year':'annual',
	'Apr-Jul':'Apr-Jul',
	'Jun-Sep':'Jun-Sep'
	}
}

form_labels={'fr':{
	'country':u'Pays analysé:',
	'region':u'Région administrative:',
	'scenario':u"Scénario d'émission:",
	'indicator':u'Indicateur climatique:',
	'period':u'Période de projection:',
	'season':u'Saison:',
	},'en':{
	'country':u'Studied country:',
	'region':u'Administrative region:',
	'scenario':u'Emission scenraio:',
	'indicator':u'Climate indicator:',
	'period':u'Projection period:',
	'season':u'Season:',	
	}
	
}

plot_titles={'fr':{
	'EWEMBI_plot':u"Observations EWEMBI pour la période de réference 1986-2006",
	'CORDEX_plot':u"Projections de modèles cliamtiques",
	'transient_plot':u"",
	'annual_cycle_plot':u""
	},'fr':{
	'EWEMBI_plot':u"EWEMBI observations over the reference period 1986-2006",
	'CORDEX_plot':u"Change projected by regional climate modeles ",
	'transient_plot':u"",
	'annual_cycle_plot':u""
	}	
}


scenarios=['rcp4p5']

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




