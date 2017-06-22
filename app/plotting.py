# -*- coding: utf-8 -*-
import os
import matplotlib.pyplot as plt

from matplotlib import rc
rc('text', usetex=True)
plt.rcParams["font.family"] = "sans-serif"
plt.style.use('classic')

def EWEMBI_plot_func(s,COU,refP,proP,region,periods,lang,indicator_label,lang_dict,out_format,highlight_region=None):
  # EWEMBI map
  ewembi=COU.selection([s['indicator'],'EWEMBI'])
  EWEMBI_plot='app/static/images/'+s['country']+'/'+s['indicator']+'_EWEMBI_ref_'+s['season']+'_'+region+out_format
  if os.path.isfile(EWEMBI_plot)==False:
    COU.period_statistics(periods={refP:s['ref_period']},selection=ewembi,ref_name=refP)
    fig,ax=plt.subplots(nrows=1,ncols=1,figsize=(4,3))
    ewembi[0].display_map(out_file=EWEMBI_plot,
      ax=ax,
      highlight_region=highlight_region,
      period=refP,
      season=s['season'],
      color_label=indicator_label,
      )
    plt.title(refP.replace('to','-')+' '+lang_dict[lang][s['season']],fontsize=10)
    plt.savefig(EWEMBI_plot)
    if out_format=='_small.png':plt.savefig(EWEMBI_plot)
    if out_format=='_large.png':plt.savefig(EWEMBI_plot,dpi=300) 
    if out_format=='.pdf':plt.savefig(EWEMBI_plot, format='pdf', dpi=1000) 
  return(EWEMBI_plot)

def Projection_plot_func(s,COU,refP,proP,region,periods,lang,indicator_label,lang_dict,out_format,highlight_region=None):
  # projection
  ens_selection=COU.selection([s['indicator'],s['dataset']])
  ens_mean=COU.selection([s['indicator'],s['dataset'],'ensemble_mean'])[0]
  Projection_plot='app/static/images/'+s['country']+'/'+s['indicator']+'_'+s["scenario"]+'_'+s["dataset"]+'_'+proP+'-'+refP+'_'+s['season']+'_'+region+out_format
  if os.path.isfile(Projection_plot)==False:
    COU.period_statistics(periods=periods,selection=ens_selection,ref_name=refP)
    COU.period_model_agreement(ref_name=refP)
    fig,ax=plt.subplots(nrows=1,ncols=1,figsize=(4,3))
    ens_mean.display_map(ax=ax,
      highlight_region=highlight_region,
      period='diff_'+proP+'-'+refP,
      season=s['season'],
      color_label=indicator_label,
      )
    plt.title(proP.replace('to','-')+' vs '+refP.replace('to','-')+' '+lang_dict[lang][s['season']],fontsize=10)
    if out_format=='_small.png':plt.savefig(Projection_plot)
    if out_format=='_large.png':plt.savefig(Projection_plot,dpi=300) 
    if out_format=='.pdf':plt.savefig(Projection_plot, format='pdf', dpi=1000) 
  return(Projection_plot)

def transient_plot_func(s,COU,refP,proP,region,periods,lang,indicator_label,lang_dict,out_format):
  # transient
  ewembi=COU.selection([s['indicator'],'EWEMBI'])
  ens_selection=COU.selection([s['indicator'],s['dataset']])
  ens_mean=COU.selection([s['indicator'],s['dataset'],'ensemble_mean'])[0]
  transient_plot='app/static/images/'+s['country']+'/'+s['indicator']+'_'+s["dataset"]+'_'+region+'_'+s['season']+'_transient'+out_format
  if os.path.isfile(transient_plot)==False:

    if region != s['country']:COU.create_mask_admin(ewembi[0].raw_file,s['indicator'],regions=[region])
    COU.area_average('lat_weighted',overwrite=False,selection=ens_selection+ewembi,regions=[region])
    fig,ax=plt.subplots(nrows=1,ncols=1,figsize=(5,4))
    message=ens_mean.plot_transients(season=s['season'],region=region,running_mean_years=20,ax=ax,title='',ylabel=None,label='model data',color='green')
    message=ewembi[0].plot_transients(season=s['season'],region=region,running_mean_years=20,ax=ax,title='',ylabel=None,label='observations (EWEMBI)',color='black')
    if message==1:
      ax.set_ylabel(indicator_label)
      leg = plt.legend(loc='best',fancybox=True,fontsize=10)
      leg.get_frame().set_alpha(0.3)
      plt.title(s['region']+' '+lang_dict[lang][s['season']],fontsize=12)
      fig.tight_layout()
      if out_format=='_small.png':plt.savefig(transient_plot)
      if out_format=='_large.png':plt.savefig(transient_plot,dpi=300)  
      if out_format=='.pdf':plt.savefig(transient_plot, format='pdf', dpi=1000)  
  return(transient_plot)

def annual_cycle_plot_func(s,COU,refP,proP,region,periods,lang,indicator_label,lang_dict,out_format):
  # annual cycle
  ewembi=COU.selection([s['indicator'],'EWEMBI'])
  ens_selection=COU.selection([s['indicator'],s['dataset']])
  ens_mean=COU.selection([s['indicator'],s['dataset'],'ensemble_mean'])[0]
  annual_cycle_plot='app/static/images/'+s['country']+'/'+s['indicator']+'_'+s["dataset"]+'_'+region+'_annual_cycle_'+proP+'-'+refP+out_format
  if os.path.isfile(annual_cycle_plot)==False:
    if ewembi[0].time_format!='yearly':
      if region != s['country']:COU.create_mask_admin(ewembi[0].raw_file,s['indicator'],regions=[region])
      COU.area_average('lat_weighted',overwrite=False,selection=ens_selection+ewembi,regions=[region])
      COU.unit_conversions()

      COU.annual_cycle(periods={refP:s['ref_period']},selection=ewembi,regions=[region])
      COU.annual_cycle(periods=periods,selection=ens_selection,ref_name=refP,regions=[region])
      COU.annual_cycle_ensemble_mean(regions=[region])

      fig,ax=plt.subplots(nrows=2,ncols=1,sharex=True,figsize=(5,4))
      ewembi[0].plot_annual_cycle(period=refP,region=region,ax=ax[0],title='',ylabel='  ',label='observations (EWEMBI)',color='black',xlabel=False)
      ens_mean.plot_annual_cycle(period=refP,region=region,ax=ax[0],title='',ylabel='  ',label='model data',color='green',xlabel=False)
      leg = ax[0].legend(loc='best',fancybox=True,fontsize=10)
      leg.get_frame().set_alpha(0.3)
      ax[0].set_title(s['region']+' '+proP.replace('to','-')+' vs '+refP.replace('to','-')+' '+lang_dict[lang][s['season']],fontsize=12)

      ens_mean.plot_annual_cycle(period='diff_'+proP+'-'+refP,region=region,ax=ax[1],title='',ylabel='  ',label='projected change',color='green')
      ax[1].plot([0,1],[0,0],color='k')
      leg = ax[1].legend(loc='best',fancybox=True,fontsize=10)
      leg.get_frame().set_alpha(0.3)
      ylab_ax=fig.add_axes([0.0,0.0,1,1])
      ylab_ax.axis([0, 1, 0, 1])
      ylab_ax.axis('off')
      ylab_ax.text(0.05,0.5,indicator_label,rotation=90,verticalalignment='center')
      fig.subplots_adjust(left=0.175, bottom=0.125, right=0.95, top=0.90, wspace=0, hspace=0.1)

      if out_format=='_small.png':plt.savefig(annual_cycle_plot)
      if out_format=='_large.png':plt.savefig(annual_cycle_plot,dpi=300)
      if out_format=='.pdf':plt.savefig(annual_cycle_plot, format='pdf', dpi=1000)  
  return(annual_cycle_plot)





