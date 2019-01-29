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



import os,glob,sys,time,random,cPickle,string,gc
from app import app
from flask import redirect, render_template, url_for, request, flash, get_flashed_messages, g, session, jsonify, Flask, send_from_directory
from collections import OrderedDict
from werkzeug.routing import BuildError
import settings
import forms
import matplotlib.pylab as plt
from plotting import *

basepath='/Users/peterpfleiderer/Projects/'
try:
  os.chdir(basepath)
  wlcalculator_path=basepath+'wlcalculator-backup/app/'
except:
  basepath='/home/tooli/regioClim/'
  wlcalculator_path=basepath+'wlcalculator/app/'

sys.path.append(basepath+'country_analysis/country_analysis_scripts/')
os.system('ls '+basepath+'country_analysis/country_analysis_scripts/')
import country_analysis; reload(country_analysis)
sys.path.append(basepath+'/regioClim/')
os.chdir(basepath+'/regioClim/')


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field: %s" % (
                getattr(form, field).label.text,
                error
            ))

ind_dict=settings.ind_dict
indicator_dict=settings.indicator_dict
season_dict=settings.season_dict
period_dict=settings.period_dict
form_labels=settings.form_labels
text_dict=settings.text_dict
button_dict=settings.button_dict
warming_lvl_dict=settings.warming_lvl_dict

languages={'en':'English','fr':'Français'}

def initialize():
  print '________________initialize_____________'
  gc.collect()
  COU=country_analysis.country_analysis(session['country'],'../country_analysis/data/'+session['country']+'/',seasons=settings.seasons)
  COU.load_data(quiet=True,load_mask=True,load_raw=False,load_area_averages=False,load_region_polygons=True)
  COU.load_data(quiet=True,filename_filter='RX1',load_mask=False,load_raw=True,load_area_averages=True,load_region_polygons=False)

  COU._region_names[session['country']]='** '+settings.country_names[session['country']][session['language']]+' **'

  COU.get_warming_slices(wlcalculator_path=wlcalculator_path,model_real_names={'IPSL':'ipsl-cm5a-lr','HADGEM2':'hadgem2-es','ECEARTH':'ec-earth','MPIESM':'mpi-esm-lr'})


  print COU._warming_slices
  session_cou = open(session['cou_path'], 'wb')
  cPickle.dump(COU, session_cou, protocol=2) ; session_cou.close()
  gc.collect()
  return COU

@app.route('/')
def index():

  # delete session files older than an hour
  os.system('find app/static/COU_sessions/ -type f -mmin +60 -delete')

  session['user_type']='beginner'
  session['language']='en'

  session["country_avail"]   = sorted(settings.country_names.keys())
  session['country']   = session["country_avail"][0]
  session['country']   = 'BEN'

  session["ref_period"]   = settings.ref_period
  session["proj_period"]  = settings.proj_period

  session['use_periods'] = True

  session['warming_lvl_avail']=warming_lvl_dict['en'].keys()
  session['warming_lvl']='2.0'
  session['warming_lvl_ref']='ref'
  index=session['warming_lvl_avail'].index(session['warming_lvl'])
  session['warming_lvl_avail'][index],session['warming_lvl_avail'][0]=session['warming_lvl_avail'][0],session['warming_lvl_avail'][index]

  session["scenario_avail"]   = settings.scenarios
  session["scenario"]   = settings.scenarios[0]

  session["dataset_avail"]   = settings.datasets
  session["dataset"]   = settings.datasets[0]

  session["indicator_avail"]   = ['tas','TXx','pr','RX1','year_RX5']
  session["indicator"]   = 'tas'
  index=session['indicator_avail'].index(session['indicator'])
  session['indicator_avail'][index],session['indicator_avail'][0]=session['indicator_avail'][0],session['indicator_avail'][index]

  session['small_region_warning']=False

  session['ref_period_warning']='ok'
  session['proj_period_warning']='ok'

  session["season_avail"]   = settings.seasons.keys()
  session["season"]   = 'year'

  session['new_season_name']=''
  session['new_season_name_auto']=True

  session['id']=str(int((time.time()-int(time.time()))*10000))+str(int(random.random()*100000))
  session['cou_path']='app/static/COU_sessions/'+session['id']+'_'+session['country']+'.pkl'

  if os.path.isfile(session['cou_path'])==False:
    COU=initialize()

  session["region_avail"]   = [COU._region_names.keys()[COU._region_names.values().index(name)] for name in sorted(COU._region_names.values())]
  session['region']   = session["region_avail"][0]

  session['new_region_name']=''
  session['new_region_name_auto']=True


  session['location']='index'
  return redirect(url_for("choices"))

@app.route('/choices')
def choices():
  if True:
    start_time=time.time()

    s=session
    lang=s['language']

    region=s['region']

    form_country = forms.countryForm(request.form)
    s["country_avail"]   = sorted(settings.country_names.keys())
    s['country_avail']=[s['country']]+[sea for sea in s['country_avail'] if sea != s['country']]
    form_country.countrys.choices = zip(s['country_avail'],[settings.country_names[cou][lang] for cou in s['country_avail']])

    session_cou = open(s['cou_path'], 'rb')
    COU=cPickle.load( session_cou) ; session_cou.close()
    COU.load_data(quiet=True,filename_filter=s['indicator'],load_mask=False,load_raw=True,load_area_averages=True,load_region_polygons=False)
    COU.unit_conversions()

    print 'loaded session and data '+str(time.time()-start_time)

    form_region = forms.regionForm(request.form)
    sorted_regions = [reg for reg in [COU._region_names.keys()[COU._region_names.values().index(name)] for name in sorted(COU._region_names.values())] if reg in s['region_avail']]
    sorted_regions=[s['region']]+[reg for reg in sorted_regions if (reg != s['region']) & ('+' in reg)]+[reg for reg in sorted_regions if (reg != s['region']) & ('+' not in reg)]
    form_region.regions.choices = zip(sorted_regions,[COU._region_names[reg].replace('_',' ') for reg in sorted_regions])

    form_scenario = forms.scenarioForm(request.form)
    form_scenario.scenarios.choices = zip(s['scenario_avail'],s['scenario_avail'])

    form_dataset = forms.datasetForm(request.form)
    form_dataset.datasets.choices = zip(s['dataset_avail'],s['dataset_avail'])

    form_indicator = forms.indicatorForm(request.form)
    if s['small_region_warning']:
        indi_avail_tmp=['tas','pr']
    else:
        indi_avail_tmp=s['indicator_avail']

    form_indicator.indicators.choices = zip(indi_avail_tmp,[indicator_dict[lang][ind][0].upper()+indicator_dict[lang][ind][1:] for ind in indi_avail_tmp])

    form_warming_lvl = forms.warming_lvlForm(request.form)
    s['warming_lvl_avail']=[warming_lvl_dict[lang].keys()[warming_lvl_dict[lang].values().index(name)] for name in sorted(warming_lvl_dict[lang].values())]
    s['warming_lvl_avail']=[s['warming_lvl']]+[sea for sea in s['warming_lvl_avail'] if sea not in [s['warming_lvl'],'ref']]
    form_warming_lvl.warming_lvls.choices = zip(s['warming_lvl_avail'],[warming_lvl_dict[lang][sea] for sea in s['warming_lvl_avail']])

    form_warming_lvl_ref = forms.warming_lvl_refForm(request.form)
    s['warming_lvl_avail']=[warming_lvl_dict[lang].keys()[warming_lvl_dict[lang].values().index(name)] for name in sorted(warming_lvl_dict[lang].values())]
    s['warming_lvl_avail']=[s['warming_lvl_ref']]+[sea for sea in s['warming_lvl_avail'] if sea not in [s['warming_lvl_ref'],'2.0']]
    form_warming_lvl_ref.warming_lvl_refs.choices = zip(s['warming_lvl_avail'],[warming_lvl_dict[lang][lvl] for lvl in s['warming_lvl_avail']])

    form_period = forms.PeriodField(request.form)
    ref_P = str(s["ref_period"][0])+'-'+str(s["ref_period"][1]-1)
    proj_P = str(s["proj_period"][0])+'-'+str(s["proj_period"][1]-1)
    form_period = forms.PeriodField(request.form, proj_period=proj_P, ref_period=ref_P)

    form_season = forms.seasonForm(request.form)
    s['season_avail']=['year']+ [sea for sea in sorted(season_dict[lang].keys()) if (sea not in ['year','10','11','12']) & ('+' not in sea)]+['10','11','12']+[sea for sea in sorted(season_dict[lang].keys()) if '+' in sea]
    s['season_avail']=[s['season']]+[sea for sea in s['season_avail'] if sea != s['season']]
    form_season.seasons.choices = zip(s['season_avail'],[season_dict[lang][sea] for sea in s['season_avail']])

    if s['use_periods']:
      refP = str(s["ref_period"][0])+'to'+str(s["ref_period"][1]-1)
      refP_longname=str(s["ref_period"][0])+'-'+str(s["ref_period"][1]-1)
      refP_clim=refP
      refP_clim_longname=refP_longname
      proP=str(s["proj_period"][0])+'to'+str(s["proj_period"][1]-1)
      proP_longname=str(s["proj_period"][0])+'-'+str(s["proj_period"][1]-1)
      periods={refP:s["ref_period"],proP:s["proj_period"]}
      periods_ewembi={refP:s["ref_period"]}

    else:
      refP = s['warming_lvl_ref']
      refP_longname=warming_lvl_dict[lang][refP]
      refP_clim = 'ref'
      refP_clim_longname=warming_lvl_dict[lang]['ref']
      proP = s['warming_lvl']
      proP_longname=warming_lvl_dict[lang][proP]
      periods=COU._warming_slices
      periods_ewembi={'ref':[1986,2006]}

    indicator_label=indicator_dict[lang][s['indicator']]+' ['+ind_dict[s['indicator']]['unit']+']'

    plot_context={
      's':s,
      'COU':COU,
      'periods':periods,
      'periods_ewembi':periods_ewembi,
      'refP':refP,
      'refP_clim':refP_clim,
      'proP':proP,
      'refP_longname':refP_longname,
      'refP_clim_longname':refP_clim_longname,
      'proP_longname':proP_longname,
      'region':region,
      'lang':lang,
      'indicator_label':indicator_label[0].upper()+indicator_label[1:],
      'season_dict':season_dict,
      'highlight_region':region,
      'out_format':'_small.png'
    }

    plt.close('all')
    EWEMBI_plot=EWEMBI_plot_func(**plot_context)
    Projection_plot=Projection_plot_func(**plot_context)
    transient_plot=transient_plot_func(**plot_context)
    annual_cycle_plot=annual_cycle_plot_func(**plot_context)
    overview_plot=localisation_overview(**plot_context)
    plt.clf()

    print 'everything plotted '+str(time.time()-start_time)

    if s['user_type']=='advanced': advanced_col='white'
    if s['user_type']=='beginner':  advanced_col='gray'


    plot_dict={
      'EWEMBI_plot':EWEMBI_plot.replace('app/',''),
      'Projection_plot':Projection_plot.replace('app/',''),
      'transient_plot':transient_plot.replace('app/',''),
      'annual_cycle_plot':annual_cycle_plot.replace('app/',''),
      'overview_plot':overview_plot.replace('app/',''),
    }


    if s['season']=='year':season_add_on=''
    if s['season']!='year' and lang=='en':season_add_on=' in '+season_dict[lang][s['season']]
    if s['season']!='year' and lang=='fr':season_add_on=' en '+season_dict[lang][s['season']]

    if s['use_periods']==False:
      refP_clim_longname=refP_clim_longname.replace('°C','°C '+settings.above_preindustrial[lang])
      refP_longname=refP_longname.replace('°C','°C '+settings.above_preindustrial[lang])
      proP_longname=proP_longname.replace('°C','°C '+settings.above_preindustrial[lang])


    plot_text_dict={
      'country':s['indicator'],
      'indicator':indicator_dict[lang][s['indicator']],
      'season_add_on':season_add_on,
      'refP_longname':refP_longname,
      'proP_longname':proP_longname,
      'refP_clim_longname':refP_clim_longname,
    }

    other_dict={
      'language':get_language_tag(),
      'advanced_col':advanced_col,
      'use_periods':s['use_periods'],
      'user_type':s['user_type'],
      'small_region_warning':s['small_region_warning'],
      'ref_period_warning':s['ref_period_warning'],
      'proj_period_warning':s['proj_period_warning'],
      'language_flag':languages[s['language']],
    }

    form_dict = {
      'form_country':form_country,
      'form_region':form_region,
      'form_period':form_period,
      'form_warming_lvl':form_warming_lvl,
      'form_warming_lvl_ref':form_warming_lvl_ref,
      'form_season':form_season,
      'form_scenario':form_scenario,
      'form_dataset':form_dataset,
      'form_indicator':form_indicator,
    }

    context=form_dict.copy()
    context.update(other_dict)
    context.update(plot_dict)
    context.update(plot_text_dict)
    context.update(text_dict[lang])
    context.update(button_dict[lang])

    session['location']='choices'
    return render_template('choices_'+lang+'.html',**context)

  # except Exception,e:
  #   print str(e)
  #   return render_template('error.html')



###############################
# Define Season
###############################

@app.route('/season_page')
def season_page():
  try:
    s=session

    if s['new_season_name']=='' and s['new_season_name_auto']: s['new_season']=[]

    form_season = forms.seasonForm(request.form)
    form_season.seasons.choices = zip([str(sea) for sea in range(1,13)],[season_dict[s['language']][str(sea)] for sea in range(1,13)])

    form_NewSeason = forms.NewSeasonForm(request.form)
    form_NewSeason = forms.NewSeasonForm(request.form, season_name=session['new_season_name'])

    context = {
      'form_season':form_season,
      'form_NewSeason':form_NewSeason,
      'new_season_name':s['new_season_name'],
      'language':get_language_tag(),
      'months':[season_dict[s['language']][str(sea)] for sea in range(1,13) if str(sea) in session['new_season']],
    }
    context.update(text_dict[s['language']])
    context.update(button_dict[s['language']])

    session['location']='season_page'

    print context
    print s['new_season']

    return render_template('season_page_'+s['language']+'.html',**context)

  except Exception,e:
    print str(e)
    return render_template('error.html')

@app.route('/given_season_name',  methods=("POST", ))
def given_season_name():
  form_NewSeason = forms.NewSeasonForm(request.form)
  session['new_season_name']=form_NewSeason.season_name.data
  form_NewSeason = forms.NewSeasonForm(request.form, season_name=session['new_season_name'])
  session['new_season_name_auto']=False

  return redirect(url_for("season_page"))

@app.route('/go_to_season_page')
def go_to_season_page():
  session['new_season']=[]
  return redirect(url_for("season_page"))

@app.route('/add_month',  methods=('POST', ))
def add_month():
  form_season = forms.seasonForm(request.form)
  session['new_season']+=[form_season.seasons.data]
  session['new_season']=sorted(set(session['new_season']))

  if session['new_season_name_auto']: session['new_season_name']='+'.join([season_dict[session['language']][str(sea)] for sea in range(1,13) if str(sea) in session['new_season']])

  return redirect(url_for('season_page'))

@app.route('/save_this_season',  methods=("POST", ))
def save_this_season():
  season_name='+'.join([str(sea) for sea in sorted(session['new_season'])])

  # for COU in COUs.values():
  #   COU._seasons[season_name]=[int(sea) for sea in sorted(session['new_season'])]
  settings.seasons[season_name]=[int(sea) for sea in sorted(session['new_season'])]

  for lang in ['en','fr']:
    season_dict[lang][season_name]='+'.join([season_dict[lang][str(sea)] for sea in session['new_season']])

  session['season_avail']+=[season_name]

  session_cou = open(session['cou_path'], 'rb')
  COU=cPickle.load(session_cou) ; session_cou.close()
  COU._seasons[season_name]=[int(sea) for sea in sorted(session['new_season'])]
  session_cou = open(session['cou_path'], 'wb')
  cPickle.dump(COU, session_cou, protocol=2) ; session_cou.close()

  session['season']=season_name
  index=session['season_avail'].index(session['season'])
  session['season_avail'][index],session['season_avail'][0]=session['season_avail'][0],session['season_avail'][index]

  season_dict['en'][session['season']]=session['new_season_name']
  season_dict['fr'][session['season']]=session['new_season_name']

  session['new_season_name_auto']=True
  session['new_season_name']=''

  return redirect(url_for("choices"))


###############################
# Region Merge
###############################

@app.route('/merging_page')
def merging_page():

  '''
  not working if full country is actual region
  '''

  try:
    s=session

    session_cou = open(s['cou_path'], 'rb')
    COU=cPickle.load( session_cou) ; session_cou.close()
    COU.load_data(quiet=True,filename_filter=s['indicator'],load_mask=False,load_raw=True,load_area_averages=False,load_region_polygons=False)

    empty_object=COU.selection([s['indicator'],s['dataset'],'ensemble_mean'])[0]
    asp=(float(len(empty_object.lon))/float(len(empty_object.lat)))**0.5

    regions_plot='app/static/COU_images/'+s['country']+'/'+s['region']+'.png'
    if os.path.isfile(regions_plot)==False:
      # fig,ax = plt.subplots(nrows=1, frameon=False, subplot_kw={'projection': ccrs.PlateCarree()})
      fig, ax = plt.subplots(nrows=1, ncols=1,subplot_kw={'projection': ccrs.PlateCarree()})
      # ax = plt.Axes(fig, [0., 0., 1., 1.])
      fig.set_size_inches(6*asp,6/asp)
      # fig.add_axes(ax)

      empty_object.plot_map(to_plot=None,
        show_region_names=True,
        color_bar=False,
        ax=ax,
        show_all_adm_polygons=True)
        #title=COU._region_names[s['region']])

      if s['region']!=s['country']:
        print COU._adm_polygons[s['region']]
        patch = PolygonPatch(COU._adm_polygons[s['region']], facecolor='orange', edgecolor=[0,0,0], alpha=0.7, zorder=2)
        ax.add_patch(patch)
        ax.set_axis_off()

      plt.savefig(regions_plot,dpi=300)

    choosable_regions=[reg for reg in s['region_avail'][:] if reg!=s['country'] and len(reg.split('+'))<2]
    form_region = forms.regionForm(request.form)
    form_region.regions.choices = zip(choosable_regions,[COU._region_names[reg].replace('_',' ') for reg in choosable_regions])

    form_NewRegion = forms.NewRegionForm(request.form)
    form_NewRegion = forms.NewRegionForm(request.form, region_name=session['new_region_name'])

    half_lon_step=abs(np.diff(empty_object.lon.copy(),1)[0]/2)
    half_lat_step=abs(np.diff(empty_object.lat.copy(),1)[0]/2)

    xmin,xmax=min(empty_object.lon)-half_lon_step,max(empty_object.lon)+half_lon_step
    ymin,ymax=min(empty_object.lat)-half_lat_step,max(empty_object.lat)+half_lat_step

    x_w=500*asp
    y_h=500/asp

    clickable=[]

    for region in choosable_regions:
      poly=COU._adm_polygons[region]
      if poly.geom_type == 'MultiPolygon':
        area=[]
        for subpoly in poly:
          area.append(subpoly.area)
        x,y=poly[area.index(max(area))].simplify(0.1).exterior.xy

      elif poly.geom_type == 'Polygon':
        x,y=poly.simplify(0.1).exterior.xy

      point_list=''
      for xx,yy in zip(x,y):
        point_list+=str((xx-xmin)/(xmax-xmin)*x_w)+', '
        point_list+=str(y_h-(yy-ymin)/(ymax-ymin)*y_h)+', '

      clickable.append({'poly':point_list[:-2],'name':region})


    context = {
      'form_region':form_region,
      'form_NewRegion':form_NewRegion,
      'regions_plot':regions_plot.replace('app/',''),
      'small_region_warning':s['small_region_warning'],
      'language':get_language_tag(),
      'regions':clickable,
      'x_width':x_w,
      'y_height':y_h,
    }

    context.update(clickable)

    context.update(text_dict[s['language']])
    context.update(button_dict[s['language']])

    session['location']='merging_page'
    return render_template('merging_page_'+s['language']+'.html',**context)

  except Exception,e:
    print str(e)
    return render_template('error.html')

@app.route('/given_region_name',  methods=("POST", ))
def given_region_name():
  form_NewRegion = forms.NewRegionForm(request.form)
  session['new_region_name']=form_NewRegion.region_name.data
  form_NewRegion = forms.NewRegionForm(request.form, region_name=session['new_region_name'])
  session['new_region_name_auto']=False

  return redirect(url_for("merging_page"))

# @app.route('/go_to_merging_page',  methods=("POST", ))
# def go_to_merging_page():
#   session['region']=session['country']
#   return redirect(url_for("merging_page"))

@app.route('/clear_selection',  methods=("POST", ))
def clear_selection():
  session['region']=session['country']
  return redirect(url_for("merging_page"))

def merge_with_region(to_merge):
  s=session

  session_cou = open(s['cou_path'], 'rb')
  COU=cPickle.load( session_cou) ; session_cou.close()

  if s['region']!=s['country']:
    s['region']=COU.merge_adm_regions([s['region'],to_merge])

    session_cou = open(s['cou_path'], 'wb')
    cPickle.dump(COU, session_cou, protocol=2) ; session_cou.close()
  else:
    s['region']=to_merge

  area=COU.get_region_area(s['region'])['latxlon']*4
  if area<4:
    s['small_region_warning']=True
  else:
    s['small_region_warning']=False

  if s['new_region_name_auto']:s['new_region_name']=s['region']


@app.route('/merge_with_region_from_form',  methods=('POST', ))
def merge_with_region_from_form():
  form_region = forms.regionForm(request.form)
  merge_with_region(form_region.regions.data)
  return redirect(url_for('merging_page'))

@app.route('/merge_with_region_click/<region>',  methods=('POST', 'GET',))
def merge_with_region_click(region):
  merge_with_region(region)
  return redirect(url_for('merging_page'))

@app.route('/save_this_region',  methods=("POST", ))
def save_this_region():

  session_cou = open(session['cou_path'], 'rb')
  COU=cPickle.load( session_cou) ; session_cou.close()

  COU._region_names[session['region']]=session['new_region_name']

  if session['region'] not in session['region_avail']:
    session['region_avail']+=[session['region']]
    index=session['region_avail'].index(session['region'])
    session['region_avail'][index],session['region_avail'][0]=session['region_avail'][0],session['region_avail'][index]

  session_cou = open(session['cou_path'], 'wb')
  cPickle.dump(COU, session_cou, protocol=2) ; session_cou.close()

  session['new_region_name_auto']=True
  session['new_region_name']=''

  return redirect(url_for("choices"))


###############################
# option choices
###############################
@app.route('/scenario_choice',  methods=('POST', ))
def scenario_choice():
  form_scenario = forms.scenarioForm(request.form)
  session['scenario']=form_scenario.scenarios.data
  # put chosen at beginning of list
  index=session['scenario_avail'].index(session['scenario'])
  session['scenario_avail'][index],session['scenario_avail'][0]=session['scenario_avail'][0],session['scenario_avail'][index]
  return redirect(url_for('choices'))

@app.route('/dataset_choice',  methods=('POST', ))
def dataset_choice():
  form_dataset = forms.datasetForm(request.form)
  session['dataset']=form_dataset.datasets.data
  # put chosen at beginning of list
  index=session['dataset_avail'].index(session['dataset'])
  session['dataset_avail'][index],session['dataset_avail'][0]=session['dataset_avail'][0],session['dataset_avail'][index]
  return redirect(url_for('choices'))

@app.route('/warming_lvl_choice',  methods=('POST', ))
def warming_lvl_choice():
  form_warming_lvl_ref = forms.warming_lvl_refForm(request.form)
  session['warming_lvl_ref']=form_warming_lvl_ref.warming_lvl_refs.data

  form_warming_lvl = forms.warming_lvlForm(request.form)
  session['warming_lvl']=form_warming_lvl.warming_lvls.data
  return redirect(url_for('choices'))

@app.route('/switch_to_periods')#,  methods=("POST", )
def switch_to_periods():
  session['use_periods']=abs(session['use_periods']-1)
  if session['use_periods']:
    session["ref_period"]   = settings.ref_period
    session["proj_period"]  = settings.proj_period
  else:
    session['warming_lvl_avail']=['1.5','2.0','2.5','3']
    session['warming_lvl']='2.0'
    index=session['warming_lvl_avail'].index(session['warming_lvl'])
    session['warming_lvl_avail'][index],session['warming_lvl_avail'][0]=session['warming_lvl_avail'][0],session['warming_lvl_avail'][index]

  return redirect(url_for("choices"))

@app.route('/periodchoice',  methods=("POST", ))
def add_periodchoice():
  form_period = forms.PeriodField(request.form)
  ref_period=[int(form_period.ref_period.data.split("-")[0]),int(form_period.ref_period.data.split("-")[1])+1]
  session["ref_period"]   = ref_period
  proj_period=[int(form_period.proj_period.data.split("-")[0]),int(form_period.proj_period.data.split("-")[1])+1]
  session["proj_period"]  = proj_period

  session['ref_period_warning']='ok'
  if ref_period[1]-ref_period[0]<20:  session['ref_period_warning']='small'
  if ref_period[0]>ref_period[1]:  session['ref_period_warning']='strange'
  if ref_period[1]>2006:  session['ref_period_warning']='out_range'
  if ref_period[0]<1979:  session['ref_period_warning']='out_range'

  session['proj_period_warning']='ok'
  if proj_period[1]-proj_period[0]<20:  session['proj_period_warning']='small'
  if proj_period[0]>proj_period[1]:  session['proj_period_warning']='strange'
  if proj_period[1]>2100:  session['proj_period_warning']='out_range'
  if proj_period[0]<1950:  session['proj_period_warning']='out_range'


  return redirect(url_for("choices"))

@app.route('/season_choice',  methods=('POST', ))
def season_choice():
  form_season = forms.seasonForm(request.form)
  session['season']=form_season.seasons.data
  return redirect(url_for('choices'))

@app.route('/indicator_choice',  methods=('POST', ))
def indicator_choice():
  form_indicator = forms.indicatorForm(request.form)
  session['indicator']=form_indicator.indicators.data
  # put chosen at beginning of list
  session['indicator_avail']=['tas','TXx','pr','RX1','year_RX5']
  session['indicator_avail']=[session['indicator']]+[ind for ind in ['tas','TXx','pr','RX1','year_RX5'] if ind!=session['indicator']]
  #index=session['indicator_avail'].index(session['indicator'])
  #session['indicator_avail'][index],session['indicator_avail'][0]=session['indicator_avail'][0],session['indicator_avail'][index]
  if ind_dict[session['indicator']]['time_step']=='yearly':  session["season_avail"]=['year']
  if ind_dict[session['indicator']]['time_step']=='monthly':  session["season_avail"]=settings.seasons.keys()
  if session["season"] not in session["season_avail"]: session["season"] = 'year'
  return redirect(url_for('choices'))

def check_size(COU):
  area=COU.get_region_area(session['region'])['latxlon']*4
  if area<4:
    session['small_region_warning']=True
  else:
    session['small_region_warning']=False


@app.route('/region_choice',  methods=('POST', ))
def region_choice():
  form_region = forms.regionForm(request.form)
  session['region']=form_region.regions.data
  if session['region'].split('(')[-1]!='full country)':
    #COU=COUs[session['country']]
    session_cou = open(session['cou_path'], 'rb')
    COU=cPickle.load( session_cou) ; session_cou.close()
    if session['region']==session['country']:
      session['small_region_warning']=False
    check_size(COU)
  return redirect(url_for('choices'))

@app.route('/country_choice',  methods=('POST', ))
def country_choice():
  form_country = forms.countryForm(request.form)
  session['country']=form_country.countrys.data

  session["season_avail"]   = settings.seasons.keys()
  session["season"]   = 'year'

  session['cou_path']='app/static/COU_sessions/'+session['id']+'_'+session['country']+'.pkl'
  if os.path.isfile(session['cou_path'])==False:
    if os.path.isdir('../country_analysis/data/'+session['country']):
        COU=initialize()
    else:
        return render_template('not_available.html')

  else:
    session_cou = open(session['cou_path'], 'rb')
    COU=cPickle.load( session_cou) ; session_cou.close()

  gc.collect()

  session["indicator"]   = 'tas'
  index=session['indicator_avail'].index(session['indicator'])
  session['indicator_avail'][index],session['indicator_avail'][0]=session['indicator_avail'][0],session['indicator_avail'][index]

  session["region_avail"]   = [COU._region_names.keys()[COU._region_names.values().index(name)] for name in sorted(COU._region_names.values())]
  session['region']   = session["region_avail"][0]

  session["season_avail"]   = settings.seasons.keys()
  session["season"]   = 'year'
  check_size(COU)

  return redirect(url_for('choices'))


###############################
# Download
###############################

@app.route('/prepare_for_download/<plot_request>',  methods=('GET',"POST", ))
def prepare_for_download(plot_request):
  print plot_request
  request_type=plot_request.split('**')[0]
  plot_format=plot_request.split('**')[-1]

  s=session

  lang=s['language']

  region=s['region']
  if region.split('(')[-1]=='full country)': region=s['country']

  session_cou = open(s['cou_path'], 'rb')
  COU=cPickle.load( session_cou) ; session_cou.close()
  COU.load_data(quiet=True,filename_filter=s['indicator'],load_mask=False,load_raw=True,load_area_averages=True,load_region_polygons=False)
  COU.unit_conversions()

  if s['use_periods']:
    refP = "to".join(str(t) for t in s["ref_period"])
    proP = "to".join(str(t) for t in s["proj_period"])
    periods={refP:s["ref_period"],proP:s["proj_period"]}
    periods_ewembi={refP:s["ref_period"]}
    refP_longname=refP.replace('to','-')
    proP_longname=proP.replace('to','-')

  else:
    refP = s['warming_lvl_ref']
    proP = s['warming_lvl']
    periods=COU._warming_slices
    periods_ewembi={'1.5':[2200,2220],'ref':[1986,2006]}
    refP_longname=warming_lvl_dict[lang][refP]
    proP_longname=warming_lvl_dict[lang][proP]




  if s['use_periods']:
    refP = str(s["ref_period"][0])+'to'+str(s["ref_period"][1]-1)
    refP_longname=str(s["ref_period"][0])+'-'+str(s["ref_period"][1]-1)
    refP_clim=refP
    refP_clim_longname=refP_longname
    proP=str(s["proj_period"][0])+'to'+str(s["proj_period"][1]-1)
    proP_longname=str(s["proj_period"][0])+'-'+str(s["proj_period"][1]-1)
    periods={refP:s["ref_period"],proP:s["proj_period"]}
    periods_ewembi={refP:s["ref_period"]}

  else:
    refP = s['warming_lvl_ref']
    refP_longname=warming_lvl_dict[lang][refP]
    refP_clim = 'ref'
    refP_clim_longname=warming_lvl_dict[lang]['ref']
    proP = s['warming_lvl']
    proP_longname=warming_lvl_dict[lang][proP]
    periods=COU._warming_slices
    periods_ewembi={'ref':[1986,2006]}


  indicator_label=indicator_dict[lang][s['indicator']]+' ['+ind_dict[s['indicator']]['unit']+']'

  plot_context={
    's':s,
    'COU':COU,
    'periods':periods,
    'periods_ewembi':periods_ewembi,
    'refP':refP,
    'refP_clim':refP_clim,
    'proP':proP,
    'refP_longname':refP_longname,
    'refP_clim_longname':refP_clim_longname,
    'proP_longname':proP_longname,
    'region':region,
    'lang':lang,
    'indicator_label':indicator_label,
    'season_dict':season_dict,
    'highlight_region':region,
    'out_format':plot_format
  }

  if request_type=='EWEMBI_plot':  filename=EWEMBI_plot_func(**plot_context)
  if request_type=='Projection_plot':  filename=Projection_plot_func(**plot_context)
  if request_type=='transient_plot':  filename=transient_plot_func(**plot_context)
  if request_type=='annual_cycle_plot':  filename=annual_cycle_plot=annual_cycle_plot_func(**plot_context)

  print(plot_request)
  if request_type=='get_data':
    curretn_path=os.getcwd()
    os.chdir('../country_analysis/data/'+s['country']+'/')
    os.system('tar -vzcf ../'+s['country']+'_'+s['indicator']+'.tar.gz area_average/*-'+s['indicator']+'_* raw/*_'+s['indicator']+'_*')
    os.chdir(curretn_path)
    filename=s['country']+'_'+s['indicator']+'.tar.gz'


  if 'get_data' in request_type.split('**'):
    return send_from_directory(directory=settings.basepath+'country_analysis/data/', filename=filename.replace('app/',''),as_attachment=True)

  if 'plot' in request_type.split('_'):
    return send_from_directory(directory=settings.basepath+'RegioClim/app/', filename=filename.replace('app/',''),as_attachment=True)


###############################
# Navigation
###############################
def get_language_tag():
  if session['language']=='fr':
    return(languages['en'])
  if session['language']=='en':
    return(languages['fr'])

@app.route('/language_choice',  methods=('POST', ))
def language_choice():
  if session['language']=='en': lang=0
  if session['language']=='fr': lang=1
  lang*=-1
  session['language']=['en','fr'][lang+1]
  return redirect(url_for(session['location']))

@app.route('/go_to_choices',  methods=("POST", ))
def go_to_choices():
  return redirect(url_for("choices"))

@app.route('/home',  methods=('GET', ))
def render_home():
  return redirect(url_for('index'))

@app.route('/about',  methods=('GET', ))
def render_about():
  return render_template('about.html')

@app.route('/contact',  methods=('GET', ))
def render_contact():
  return render_template('contact.html')

@app.route('/documentation')
def documentation():
  session['location']='documentation'
  return render_template('documentation_'+session['language']+'.html',language=get_language_tag())


# @app.route('/user_type_choice',  methods=('POST', ))
# def user_type_choice():
#   if session['user_type']=='beginner': usr=0
#   if session['user_type']=='advanced': usr=1
#   usr*=-1
#   session['user_type']=['beginner','advanced'][usr+1]
#   if session['user_type']=='advanced':
#     print 'asdasdasd ------- asdas'
#     session['period_avail']=settings.periods_advanced
#   if session['user_type']=='beginner':
#     session['period_avail']=settings.periods_beginner
#     session['dataset']='CORDEX_BC'
#   return redirect(url_for('choices'))

# @app.route('/go_to_model_agreement',  methods=("POST", ))
# def go_to_model_agreement():
#   return redirect(url_for("model_agreement"))

# @app.route('/go_to_bias_correction',  methods=("POST", ))
# def go_to_bias_correction():
#   return redirect(url_for("bias_correction"))

# @app.route('/model_agreement')
# def model_agreement():
  # try:
#     country=session['country']

#     form_period = forms.periodForm(request.form)
#     form_period.periods.choices = zip(session['period_avail'],session['period_avail'])

#     refP = "-".join(str(t) for t in session["ref_period"])
#     proP = session['period']
#     periods={'ref':session["ref_period"],'projection':session["proj_period"]}
#     CORDEX_BC_plot_detail='static/images/'+country+'/'+session["indicator"]+'_'+session["scenario"]+'_'+session['dataset']+'_'+session['season']+'_details.png'

#     context = {
#       'CORDEX_BC_plot_detail':CORDEX_BC_plot_detail,
#     }
#     return render_template('model_agreement.html',**context)

#   except KeyError:
#     return redirect(url_for("index"))

# @app.route('/bias_correction')
# def bias_correction():
  # try:
#     country=session['country']

#     form_period = forms.PeriodField(request.form)
#     form_period.periods.choices = zip(session['period_avail'],session['period_avail'])

#     refP = "-".join(str(t) for t in session["ref_period"])
#     proP = session['period']
#     periods={'ref':session["ref_period"],'projection':session["proj_period"]}
#     bias_corretion_check='static/images/'+country+'/'+session["indicator"]+'_BC_check_'+session['season']+'.png'

#     context = {
#       'bias_corretion_check':bias_corretion_check
#     }
#     return render_template('bias_correction.html',**context)

#   except KeyError:
#     return redirect(url_for("index"))
