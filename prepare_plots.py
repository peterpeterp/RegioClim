import sys,glob,os,pickle
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import pandas as pd
import matplotlib.pylab as plt

sys.path.append('/Users/peterpfleiderer/Documents/Projects/country_analysis/country_analysis_scripts/')
try:del sys.modules['country_analysis'] 
except:pass
from country_analysis import country_analysis,plot_map
sys.path.append('/Users/peterpfleiderer/Documents/')

os.chdir('/Users/peterpfleiderer/Documents/Projects')

COU={}

COU['SEN']=country_analysis('SEN','/Users/peterpfleiderer/Documents/Projects/country_analysis/SEN/',seasons={'year':range(1,13),'wet':[5,6,7,8,9,10],'dry':[11,12,1,2,3,4]})
COU['SEN'].load_data()
COU['SEN'].data_summary()
COU['SEN'].unit_conversions()


COU['BEN']=country_analysis('BEN','/Users/peterpfleiderer/Documents/Projects/country_analysis/BEN/',seasons={'year':range(1,13),'wet':[5,6,7,8,9,10],'dry':[11,12,1,2,3,4]})
COU['BEN'].load_data()
COU['BEN'].data_summary()
COU['BEN'].unit_conversions()

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

os.chdir('/Users/peterpfleiderer/Documents/Projects/projection_sharing_static/app/')

periods={'ref':[1986,2006],'2020-2040':[2020,2040],'2040-2060':[2040,2060]}
ref_period_name='1986-2006'

overwrite=True


for country in COU.keys():
  for scenario in ['rcp45']:
    for indicator in indicator_dict.keys():
      cordex=COU[country].selection([indicator,scenario,'CORDEX_BC','ensemble_mean'])[0]
      ewembi=COU[country].selection([indicator,'EWEMBI'])[0]

      for proj_period in ['2020-2040','2040-2060']:

        if cordex.time_format=='monthly':   seasons=['wet','year','dry']
        if cordex.time_format=='yearly':    seasons=['year']

        for season in seasons:
          # cordex projection
          CORDEX_BC_plot='static/images/'+country+'/'+indicator+'_'+scenario+'_CORDEX_BC_'+proj_period+'-'+ref_period_name+'_'+season+'.png'
          if os.path.isfile(CORDEX_BC_plot)==False or overwrite:
            COU[country].period_averages(periods=periods,filters=[indicator,scenario,'CORDEX_BC'])
            COU[country].model_agreement()
            cordex.display_map(period='diff_'+proj_period+'-ref',season=season,out_file=CORDEX_BC_plot,polygons=COU[country]._adm_polygons,title='projections',color_label=indicator_dict[indicator]['ylabel'])

          # ewembi map
          EWEMBI_plot='static/images/'+country+'/'+indicator+'_EWEMBI_'+ref_period_name+'_'+season+'.png'
          if os.path.isfile(EWEMBI_plot)==False or overwrite:
            COU[country].period_averages(periods=periods,filters=[indicator,'EWEMBI'])
            ewembi.display_map(period='ref',season=season,out_file=EWEMBI_plot,polygons=COU[country]._adm_polygons,title='observations',color_label=indicator_dict[indicator]['ylabel'])

          # cordex detail
          CORDEX_BC_plot_detail='static/images/'+country+'/'+indicator+'_'+scenario+'_CORDEX_BC_'+proj_period+'-'+ref_period_name+'_'+season+'_detials.png'
          if os.path.isfile(CORDEX_BC_plot_detail)==False or overwrite:
            COU[country].period_averages(periods=periods,filters=[indicator,scenario,'CORDEX_BC'])
            COU[country].model_agreement()
            fig,axes=plt.subplots(nrows=1,ncols=5,figsize=(6,4))
            axes=axes.flatten()
            selection=COU[country].selection([indicator,scenario,'CORDEX_BC'])
            for model,i in zip(selection,range(len(selection))):
              print model.period.keys()
              im=model.display_map(period='diff_'+proj_period+'-ref',season=season,ax=axes[i],title=model.model,color_bar=False)
            cbar_ax=fig.add_axes([0.3,0.2,0.4,0.6])
            cbar_ax.axis('off')
            cb=fig.colorbar(im,orientation='horizontal',label='')
            plt.savefig(CORDEX_BC_plot_detail)


      for region in COU[country]._masks['360x720_lat_89.75_-89.75_lon_-179.75_179.75']['lat_weighted'].keys():
        transient_plot='static/images/'+country+'/'+indicator+'_'+region+'_transient.png'
        transient_plot='static/images/'+country+'/'+indicator+'_'+region+'_transient.png'
        if os.path.isfile(transient_plot)==False or overwrite:
          fig,ax=plt.subplots(nrows=1,ncols=1,figsize=(5,4))
          cordex.plot_transients(region=region,running_mean_years=20,ax=ax,title='',ylabel=None,label='projection',color='red')
          ewembi.plot_transients(region=region,running_mean_years=20,ax=ax,title='',ylabel=None,label='observation',color='green')

          ax.set_ylabel(indicator_dict[indicator]['ylabel'])
          ax.set_title('transient plot')
          plt.legend(loc='best')
          plt.savefig(transient_plot)

        for proj_period in ['2020-2040','2040-2060']:
          if cordex.time_format=='monthly':
            annual_cycle_plot='static/images/'+country+'/'+indicator+'_'+region+'_annual_cycle_'+proj_period+'-'+ref_period_name+'.png'
            if os.path.isfile(annual_cycle_plot)==False or overwrite:
              fig,ax=plt.subplots(nrows=1,ncols=1,figsize=(5,4))
              cordex.plot_annual_cycle(period=periods[proj_period],region=region,ax=ax,title='',ylabel=None,label='projection',color='red')
              ewembi.plot_annual_cycle(period=periods['ref'],region=region,ax=ax,title='',ylabel=None,label='observation',color='green')
              ax.set_title('annual cycle plot')
              ax.set_ylabel(indicator_dict[indicator]['ylabel'])
              plt.legend(loc='best')
              plt.savefig(annual_cycle_plot)

