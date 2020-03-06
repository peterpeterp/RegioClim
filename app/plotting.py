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


import os,sys,importlib,time
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.patches import Rectangle
import numpy as np
# from descartes import PolygonPatch
import cartopy.crs as ccrs
import cartopy
import xarray as xr

basepath='/Users/peterpfleiderer/Projects/regioClim_2020/'
try:
	os.chdir(basepath)
except:
	basepath='/home/tooli/regioClim/'

sys.path.append(basepath+'shaped_analysis/')
import shaped_analysis; importlib.reload(shaped_analysis)

from matplotlib import rc
rc('text', usetex=True)
plt.rcParams["font.family"] = "sans-serif"
plt.style.use('classic')

def create_new_plots(s,COU,refP,refP_clim,proP,refP_longname,refP_clim_longname,proP_longname,region,highlight_region,periods,periods_ewembi,lang,indicator_label,ind_dict,season_dict,out_format,method):

	start_time = time.time()
	COU=shaped_analysis.country_analysis(iso=s['country'], working_directory='/Users/peterpfleiderer/Projects/regioClim_2020/cou_data/'+s['country'])
	COU.load_shapefile()
	COU.load_mask()
	COU.load_data()
	COU.load_area_average()

	EWEMBI_plot='app/static/COU_images/'+s['country']+'/'+s['indicator']+'_EWEMBI_'+refP_clim+'_'+s['season']+'_'+lang+out_format
	if os.path.isfile(EWEMBI_plot)==False or True:
		ref = COU.select_data_gridded(time_format='monthly',tags={'scenario':'historical','experiment':'CORDEX','var_name':s['indicator']})
		ref = ref.loc[:,np.datetime64(str(periods[refP][0])+'-01-15'):np.datetime64(str(periods[refP][1])+'-12-31')]
		monthly = ref.groupby('time.month').mean('time')
		ref_seasonal = monthly.loc[:,season_dict[s['season']]['months']].mean(axis=1)
		to_plot = ref_seasonal.mean(axis=0)

		plt.close('all')
		x,y=ref_seasonal.lon.copy(),ref_seasonal.lat.copy()
		fig,ax = plt.subplots(nrows=1, figsize=(4,4*(len(y)/len(x))**0.5),subplot_kw={'projection': ccrs.PlateCarree()})
		ax.coastlines(resolution='10m');
		x-=np.diff(x,1)[0]/2.
		y-=np.diff(y,1)[0]/2.
		x=np.append(x,[x[-1]+np.diff(x,1)[0]])
		y=np.append(y,[y[-1]+np.diff(y,1)[0]])
		x,y=np.meshgrid(x,y)

		color_range=np.nanpercentile(to_plot,[10,90])
		if np.mean(color_range)==0:		cmap = ind_dict[s['indicator']]['cmap']['div']
		elif np.mean(color_range)<0:	cmap = ind_dict[s['indicator']]['cmap']['neg']
		elif np.mean(color_range)>0:	cmap = ind_dict[s['indicator']]['cmap']['pos']

		im = ax.pcolormesh(x,y,to_plot, cmap=cmap, vmin=color_range[0], vmax=color_range[1],  transform=ccrs.PlateCarree())
		for shape in COU._region_polygons.values():
		    ax.add_geometries(shape, ccrs.PlateCarree(), edgecolor='k',alpha=1,facecolor='none',linewidth=0.5,zorder=50)
		cb = plt.colorbar(im, ax=ax)
		tick_locator = mpl.ticker.MaxNLocator(nbins=5)
		cb.locator = tick_locator
		cb.update_ticks()
		cb.set_label(indicator_label, rotation=90)
		ax.set_title(str(u'' + refP_longname).replace('°','$^\circ$')+' '+season_dict[s['season']]['name'][lang],fontsize=10)
		plt.savefig(EWEMBI_plot, bbox_inches='tight')

	print('plotted '+str(time.time()-start_time))

	Projection_plot='app/static/COU_images/'+s['country']+'/'+s['indicator']+'_'+s["scenario"]+'_'+s["dataset"]+'_'+proP+'-'+refP+'_'+s['season']+'_'+lang+out_format
	if os.path.isfile(Projection_plot)==False or True:
		ref = COU.select_data_gridded(time_format='monthly',tags={'scenario':'historical','experiment':'CORDEX','var_name':s['indicator']})
		ref = ref.loc[:,np.datetime64(str(periods[refP][0])+'-01-15'):np.datetime64(str(periods[refP][1])+'-12-31')]
		monthly = ref.groupby('time.month').mean('time')
		ref_seasonal = monthly.loc[:,season_dict[s['season']]['months']].mean(axis=1)

		proj = COU.select_data_gridded(time_format='monthly',tags={'scenario':'rcp45','experiment':'CORDEX','var_name':s['indicator']})
		per = periods[refP]
		proj = proj.loc[:,np.datetime64(str(periods[proP][0])+'-01-15'):np.datetime64(str(periods[proP][1])+'-12-31')]
		monthly = proj.groupby('time.month').mean('time')
		proj_seasonal = monthly.loc[:,season_dict[s['season']]['months']].mean(axis=1)

		diff = proj_seasonal - ref_seasonal
		mean_diff = diff.mean('model')

		agree = mean_diff.copy()*0
		for model in diff.model.values:
		    agree += np.sign(mean_diff) == np.sign(diff.loc[model])

		agree.values[agree.values>2] = np.nan
		agree.values[agree.values<3] = 0.5

		plt.close('all')
		fig,ax = plt.subplots(nrows=1, figsize=(4,4*(agree.shape[0]/agree.shape[1])**0.5),subplot_kw={'projection': ccrs.PlateCarree()})
		ax.coastlines(resolution='10m');
		x,y=agree.lon.copy(),agree.lat.copy()
		x-=np.diff(x,1)[0]/2.
		y-=np.diff(y,1)[0]/2.
		x=np.append(x,[x[-1]+np.diff(x,1)[0]])
		y=np.append(y,[y[-1]+np.diff(y,1)[0]])
		x,y=np.meshgrid(x,y)

		color_range=np.nanpercentile(mean_diff,[10,90])
		if np.mean(color_range)==0:		cmap = ind_dict[s['indicator']]['cmap']['div']
		elif np.mean(color_range)<0:	cmap = ind_dict[s['indicator']]['cmap']['neg']
		elif np.mean(color_range)>0:	cmap = ind_dict[s['indicator']]['cmap']['pos']

		im = ax.pcolormesh(x,y,mean_diff, cmap=cmap, vmin=color_range[0], vmax=color_range[1],  transform=ccrs.PlateCarree())
		ax.pcolormesh(x,y,agree, cmap='Greys', vmin=0, vmax=1, transform=ccrs.PlateCarree())
		for shape in COU._region_polygons.values():
		    ax.add_geometries(shape, ccrs.PlateCarree(), edgecolor='k',alpha=1,facecolor='none',linewidth=0.5,zorder=50)
		cb = plt.colorbar(im, ax=ax)
		tick_locator = mpl.ticker.MaxNLocator(nbins=5)
		cb.locator = tick_locator
		cb.update_ticks()
		cb.set_label(indicator_label, rotation=90)

		ax.set_title(str(u'' + proP_longname+' vs '+refP_longname).replace('°','$^\circ$')+' '+season_dict[s['season']]['name'][lang]+' RCP4.5',fontsize=10)
		plt.savefig(Projection_plot, bbox_inches='tight')

	print('plotted '+str(time.time()-start_time))

	transient_plot='app/static/COU_images/'+s['country']+'/'+s['indicator']+'_'+s["dataset"]+'_'+region+'_'+s['season']+'_transient'+'_'+lang+out_format
	if os.path.isfile(transient_plot)==False or True:
		plt.close('all')
		tmp = COU.select_data('monthly',tags={'scenario':'historical','experiment':'CORDEX','var_name':s['indicator'],'region':s['region'],'mask_style':'latWeight'})
		hist = tmp[:,np.all(np.isnan(tmp), axis=0)==False]

		tmp = COU.select_data('monthly',tags={'scenario':'rcp45','experiment':'CORDEX','var_name':s['indicator'],'region':s['region'],'mask_style':'latWeight'})
		proj = tmp[:,np.all(np.isnan(tmp), axis=0)==False]

		tmp = xr.concat((hist,proj), dim='time')

		relMon = np.zeros(tmp.time.shape[0], np.bool)
		for mon in season_dict[s['season']]['months']:
			relMon[tmp.time.dt.month.values == mon] = True

		tmp = tmp[:,relMon]
		tmp = tmp.groupby('time.year').mean('time')

		ens = tmp.copy()
		for model in tmp.model:
			ens.loc[model] = tmp.loc[model].rolling(year=20, center=True).mean()

		fig,ax = plt.subplots(nrows=1, figsize=(5,4))
		ax.plot(ens.year.values,ens.mean('model'), color='green')
		ax.fill_between(ens.year.values,ens.min('model'),ens.max('model'), alpha=0.2, color='green')

		ax.set_ylabel(indicator_label)
		ax.set_xlabel('year')
		ax.set_title(u''+COU._region_names[s['region']].replace('_',' ')+' '+season_dict[s['season']]['name'][lang].replace('*','')+' RCP4.5',fontsize=12)
		plt.savefig(transient_plot, bbox_inches='tight')

		print('plotted '+str(time.time()-start_time))


	annual_cycle_plot='app/static/COU_images/'+s['country']+'/'+s['indicator']+'_'+s["dataset"]+'_'+region+'_annual_cycle_'+proP+'-'+refP+'_'+lang+out_format
	if os.path.isfile(annual_cycle_plot)==False or True:
		plt.close('all')
		tmp = COU.select_data('monthly',tags={'scenario':'historical','experiment':'EWEMBI','model':'EWEMBI','var_name':'pr','region':s['region'],'mask_style':'latWeight'})
		ewembi = tmp.loc[np.datetime64(str(1986)+'-01-15'):np.datetime64(str(2005)+'-12-31')]
		ewembi = ewembi.groupby('time.month').mean('time')

		tmp = COU.select_data('monthly',tags={'scenario':'historical','experiment':'CORDEX','var_name':'pr','region':s['region'],'mask_style':'latWeight'})
		hist = tmp[:,np.all(np.isnan(tmp), axis=0)==False]
		hist = hist.loc[:,np.datetime64(str(1986)+'-01-15'):np.datetime64(str(2005)+'-12-31')]
		hist = hist.groupby('time.month').mean('time')

		tmp = COU.select_data('monthly',tags={'scenario':'rcp45','experiment':'CORDEX','var_name':'pr','region':s['region'],'mask_style':'latWeight'})
		proj = tmp[:,np.all(np.isnan(tmp), axis=0)==False]
		proj = proj.loc[:,np.datetime64(str(2040)+'-01-15'):np.datetime64(str(2060)+'-12-31')]
		proj = proj.groupby('time.month').mean('time')

		fig,axes=plt.subplots(nrows=2,ncols=1,sharex=True,figsize=(5,4))
		ax = axes[0]
		ax.plot(ewembi.month, np.mean(hist,axis=0), color='green', label='model data')
		ax.fill_between(ewembi.month,np.min(hist,axis=0),np.max(hist,axis=0), alpha=0.2, color='green')
		ax.plot(ewembi.month, ewembi.values, color='k', label='observations (EWEMBI)')
		leg = axes[0].legend(loc='best',fancybox=True,fontsize=10)
		leg.get_frame().set_alpha(0.3)
		ax.set_title(str(u''+COU._region_names[s['region']].replace('_',' ')+' ' + refP_longname).replace('°','$^\circ$'),fontsize=10)

		ax = axes[1]
		ax.plot(ewembi.month, np.mean(proj-hist,axis=0), label='projected change', color='green')
		ax.fill_between(ewembi.month,np.min(proj-hist,axis=0),np.max(proj-hist,axis=0), alpha=0.2, color='green')
		leg = axes[1].legend(loc='best',fancybox=True,fontsize=10)
		leg.get_frame().set_alpha(0.3)
		ax.set_title(str(u'' + proP_longname+' vs '+refP_longname).replace('°','$^\circ$')+' RCP4.5',fontsize=10)

		ax.set_xticks(range(1,13))
		ax.set_xticklabels(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'])
		plt.annotate(indicator_label, xy=(0.01,0.5), xycoords='figure fraction', rotation=90)
		plt.savefig(annual_cycle_plot, bbox_inches='tight')

		print('plotted '+str(time.time()-start_time))


	return EWEMBI_plot, Projection_plot, transient_plot, annual_cycle_plot, 'bla'


# def EWEMBI_plot_func(s,COU,refP,refP_clim,proP,refP_longname,refP_clim_longname,proP_longname,region,highlight_region,periods,periods_ewembi,lang,indicator_label,season_dict,out_format,method):
#   # EWEMBI map
#   ewembi=COU.selection([s['indicator'],'EWEMBI'])
#   EWEMBI_plot='app/static/COU_images/'+s['country']+'/'+s['indicator']+'_EWEMBI_'+refP_clim+'_'+s['season']+'_'+lang+out_format
#   if os.path.isfile(EWEMBI_plot)==False:
#     COU.period_statistics(periods=periods_ewembi,selection=ewembi,ref_name=refP_clim,method=method)
#     if np.isnan(np.nanmean(ewembi[0].period[method][s['season']][refP_clim])):
#       return('no_plot')
#     else:
#       asp=(float(len(ewembi[0].lon))/float(len(ewembi[0].lat)))**0.5
#       fig,ax=plt.subplots(nrows=1,ncols=1,figsize=(3*asp+2.5,3/asp+1),subplot_kw={'projection': ccrs.PlateCarree()})
#       ewembi[0].display_map(out_file=EWEMBI_plot,
#         ax=ax,
#         method=method,
#         period=refP_clim,
#         season=s['season'],
#         color_label=indicator_label,
#         )
#
#       if s['season']=='year':
#         plt.title(refP_clim_longname.replace('°','$^\circ$'),fontsize=10)
#       if s['season']!='year':
#         plt.title(refP_clim_longname.replace('°','$^\circ$')+' '+season_dict[lang][s['season']],fontsize=10)
#
#       plt.savefig(EWEMBI_plot)
#       if out_format=='_small.png':plt.savefig(EWEMBI_plot)
#       if out_format=='_large.png':plt.savefig(EWEMBI_plot,dpi=300)
#       if out_format=='.pdf':plt.savefig(EWEMBI_plot, format='pdf', dpi=1000)
#   plt.clf()
#   return(EWEMBI_plot)
#
#
# def Projection_plot_func(s,COU,refP,refP_clim,proP,refP_longname,refP_clim_longname,proP_longname,region,highlight_region,periods,periods_ewembi,lang,indicator_label,season_dict,out_format,method):
#   # projection
#   ens_selection=COU.selection([s['indicator'],s['dataset']])
#   ens_mean=COU.selection([s['indicator'],s['dataset'],'ensemble_mean'])[0]
#   Projection_plot='app/static/COU_images/'+s['country']+'/'+s['indicator']+'_'+s["scenario"]+'_'+s["dataset"]+'_'+proP+'-'+refP+'_'+s['season']+'_'+lang+out_format
#   if os.path.isfile(Projection_plot)==False:
#     COU.period_statistics(periods=periods,selection=ens_selection,ref_name=refP,method=method)
#     COU.period_model_agreement(ref_name=refP)
#     asp=(float(len(ens_selection[0].lon))/float(len(ens_selection[0].lat)))**0.5
#     fig,ax=plt.subplots(nrows=1,ncols=1,figsize=(3*asp+2.5,3/asp+1),subplot_kw={'projection': ccrs.PlateCarree()})
#     ens_mean.display_map(ax=ax,
#       period='diff_'+proP+'-'+refP,
#       method=method,
#       season=s['season'],
#       color_label=indicator_label,
#       )
#
#
#     title = u'' + proP_longname+' vs '+refP_longname
#     if s['season']=='year':
#       plt.title(title.replace('°','$^\circ$')+' RCP4.5',fontsize=10)
#     if s['season']!='year':
#       plt.title(title.replace('°','$^\circ$')+' '+season_dict[lang][s['season']]+' RCP4.5',fontsize=10)
#
#     if out_format=='_small.png':plt.savefig(Projection_plot)
#     if out_format=='_large.png':plt.savefig(Projection_plot,dpi=300)
#     if out_format=='.pdf':plt.savefig(Projection_plot, format='pdf', dpi=1000)
#   plt.clf()
#   return(Projection_plot)
#
# def transient_plot_func(s,COU,refP,refP_clim,proP,refP_longname,refP_clim_longname,proP_longname,region,highlight_region,periods,periods_ewembi,lang,indicator_label,season_dict,out_format,method):
#   # transient
#   #ewembi=COU.selection([s['indicator'],'EWEMBI'])
#
#   transient_plot='app/static/COU_images/'+s['country']+'/'+s['indicator']+'_'+s["dataset"]+'_'+region+'_'+s['season']+'_transient'+'_'+lang+out_format
#   if os.path.isfile(transient_plot)==False:
#     ens_selection=COU.selection([s['indicator'],s['dataset']])
#     ens_mean=COU.selection([s['indicator'],s['dataset'],'ensemble_mean'])[0]
#
#     if region != s['country']:COU.create_mask_admin(ens_mean.raw_file,s['indicator'],regions=[region])
#     COU.area_average('lat_weighted',overwrite=False,selection=ens_selection,regions=[region])#+ewembi
#     COU.unit_conversions(ens_selection)
#
#     fig,ax=plt.subplots(nrows=1,ncols=1,figsize=(5,4))
#     message=ens_mean.plot_transients(season=s['season'],region=region,running_mean_years=20,ax=ax,title='',ylabel=None,label='model data',color='green',shading_range=[0,100],x_range=[1960,2090],show_all_models=False,method=method)
#     #message=ewembi[0].plot_transients(season=s['season'],region=region,running_mean_years=20,ax=ax,title='',ylabel=None,label='observations (EWEMBI)',color='black',x_range=[1960,2090])
#     print(message,s['season'])
#     if message==1:
#       ax.set_ylabel(u''+indicator_label)
#       print(indicator_label)
#       #leg = plt.legend(loc='best',fancybox=True,fontsize=10)
#       #leg.get_frame().set_alpha(0.3)
#       if s['season']=='year':
#         plt.title(u''+COU._region_names[s['region']].replace('**','').replace('_',' ')+' RCP4.5',fontsize=12)
#       if s['season']!='year':
#         plt.title(u''+COU._region_names[s['region']].replace('**','').replace('_',' ')+' '+season_dict[lang][s['season']]+' RCP4.5',fontsize=12)
#       #plt.text(2100,60,'Climate Analytics',horizontalalignment='right',fontsize=7)
#       #plt.text(-0.1, 0.,'climate anaylics',horizontalalignment='left',verticalalignment='bottom',transform = ax.transAxes)
#       fig.tight_layout()
#       if out_format=='_small.png':plt.savefig(transient_plot)
#       if out_format=='_large.png':plt.savefig(transient_plot,dpi=300)
#       if out_format=='.pdf':plt.savefig(transient_plot, format='pdf', dpi=1000)
#   plt.clf()
#   return(transient_plot)
#
# def annual_cycle_plot_func(s,COU,refP,refP_clim,proP,refP_longname,refP_clim_longname,proP_longname,region,highlight_region,periods,periods_ewembi,lang,indicator_label,season_dict,out_format,method):
#   # annual cycle
#   ewembi=COU.selection([s['indicator'],'EWEMBI'])
#   ens_selection=COU.selection([s['indicator'],s['dataset']])
#   ens_mean=COU.selection([s['indicator'],s['dataset'],'ensemble_mean'])[0]
#   annual_cycle_plot='app/static/COU_images/'+s['country']+'/'+s['indicator']+'_'+s["dataset"]+'_'+region+'_annual_cycle_'+proP+'-'+refP+'_'+lang+out_format
#   if os.path.isfile(annual_cycle_plot)==False:
#     if ewembi[0].time_format=='yearly':
#       return('no_plot')
#     else:
      # if region != s['country']:COU.create_mask_admin(ewembi[0].raw_file,s['indicator'],regions=[region])
      # COU.area_average('lat_weighted',overwrite=False,selection=ens_selection+ewembi,regions=[region])
      # COU.unit_conversions(ens_selection+ewembi)
	  #
      # COU.annual_cycle(periods=periods_ewembi,selection=ewembi,regions=[region])
      # COU.annual_cycle(periods=periods_ewembi,selection=ens_selection,ref_name=refP,regions=[region])
      # COU.annual_cycle(periods=periods,selection=ens_selection,ref_name=refP,regions=[region])
      # COU.annual_cycle_ensemble_mean(regions=[region])
	  #
      # fig,ax=plt.subplots(nrows=2,ncols=1,sharex=True,figsize=(5,4))
	  #
      # if np.isnan(np.nanmean(ewembi[0].annual_cycle['lat_weighted'][region][refP_clim]))==False:
      #   ewembi[0].plot_annual_cycle(period=refP_clim,region=region,ax=ax[0],title='',ylabel='  ',label='observations (EWEMBI)',color='black',xlabel=False)
	  #
      # ens_mean.plot_annual_cycle(period=refP_clim,region=region,ax=ax[0],title='',ylabel='  ',label='model data',color='green',xlabel=False,shading_range=[0,100])
      # leg = ax[0].legend(loc='best',fancybox=True,fontsize=10)
      # leg.get_frame().set_alpha(0.3)
	  #
      # print(COU._region_names[s['region']])
      # print(COU._region_names[s['region']].encode('utf8'))
      # print(COU._region_names[s['region']].decode('utf8'))
      # print(s['region'])
      # ax[0].set_title(u''+COU._region_names[s['region']].replace('**','').replace('_',' ')+' '+refP_clim_longname,fontsize=12)
	  #
      # ens_mean.plot_annual_cycle(period='diff_'+proP+'-'+refP,region=region,ax=ax[1],title='',ylabel='  ',label='projected change',color='green',shading_range=[0,100])
      # ax[1].plot([0,1],[0,0],color='k')
      # leg = ax[1].legend(loc='best',fancybox=True,fontsize=10)
      # leg.get_frame().set_alpha(0.3)
	  #
      # title = u''+proP_longname+' vs '+refP_longname+' RCP4.5'
      # ax[1].set_title(title.replace('°','$^\circ$'),fontsize=12)
	  #
      # ylab_ax=fig.add_axes([0.0,0.0,1,1])
      # ylab_ax.axis([0, 1, 0, 1])
      # ylab_ax.axis('off')
      # ylab_ax.text(0.05,0.5,u''+indicator_label,rotation=90,verticalalignment='center')
      # fig.subplots_adjust(left=0.175, bottom=0.125, right=0.95, top=0.90, wspace=0, hspace=0.2)
	  #
      # if out_format=='_small.png':plt.savefig(annual_cycle_plot)
      # if out_format=='_large.png':plt.savefig(annual_cycle_plot,dpi=300)
      # if out_format=='.pdf':plt.savefig(annual_cycle_plot, format='pdf', dpi=1000)
#   plt.clf()
#   return(annual_cycle_plot)
#
#
# def localisation_overview(s,COU,refP,refP_clim,proP,refP_longname,refP_clim_longname,proP_longname,region,highlight_region,periods,periods_ewembi,lang,indicator_label,season_dict,out_format,method):
#   overview_plot='app/static/COU_images/'+s['country']+'/overview_'+highlight_region+out_format
#   if os.path.isfile(overview_plot)==False:
#     ewembi=COU.selection([s['indicator'],'EWEMBI'])[0]
#     lon,lat=ewembi.lon,ewembi.lat
#     fig,ax=plt.subplots(nrows=1,ncols=1,figsize=(5,5),subplot_kw={'projection': ccrs.PlateCarree()})
#     ewembi.plot_map(to_plot=None,limits=[min(lon)-10,max(lon)+10,min(lat)-10,max(lat)+10],ax=ax,color_bar=False)
#
#
#     # patch = PolygonPatch(COU._adm_polygons[s['country']], facecolor=[0,0,0.5], edgecolor=[0,0,0], alpha=0.7, zorder=2)
#     # ax.add_patch(patch)
#
#     # patch = PolygonPatch(COU._adm_polygons[highlight_region], facecolor='orange', edgecolor=[0,0,0], alpha=0.7, zorder=2)
#     # ax.add_patch(patch)
#
#
#     if out_format=='_small.png':plt.savefig(overview_plot)
#     if out_format=='_large.png':plt.savefig(overview_plot,dpi=300)
#     if out_format=='.pdf':plt.savefig(overview_plot, format='pdf', dpi=1000)
#   plt.clf()
#   return(overview_plot)
