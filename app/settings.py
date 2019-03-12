# -*- coding: utf-8 -*-

# Copyright (C) 2017 Peter Pfleiderer
#
# This file is part of regioclim.
#
# regioclim is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation; either version 3 of the License, or (at your option) any later
# version.
#
# regioclim is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License
# along with regioclim; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA




""" database setting file. """


import sys,glob,os,pickle,string
import numpy as np
from netCDF4 import Dataset,num2date
import pandas as pd
import pycountry

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import rc
rc('text', usetex=True)

basepath='/Users/peterpfleiderer/Projects/RegioClim'
try:
  os.chdir(basepath)
except:
  basepath='/home/tooli/regioClim/'

# print('importing')
# print(hasattr(sys, 'real_prefix'))
# print(sys.executable)
#
# os.system('which python')

# sys.path.append(basepath+'country_analysis/country_analysis_scripts/')
# import country_analysis; reload(country_analysis)
# sys.path.append(basepath+'/regioClim/')
# os.chdir(basepath+'/regioClim/')

seasons={'year':range(1,13)}
for i in range(1,13):
	seasons[str(i)]=[i]

all_isos=['AGO', 'DZA', 'EGY', 'GNQ', 'BEN', 'NGA', 'NER', 'ZWE', 'NAM', 'GNB', 'SWZ', 'GHA', 'COG', 'SLE', 'ETH', 'COM', 'ERI', 'CPV', 'LBR', 'LBY', 'LSO', 'UGA', 'RWA', 'SOM', 'MDG', 'CMR', 'TZA', 'BWA', 'SEN', 'TCD', 'GAB', 'BFA', 'MWI', 'MOZ', 'MRT', 'GMB', 'MLI', 'BDI', 'STP', 'DJI', 'GIN', 'ESH', 'KEN', 'MAR', 'COD', 'ZMB', 'ZAF', 'TGO', 'TUN', 'CAF', 'SSD', 'SDN', 'CIV','SYC','MUS']

iso_fr=open('app/iso_french_country.txt','r').read().split('\n')
french_cou_dict={}
for line in iso_fr:
    if len(line)>1:
        french_cou_dict[line.split('\t')[2][0:3]]=line.split('\t')[0]

french_cou_dict['ESH']='Sahara occidental'

country_names={}
for iso in all_isos:
	if os.path.isdir('app/static/COU_images/'+iso)==False:os.system('mkdir app/static/COU_images/'+iso)
	country_names[iso]={'en':pycountry.countries.get(alpha_3=iso).name,'fr':french_cou_dict[iso]}




datasets=['CORDEX_BC','CMIP5_BC']

ind_dict={
	'tas':{'unit':'$^\circ C$','time_step':'monthly'},
	'pr':{'unit':'mm','time_step':'monthly'},
	'RX1':{'unit':'mm','time_step':'monthly'},
	'TXx':{'unit':'$^\circ C$','time_step':'monthly'},
	'year_RX5':{'unit':'mm','time_step':'yearly'},
}

indicator_dict={'fr':{
	'tas':'température',
	'pr':'précipitation',
	'RX1':'extrêmes humides (RX1day)',
	'TXx':'extrêmes de chaleur (TXx)',
	'year_RX5':'extrêmes humides de 5 jours (RX5day)',
	},
	'en':{
	'tas':'temperature',
	'pr':'precipitation',
	'RX1':'wet extremes (RX1day)',
	'TXx':'hot extremes (TXx)',
	'year_RX5':'5day wet extremes (RX5day)',
	}
}

season_dict={'fr':{
	'year':'** Annuel **',
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
	'year':'** Annual **',
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



ref_period  = [1986,2006]
proj_period = [2031,2051]

period_dict	= {
	'2020-2040':'2020-2040',
	'2040-2060':'2040-2060',
	'2':'2 deg global warming',
	'1.5':'1.5 deg global warming',
}

text_dict={'en':{

	'country_h':'Country',
	'country_txt':'',

	'warning':'Warning: ',
	'warning_txt':'The chosen region is smaller than 5 grid-cells. Please ',
	'reduced_inidicator_set_txt':"The chosen region is smaller than 5 grid-cells. We don't provide extreme indicators for such small regions!",

	'merge_page_h':'Add another region',
	'merge_page_txt':'Select a region you want to add to the chosen region.',
	'warning_merge_page_txt':'The chosen region is smaller than 5 grid-cells. Please select another region you want to merge the current region with.',

	'season_page_h':'Add another month',
	'season_page_txt':'Select a month that will be added to the season',

	'region_h':'Administrative Region',
	'region_txt':'Region for which the transient and annual cycle is presented. You can also ',

	'warming_lvl_h':'Global Warming Level',
	'warming_lvl_txt_1':'Global warming level above pre-industrial for which the regional response is presented. Alternatively you can use ',
	'warming_lvl_txt_2':'',
	'future_warming_lvl':'Future warming level',
	'ref_warming_lvl':'Reference warming level',

	'period_h':'Projection Period',
	'period_txt_1':'Time period for which projections are shown. Alternatively you can select ',
	'period_txt_2':'  for which the regional climate response will be displayed',

	'indicator_h':'Climate Indicator',
	'indicator_txt':'Climate indicators based on daily temperature and precipitation. Please find more information about the indicators ',

	'time_scale_h':'Time Scale',
	'time_scale_txt':'Select annual or monthly time scale or ',

	'ref_period':'Reference Period',
	'proj_period':'Projection Period',

},'fr':{
	'warning':'Avertissement!',
	'warning_txt':'La région choisie est plus petite que 5 grilles. Veuillez ',
	'reduced_inidicator_set_txt':"La région choisie est plus petite que 5 grilles. Nous ne fournissons pas d'indicateurs climatiques extrêmes pour cette région!",

	'merge_page_h':'Ajoutez une Région',
	'merge_page_txt':'Choisissez une région qui sera combiné avec la région actuelle.',
	'warning_merge_page_txt':'La région choisie est plus petite que 5 grilles. Veuillez choisir une autre région à combiner avec la région actuelle.',

	'season_page_h':'Ajoutez un mois',
	'season_page_txt':'Choisissez un mois qui sera ajouté à la saison',

	'region_h':'Région administrative',
	'region_txt':'Région pour laquelle le trajectoire et le cycle annuel sont présentés. Vous pouvet aussi ',

	'warming_lvl_h':'Niveau de Réchauffement Global',
	'warming_lvl_txt_1':'Niveau de Réchauffement Global pour lequel la réponse climatique régionale est présentée. Vous pouvez aussi utiliser des ',
	'warming_lvl_txt_2':' pour lesquelles les projections climatiques seront projetées.',
	'future_warming_lvl':'Niveau de réchauffement future',
	'ref_warming_lvl':'Niveau de réchauffement de référence',

	'period_h':'Période de Projection',
	'period_txt_1':'Périodes pour lesquelles les projections sont présentées. Comme les projections climatiques dépendent sur les scénarios d´émission, nous recommandons d´utiliser un ',
	'period_txt_2':' pour lequel la réponse climatique régionale va être présentée.',

	'country_h':'Pays',
	'country_txt':'Pour le moment seulement le Bénin et le Sénégal peuvent être sélectionné. La liste des pays sera bientôt élargie.',

	'indicator_h':'Indicateur Climatique',
	'indicator_txt':'Indicateurs climatiques basés sur des donnés quotidiennes de température et de précipitation. Pour le moment aucun indicateur de sécheresse est présenté. Veuillez considérer les projection de précipitation pour les analyses de sécheresses en gardant à l`esprit que l`évapotranspiration potentielle pourrait augmenter avec la température.',

	'time_scale_h':'Échelle temporelle',
	'time_scale_txt':'Les tendances projetés peuvent fortement dépendre de la saison. Veuillez choisir le mois le plus pertinent pour votre analyse ou ',

	'ref_period':'Période de Référence',
	'proj_period':'Période de Projection',

}
}

button_dict={'en':{
	'use_periods_0':'fixed time periods',
	'use_periods_1':'global warming levels',
	'merge_regions':'merge several regions.',
	'select_periods':'Select Periods',
	'define_season':'define a season.',
	'download_png':'Download png',
	'download_pdf':'Download pdf',
	'download_data':'Download data',
	'save_region':'Keep this Region',
	'save_season':'Keep this Season',

},'fr':{
	'use_periods_0':'périodes temporelles fixes',
	'use_periods_1':'niveau de réchauffement global',
	'merge_regions':'regrouper des régions.',
	'select_periods':'Choisir ces Périodes',
	'define_season':'définissez une saison.',
	'download_png':'Télécharger png',
	'download_pdf':'Télécharger pdf',
	'download_data':'Télécharger data',
	'save_region':'Garder cette Région',
	'save_season':'Garder cette Saison',
}
}

warming_lvl_dict={'en':{
	'ref':'1986-2005 (+0.61°C)',
	'1.5':'+1.5°C',
	'2.0':'+2.0°C',
},'fr':{
	'ref':'1986-2005 (+0.61°C)',
	'1.5':'+1.5°C',
	'2.0':'+2.0°C',
}
}

above_preindustrial={'en':'above preindustrial','fr':'au-dessus des niveaux préindustriels'}


print 'done with settings'
