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
from netCDF4 import Dataset,netcdftime,num2date
import pandas as pd

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import rc
rc('text', usetex=True)

basepath='/Users/peterpfleiderer/Documents/Projects/'
try: 
  os.chdir(basepath)
except:
  basepath='/home/RCM_projection/'

sys.path.append(basepath+'country_analysis/country_analysis_scripts/')
import country_analysis; reload(country_analysis)
sys.path.append(basepath+'/projection_sharing/')
os.chdir(basepath+'/projection_sharing/')

seasons={'year':range(1,13)}
for i in range(1,13):
	seasons[str(i)]=[i]

country_names={'BEN':'Benin','SEN':'Senegal','UGA':'Uganda'}

regions={}
	# 'SEN':['Senegal (full country)', 'Kaolack', 'Fatick', 'Kolda', 'Tambacounda', 'Dakar', 'Saint-Louis', 'Matam', 'Kedougou', 'Louga', 'Sedhiou', 'Thies', 'Diourbel', 'Kaffrine', 'Ziguinchor'],
	# 'BEN':['Benin (full country)','Borgou', 'Collines', 'Mono', 'Kouffo', 'Atlantique', 'Donga', 'Plateau', 'Atakora', 'Alibori', 'Littoral', 'Oueme', 'Zou']
#}

# for iso in country_names.keys():
# 	print iso
# 	COU=country_analysis.country_analysis(iso,'../country_analysis/data/'+iso+'/',seasons=seasons)
# 	COU.load_data(quiet=True,filename_filter='dont_load_anything')
# 	regions[iso]=[country_names[iso]+' (full country)']+COU._regions.keys()


datasets=['CORDEX_BC','CMIP5_BC']

season_dict={
	'SEN':seasons.keys(),
	'UGA':seasons.keys(),
	'BEN':seasons.keys()
}

ind_dict={
	'tas':{'unit':'$^\circ C$','time_step':'monthly'},
	'pr':{'unit':'mm','time_step':'monthly'},
	'RX1':{'unit':'mm','time_step':'monthly'},
	'TXx':{'unit':'$^\circ C$','time_step':'monthly'},
	'year_RX5':{'unit':'mm','time_step':'yearly'},
}

lang_dict={'fr':{
	'tas':'Température',
	'pr':'Précipitation',
	'RX1':'Extrêmes humides (RX1day)',
	'TXx':'Extrêmes de chaleur (TXx)',
	'year_RX5':'Extrêmes humides de 5 jours (RX5day)',
	'year':'annuel',
	'1':'Janvier',
	'2':'Février',
	'3':'Mars',
	'4':'Avril',
	'5':'Mai',
	'6':'Juin',
	'7':'Juillet',
	'8':'Août',
	'9':'Septembre',
	'10':'Octobre',
	'11':'Novembre',
	'12':'Décembre',
	},
	'en':{
	'tas':'Temperature',
	'pr':'Precipitation',
	'RX1':'Wet Extremes (RX1day)',
	'TXx':'Hot Extremes (TXx)',
	'year_RX5':'5day Wet Extremes (RX5day)',
	'year':'annual',
	'1':'January',
	'2':'Febuary',
	'3':'March',
	'4':'April',
	'5':'Mai',
	'6':'June',
	'7':'July',
	'8':'August',
	'9':'September',
	'10':'October',
	'11':'November',
	'12':'December',
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

plot_titles={'en':{
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



ref_period  = [1986,2005]
proj_period = [2031,2050]
periods_beginner	= ['2020-2040','2040-2060']
periods_advanced	= ['2020-2040','2040-2060','2','1.5']

period_dict	= {
	'2020-2040':'2020-2040',
	'2040-2060':'2040-2060',
	'2':'2 deg global warming',
	'1.5':'1.5 deg global warming',
}

text_dict={'en':{
	'warning':'Warning!',
	'warning_txt':'The chosen region is smaller than 5 grid-cells. Please use the "Merge Region" function to aggregate several small regions.',

	'merge_page_h':'Add another region',
	'merge_page_txt':'Select a region you want to add to the chosen region.',
	'warning_merge_page_txt':'The chosen region is smaller than 5 grid-cells. Please select another region you want to merge the current region with.',

	'season_page_h':'Add another month',
	'season_page_txt':'Select a month that will be added to the season',

	'region_h':'Administrative Region',
	'region_txt':'Region for which the transient and annual cycle is presented. Use "Merge Regions" function to aggregate several small regions.',

	'country_h':'Country',
	'country_txt':'For the moment only the PAS-PNA countries Benin and Senegal are available. Could be extended',

	'indicator_h':'Climate Indicator',
	'indicator_txt':'Climate indicators based on daily temperature and precipitation. For the moment no drought indicator is included. Please consider monthly precipitation for drought assements and keep in mind that potential evapotranspiration might increase in a warmer world.',

	'time_scale_h':'Time Scale',
	'time_scale_txt':'Projected trends might depend on the season. As for different regions the monsoon onset and end differes, use monthly data to estimate seasonal changes.',

	'ref_period':'Reference Period',
	'proj_period':'Projection Period',

},'fr':{
	'warning':'Avertissement!',
	'warning_txt':'La région choisie est plus petite que 5 grilles. Veuillez utiliser la fonction "Regrouper des Régions" pour regrouper différentes régions.',

	'merge_page_h':'Ajoutez une Région',
	'merge_page_txt':'Choisissez une région qui sera combiné avec la région actuelle.',
	'warning_merge_page_txt':'La région choisie est plus petite que 5 grilles. Veuillez choisir une autre région à combiner avec la région actuelle.',

	'season_page_h':'Ajoutez un mois',
	'season_page_txt':'Choisissez un mois qui sera ajouté à la saison',

	'region_h':'Région administrative',
	'region_txt':'Région pour laquelle le trajectoire et le cycle annuel sont présentés. Utilisez la fonction "Regrouper des Régions" pour regrouper différentes régions.',

	'country_h':'Pays',
	'country_txt':'Pour le moment seulement le Bénin et le Sénégal peuvent être sélectionné. La liste des pays sera bientôt élargie.',

	'indicator_h':'Indicateur Climatique',
	'indicator_txt':'Indicateurs climatiques basés sur des donnés quotidiennes de température et de précipitation. Pour le moment aucun indicateur de sécheresse est présenté. Veuillez considérer les projection de précipitation pour les analyses de sécheresses en gardant à l`esprit que l`évapotranspiration potentielle pourrait augmenter avec la température.',

	'time_scale_h':'Échelle temporelle',
	'time_scale_txt':'Les tendances projetés peuvent fortement dépendre de la saison. Veuillez choisir le mois le plus pertinent pour votre analyse ou définir une saison en utilisant la fonction "Définir une Saison".',

	'ref_period':'Période de Référence',
	'proj_period':'Période de Projection',

}
}

button_dict={'en':{
	'merge_regions':'Merge regions',
	'select_periods':'Select Periods',
	'define_season':'Define Season',
	'download_png':'Download png',
	'download_pdf':'Download pdf',
	'download_data':'Download data',
	'save_region':'Keep this Region',
	'save_season':'Keep this Season',

},'fr':{
	'merge_regions':'Regrouper des Régions',
	'select_periods':'Choisir ces Périodes',
	'define_season':'Définir une Saison',
	'download_png':'Télécharger png',
	'download_pdf':'Télécharger pdf',
	'download_data':'Télécharger data',
	'save_region':'Garder cette Région',
	'save_season':'Garder cette Saison',
}
}


print 'done with settings'







