import sys,glob,os,pickle
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import pandas as pd
import matplotlib.pylab as plt

from matplotlib import rc
rc('text', usetex=True)

sys.path.append('/Users/peterpfleiderer/Documents/Projects/country_analysis/country_analysis_scripts/')
try:del sys.modules['country_analysis'] 
except:pass
from country_analysis import country_analysis
sys.path.append('/Users/peterpfleiderer/Documents/')

os.chdir('/Users/peterpfleiderer/Documents/Projects')


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

periods={'ref':[1986,2006],'2020-2040':[2020,2040],'2040-2060':[2040,2060]}
ref_period_name='1986-2006'

COU={}
COU['SEN']=country_analysis('SEN','/Users/peterpfleiderer/Documents/Projects/country_analysis/SEN/',seasons={'year':range(1,13),'wet':[5,6,7,8,9,10],'dry':[11,12,1,2,3,4]})
COU['BEN']=country_analysis('BEN','/Users/peterpfleiderer/Documents/Projects/country_analysis/BEN/',seasons={'year':range(1,13),'wet':[5,6,7,8,9,10],'dry':[11,12,1,2,3,4]})

for country in COU.keys():
  COU[country].load_data()
  COU[country].data_summary()
  COU[country].unit_conversions()
  COU[country].period_averages(periods={'ref':[1986,2006]},filters=['EWEMBI'])
  COU[country].annual_cycle(periods={'ref':[1986,2006]},filters=['EWEMBI'])
  COU[country].period_averages(periods=periods,filters=['CORDEX_BC'])
  COU[country].annual_cycle(periods=periods,filters=['CORDEX_BC'])
  COU[country].get_warming_slices(GMT_path='wlcalculator/data/cmip5_ver002/',model_real_name={'IPSL':'ipsl-cm5a-lr','HADGEM2':'hadgem2-es','ECEARTH':'hadgem2-es','MPIESM':'mpi-esm-lr'})
  COU[country].period_averages(periods=COU[country]._warming_slices,filters=['CORDEX_BC'])
  COU[country].annual_cycle(periods=COU[country]._warming_slices,filters=['CORDEX_BC'])

  COU[country].period_model_agreement()
  COU[country].annual_cycle_ensemble_mean()


os.chdir('/Users/peterpfleiderer/Documents/Projects/projection_sharing/app/')

overwrite=True

figsizes={
  'BEN':{'bias_correction':(6,5),'detail':(7,4)},
  'SEN':{'bias_correction':(7,3.5),'detail':(8,4)},
}


# # reference and difference map
# for country in COU.keys():
#   for scenario in ['rcp45']:
#     for indicator in indicator_dict.keys():
#       cordex=COU[country].selection([indicator,scenario,'CORDEX_BC','ensemble_mean'])[0]
#       ewembi=COU[country].selection([indicator,'EWEMBI'])[0]
#       if cordex.time_format=='monthly':   seasons=['wet','year','dry']
#       if cordex.time_format=='yearly':    seasons=['year']
      
#       for season in seasons:
#         # ewembi map
#         EWEMBI_plot='static/images/'+country+'/'+indicator+'_EWEMBI_'+ref_period_name+'_'+season+'.png'
#         if os.path.isfile(EWEMBI_plot)==False or overwrite:
#           ewembi.display_map(period='ref',
#             season=season,
#             out_file=EWEMBI_plot,
#             title='observations',
#             color_label=indicator_dict[indicator]['ylabel'])

#         for proj_period in ['2020-2040','2040-2060','2','1.5','2.5']:
#           # cordex projection
#           CORDEX_BC_plot='static/images/'+country+'/'+indicator+'_'+scenario+'_CORDEX_BC_'+proj_period+'-'+ref_period_name+'_'+season+'.png'
#           if os.path.isfile(CORDEX_BC_plot)==False or overwrite:
#             cordex.display_map(period='diff_'+proj_period+'-ref',
#               season=season,
#               out_file=CORDEX_BC_plot,
#               title='projections',
#               color_label=indicator_dict[indicator]['ylabel'])



# detail map
for country in COU.keys():
  for scenario in ['rcp45']:
    for indicator in indicator_dict.keys():
      cordex=COU[country].selection([indicator,scenario,'CORDEX_BC','ensemble_mean'])[0]
      ewembi=COU[country].selection([indicator,'EWEMBI'])[0]
      if cordex.time_format=='monthly':   seasons=['wet','year','dry']
      if cordex.time_format=='yearly':    seasons=['year']
      
      for season in seasons:
        for proj_period in ['2020-2040','2040-2060','2','1.5','2.5']:
          # cordex detail
          CORDEX_BC_plot_detail='static/images/'+country+'/'+indicator+'_'+scenario+'_CORDEX_BC_'+proj_period+'-'+ref_period_name+'_'+season+'_detials.png'
          if os.path.isfile(CORDEX_BC_plot_detail)==False or overwrite:
            fig,axes=plt.subplots(nrows=1,ncols=5,figsize=figsizes[country]['detail'])
            axes=axes.flatten()
            ensemble,ensemble_mean=COU[country].find_ensemble([indicator,scenario,'CORDEX_BC'])
            im,color_range=ensemble_mean.display_map(period='diff_'+proj_period+'-ref',season=season,ax=axes[4],title=ensemble_mean.model,color_bar=False)
            for model,i in zip(ensemble.values(),range(len(ensemble.values()))):
              im,color_range=model.display_map(period='diff_'+proj_period+'-ref',season=season,ax=axes[i],title=model.model,color_bar=False,color_range=color_range)
            if im!=0:
              cbar_ax=fig.add_axes([0.3,0.1,0.4,0.6])
              cbar_ax.axis('off')
              cb=fig.colorbar(im,orientation='horizontal',label=indicator_dict[indicator]['ylabel'])
              plt.savefig(CORDEX_BC_plot_detail)



# bias correction check
for country in COU.keys():
  for indicator in indicator_dict.keys():
    ensemble,ensemble_mean=COU[country].find_ensemble([indicator,'CORDEX_BC'])
    ewembi=COU[country].selection([indicator,'EWEMBI'])[0]
    if ensemble_mean.time_format=='monthly':   seasons=['wet','year','dry']
    if ensemble_mean.time_format=='yearly':    seasons=['year']
    for season in seasons:
      bias_corretion_check='static/images/'+country+'/'+indicator+'_BC_check_'+season+'.png'
      if os.path.isfile(bias_corretion_check)==False or overwrite:
        fig,axes=plt.subplots(nrows=1,ncols=4,figsize=figsizes[country]['bias_correction'])
        axes=axes.flatten()
        for model,i in zip(ensemble.values(),range(len(ensemble.values()))):
          to_plot=(model.period[season]['ref']-ewembi.period[season]['ref'])*100./ewembi.period[season]['ref']
          im,color_range=COU[country].plot_map(to_plot=to_plot,lat=ewembi.lat,lon=ewembi.lon,ax=axes[i],title=model.model,color_bar=False,color_range=[-10,10],color_palette=plt.cm.PiYG_r)
        if im!=0:
          cbar_ax=fig.add_axes([0.3,0.2,0.4,0.6])
          cbar_ax.axis('off')
          cb=fig.colorbar(im,orientation='horizontal',label=indicator_dict[indicator]['long_name']+' [$\%$]')
          plt.savefig(bias_corretion_check)


# # transients
# for country in COU.keys():
#   for scenario in ['rcp45']:
#     for indicator in indicator_dict.keys():
#       cordex=COU[country].selection([indicator,scenario,'CORDEX_BC','ensemble_mean'])[0]
#       ewembi=COU[country].selection([indicator,'EWEMBI'])[0]

#       for region in COU[country]._masks['360x720_lat_89.75_-89.75_lon_-179.75_179.75']['lat_weighted'].keys():
#         for season in seasons:
#           transient_plot='static/images/'+country+'/'+indicator+'_'+region+'_'+season+'_transient.png'
#           transient_plot='static/images/'+country+'/'+indicator+'_'+region+'_'+season+'_transient.png'
#           if os.path.isfile(transient_plot)==False or overwrite:
#             fig,ax=plt.subplots(nrows=1,ncols=1,figsize=(5,4))
#             message=cordex.plot_transients(season=season,region=region,running_mean_years=20,ax=ax,title='',ylabel=None,label='projection',color='red')
#             message=ewembi.plot_transients(season=season,region=region,running_mean_years=20,ax=ax,title='',ylabel=None,label='observation',color='green')

#             if message==1:
#               ax.set_ylabel(indicator_dict[indicator]['ylabel'])
#               ax.set_title('transient plot')
#               plt.legend(loc='best')
#               plt.savefig(transient_plot)


# # annual cycle
# for country in COU.keys():
#   for scenario in ['rcp45']:
#     for indicator in indicator_dict.keys():
#       cordex=COU[country].selection([indicator,scenario,'CORDEX_BC','ensemble_mean'])[0]
#       ewembi=COU[country].selection([indicator,'EWEMBI'])[0]
#       for region in COU[country]._masks['360x720_lat_89.75_-89.75_lon_-179.75_179.75']['lat_weighted'].keys():
#         for proj_period in ['2020-2040','2040-2060','2','1.5']:
#           if cordex.time_format=='monthly':
#             annual_cycle_plot='static/images/'+country+'/'+indicator+'_'+region+'_annual_cycle_'+proj_period+'-'+ref_period_name+'.png'
#             if os.path.isfile(annual_cycle_plot)==False or overwrite:
#               fig,ax=plt.subplots(nrows=1,ncols=1,figsize=(5,4))
#               cordex.plot_annual_cycle(period=proj_period,region=region,ax=ax,title='',ylabel=None,label='projection',color='red')
#               ewembi.plot_annual_cycle(period='ref',region=region,ax=ax,title='',ylabel=None,label='observation',color='green')
#               ax.set_title('annual cycle plot')
#               ax.set_ylabel(indicator_dict[indicator]['ylabel'])
#               plt.legend(loc='best')
#               plt.savefig(annual_cycle_plot)
              


# # annual cycle alternative
# for country in COU.keys():
#   for scenario in ['rcp45']:
#     for indicator in indicator_dict.keys():
#       cordex=COU[country].selection([indicator,scenario,'CORDEX_BC','ensemble_mean'])[0]
#       ewembi=COU[country].selection([indicator,'EWEMBI'])[0]
#       for region in COU[country]._masks['360x720_lat_89.75_-89.75_lon_-179.75_179.75']['lat_weighted'].keys():
#         for proj_period in ['2020-2040','2040-2060','2','1.5']:
#           if cordex.time_format=='monthly':
#             annual_cycle_plot='static/images/'+country+'/'+indicator+'_'+region+'_annual_cycle_'+proj_period+'-'+ref_period_name+'.png'
#             if os.path.isfile(annual_cycle_plot)==False or overwrite:
#               fig,axes=plt.subplots(nrows=2,ncols=1,figsize=(5,4))
#               axes=axes.flatten()
#               cordex.plot_annual_cycle(period='diff_'+proj_period+'-ref',region=region,ax=axes[0],title='',ylabel=None,label='projection',color='red')
#               ewembi.plot_annual_cycle(period='ref',region=region,ax=axes[1],title='',ylabel=None,label='observation',color='green')
#               ax.set_title('annual cycle plot')
#               ax.set_ylabel(indicator_dict[indicator]['ylabel'])
#               plt.legend(loc='best')
#               plt.savefig(annual_cycle_plot)













