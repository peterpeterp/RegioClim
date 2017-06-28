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

import os,glob
from app import app
from flask import redirect, render_template, url_for, request, flash, get_flashed_messages, g, session, jsonify, Flask, send_from_directory
from collections import OrderedDict
from werkzeug.routing import BuildError
import settings
import forms
import matplotlib.pylab as plt
from plotting import *

# from flask_nav import Nav
# from flask_nav.elements import Navbar, View
# nav = Nav()
# nav.init_app(app)
# @nav.navigation()
# def top_nav():
#     items = [View('Home', 'index'), View('Shopping Area', 'index')]
#     items.append(View('Secret Shop', 'index'))
#     return Navbar('', *items)




def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field: %s" % (
                getattr(form, field).label.text,
                error
            ))

ind_dict=settings.ind_dict
lang_dict=settings.lang_dict
period_dict=settings.period_dict
regions=settings.regions
form_labels=settings.form_labels
season_dict=settings.season_dict
text_dict=settings.text_dict
button_dict=settings.button_dict


COUs=settings.COUs

languages={'en':'English','fr':'Français'}


@app.route('/')
def index():
  session['user_type']='beginner'
  session['language']='en'

  session["country_avail"]   = settings.countrys
  session['country']   = settings.countrys[0]

  session["ref_period"]   = settings.ref_period
  session["proj_period"]  = settings.proj_period

  session["scenario_avail"]   = settings.scenarios
  session["scenario"]   = settings.scenarios[0]

  session["dataset_avail"]   = settings.datasets
  session["dataset"]   = settings.datasets[0]

  session["indicator_avail"]   = settings.ind_dict.keys()
  session["indicator"]   = session["indicator_avail"][0]

  session["region_avail"]   = regions[session['country']]
  session['region']   = session["region_avail"][0]

  session['small_region_warning']=False

  session["season_avail"]   = season_dict[session['country']]
  index=session['season_avail'].index('year')
  session['season_avail'][index],session['season_avail'][0]=session['season_avail'][0],session['season_avail'][index]
  session["season"]   = session["season_avail"][0]

  print session
  return redirect(url_for("choices"))

@app.route('/choices')
def choices():
  try: 
    s=session
    lang=s['language']

    region=s['region']
    if region.split('(')[-1]=='full country)': region=s['country']

    form_country = forms.countryForm(request.form)
    form_country.countrys.choices = zip(s['country_avail'],[{'BEN':'Benin','SEN':'Senegal'}[cou] for cou in s['country_avail']])

    form_region = forms.regionForm(request.form)
    form_region.regions.choices = zip(s['region_avail'],s['region_avail'])

    form_scenario = forms.scenarioForm(request.form)
    form_scenario.scenarios.choices = zip(s['scenario_avail'],s['scenario_avail'])

    form_dataset = forms.datasetForm(request.form)
    form_dataset.datasets.choices = zip(s['dataset_avail'],s['dataset_avail'])

    form_indicator = forms.indicatorForm(request.form)
    form_indicator.indicators.choices = zip(s['indicator_avail'],[lang_dict[lang][ind] for ind in s['indicator_avail']])

    form_period = forms.PeriodField(request.form)
    ref_P = "-".join(str(t) for t in session["ref_period"])
    proj_P = "-".join(str(t) for t in session["proj_period"])
  
    form_period = forms.PeriodField(request.form, proj_period=proj_P, ref_period=ref_P)

    print s['season_avail']

    form_season = forms.seasonForm(request.form)
    form_season.seasons.choices = zip(s['season_avail'],[lang_dict[lang][sea] for sea in s['season_avail']])

    refP = "to".join(str(t) for t in s["ref_period"])
    proP = "to".join(str(t) for t in s["proj_period"])
    periods={refP:s["ref_period"],proP:s["proj_period"]}

    COU=COUs[s['country']]

    indicator_label=lang_dict[lang][s['indicator']]+' ['+ind_dict[s['indicator']]['unit']+']'

    EWEMBI_plot=EWEMBI_plot_func(s,COU,refP,proP,region,periods,lang,indicator_label,lang_dict,'_small.png',highlight_region=region)
    Projection_plot=Projection_plot_func(s,COU,refP,proP,region,periods,lang,indicator_label,lang_dict,'_small.png',highlight_region=region)
    print '_________ transient'
    transient_plot=transient_plot_func(s,COU,refP,proP,region,periods,lang,indicator_label,lang_dict,'_small.png')
    print '_________ annual cycle'
    annual_cycle_plot=annual_cycle_plot_func(s,COU,refP,proP,region,periods,lang,indicator_label,lang_dict,'_small.png')
    print '_________ done'

    if s['user_type']=='advanced': advanced_col='white'
    if s['user_type']=='beginner':  advanced_col='gray'

    plot_dict={
      'EWEMBI_plot':EWEMBI_plot.replace('app/',''),
      'Projection_plot':Projection_plot.replace('app/',''),
      'transient_plot':transient_plot.replace('app/',''),
      'annual_cycle_plot':annual_cycle_plot.replace('app/',''),
    }

    if s['season']=='year':season_add_on=''
    if s['season']!='year':season_add_on=' in '+lang_dict[lang][s['season']]
    plot_txt_dict={'en':{
      'EWEMBI_plot':EWEMBI_plot.replace('app/',''),
      'EWEMBI_plot_title':'Climatology',
      'EWEMBI_plot_title_txt':lang_dict[lang][s['indicator']]+' averaged over the reference period '+refP.replace('to','-')+season_add_on+'. Observations are taken from EWEMBI.',

      'Projection_plot':Projection_plot.replace('app/',''),
      'Projection_plot_title':'Projected Change',
      'Projection_plot_title_txt':'Projected change in '+lang_dict[lang][s['indicator']]+' for '+proP.replace('to','-')+' compared to the reference period '+refP.replace('to','-')+season_add_on+'. Here the ensemble mean is displayed, grid-cells for which a model-disagreement is found are colored in gray.',

      'transient_plot':transient_plot.replace('app/',''),
      'transient_plot_title':'Transient',
      'transient_plot_title_txt':lang_dict[lang][s['indicator']]+' displayed as 20 year running mean'+season_add_on+'. Observations (EWEMBI) are shown in green for the period 1999-2013. RCM simulations are shown in red for the period 1970-2100. The line represents the ensemble mean while the shaded area represents the model spread. Differences between observations and model data during the period 1999-2013 have to be expected.',

      'annual_cycle_plot':annual_cycle_plot.replace('app/',''),
      'annual_cycle_plot_title':'Annual Cycle',
      'annual_cycle_plot_title_txt':'Annual cycle of '+lang_dict[lang][s['indicator']]+' for the reference period '+refP.replace('to','-')+' (top) and changes in the annual cycle projected for '+proP.replace('to','-')+' compared to the reference period '+refP.replace('to','-')+' (bottom). Observations (EWEMBI) are shown in green, RCM simulations are shown in red. The line represents the ensemble mean while the shaded area represents the model spread.',
    },

    'fr':{
      'EWEMBI_plot':EWEMBI_plot.replace('app/',''),
      'EWEMBI_plot_title':'Climatologie',
      'EWEMBI_plot_title_txt':lang_dict[lang][s['indicator']]+' en moyenne de le période de référence '+refP.replace('to','')+' '+s['season']+'. Les observations proviennent de EWEMBI',

      'Projection_plot':Projection_plot.replace('app/',''),
      'Projection_plot_title':'Changement Projeté',
      'Projection_plot_title_txt':'Changement projeté en '+lang_dict[lang][s['indicator']]+' pour '+proP.replace('to','')+' par rapport à la période de référence '+refP.replace('to','')+' '+s['season']+'. Ici la moyenne de l`ensemble est présentée, les grilles pour lesquelles les différents modèles sont en désaccord sont coloriés en gris.',

      'transient_plot':transient_plot.replace('app/',''),
      'transient_plot_title':'Trajectoire Projetée',
      'transient_plot_title_txt':lang_dict[lang][s['indicator']]+' présenté comme moyenne mobile de 20 années. Observations (EWEMBI) en vert pour la période 1999-2013. Modélisations climatiques régionales en rouge pour la période 1970-2100. La ligne représente la moyenne de l`ensemble et la zone ombragée montre l`écart entre les modèles.',

      'annual_cycle_plot':annual_cycle_plot.replace('app/',''),
      'annual_cycle_plot_title':'Cycle Annuel',
      'annual_cycle_plot_title_txt':'Cycle annuel de '+lang_dict[lang][s['indicator']]+' pour la période de référence '+refP.replace('to','')+' (en haut) et différences dans le cycle annuel projetées pour '+proP.replace('to','')+ ' par rapport à la période de référence'+refP.replace('to','-')+' (en bas). Observations (EWEMBI) en vert, modélisation climatique régionale en rouge. La ligne représente la moyenne de l`ensemble et la zone ombragée montre l`écart entre les modèles.',
    }
    }

    if lang=='fr':
      language=languages['en']
    if lang=='en':
      language=languages['fr']

    other_dict={
      'language':language,
      'advanced_col':advanced_col,
      'user_type':s['user_type'],
      'small_region_warning':s['small_region_warning'],
      'language_flag':languages[s['language']],
    }

    form_dict = { 
      'form_country':form_country,
      'form_country':form_country,
      'form_region':form_region,
      'form_period':form_period,
      'form_season':form_season,
      'form_scenario':form_scenario,
      'form_dataset':form_dataset,
      'form_indicator':form_indicator,
    }

    context=form_dict.copy()
    context.update(other_dict)
    context.update(plot_dict)
    context.update(plot_txt_dict[lang])
    context.update(text_dict[lang])
    context.update(button_dict[lang])

    print plot_dict


    return render_template('choices.html',**context)

  except Exception,e: 
    print str(e)
    return redirect(url_for("index"))



###############################
# Define Season
###############################

@app.route('/season_page')
def season_page():
  if True:
    s=session

    form_season = forms.seasonForm(request.form)
    form_season.seasons.choices = zip([str(sea) for sea in range(1,13)],[lang_dict[s['language']][str(sea)] for sea in range(1,13)])

    new_season_name='+'.join([lang_dict[s['language']][str(sea)] for sea in session['new_season']])

    context = { 
      'form_season':form_season,
      'new_season_name':new_season_name
    }
    context.update(text_dict[s['language']])
    context.update(button_dict[s['language']])

    return render_template('season_page.html',**context)

  # except KeyError:
  #   return redirect(url_for("index"))


@app.route('/go_to_season_page',  methods=("POST", ))
def go_to_season_page():
  session['new_season']=[]
  return redirect(url_for("season_page"))

@app.route('/add_month',  methods=('POST', ))
def add_month():
  form_season = forms.seasonForm(request.form)
  session['new_season']+=[form_season.seasons.data]
  session['new_season']=sorted(set(session['new_season']))
  #update_keywords()
  return redirect(url_for('season_page'))

@app.route('/save_this_season',  methods=("POST", ))
def save_this_season():
  season_name='+'.join([str(sea) for sea in sorted(session['new_season'])])

  for COU in COUs.values():
    COU._seasons[season_name]=[int(sea) for sea in sorted(session['new_season'])]

  for lang in ['en','fr']:
    lang_dict[lang][season_name]='+'.join([lang_dict[lang][str(sea)] for sea in session['new_season']])

  for cou in season_dict.keys():
    season_dict[cou].append(season_name)

  session['season_avail']+=[season_name]

  print session['season_avail']

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
    COU=COUs[s['country']]

    regions_plot='app/static/images/'+s['country']+'/'+s['region']+'.png'
    if os.path.isfile(regions_plot)==False:
      COU.selection([s['indicator'],s['dataset'],'ensemble_mean'])[0].plot_map(to_plot='empty',
        show_region_names=True,
        color_bar=False,
        out_file=regions_plot,
        highlight_region=s['region'],
        title=s['region'])

    form_region = forms.regionForm(request.form)
    form_region.regions.choices = zip(s['region_avail'],s['region_avail'])
    form_region.regions.label = 'Add another region'

    context = { 
      'form_region':form_region,
      'regions_plot':regions_plot.replace('app/',''),
      'small_region_warning':s['small_region_warning']
    }
    context.update(text_dict[s['language']])
    context.update(button_dict[s['language']])

    return render_template('merging_page.html',**context)

  except KeyError:
    return redirect(url_for("index"))


@app.route('/go_to_merging_page',  methods=("POST", ))
def go_to_merging_page():
  return redirect(url_for("merging_page"))

@app.route('/merge_with_region',  methods=('POST', ))
def merge_with_region():
  form_region = forms.regionForm(request.form)
  to_merge=form_region.regions.data
  s=session
  s['region']=COUs[s['country']].merge_adm_regions([s['region'],to_merge])

  if s['region'].split('(')[-1]!='full country)':
    COU=COUs[s['country']]
    area=COU.get_region_area(s['region'])['latxlon']*4
    if area<4:
      s['small_region_warning']=True
    else:
      s['small_region_warning']=False

  return redirect(url_for('merging_page'))

@app.route('/save_this_region',  methods=("POST", ))
def save_this_region():

  if session['region'] not in session['region_avail']:
    session['region_avail']+=[session['region']]
    index=session['region_avail'].index(session['region'])
    session['region_avail'][index],session['region_avail'][0]=session['region_avail'][0],session['region_avail'][index]

  return redirect(url_for("choices"))


###############################
# option choices
###############################

@app.route('/user_type_choice',  methods=('POST', ))
def user_type_choice():
  if session['user_type']=='beginner': usr=0
  if session['user_type']=='advanced': usr=1
  usr*=-1
  session['user_type']=['beginner','advanced'][usr+1]
  if session['user_type']=='advanced':
    print 'asdasdasd ------- asdas'
    session['period_avail']=settings.periods_advanced
  if session['user_type']=='beginner':
    session['period_avail']=settings.periods_beginner
    session['dataset']='CORDEX_BC'
  return redirect(url_for('choices'))

@app.route('/language_choice',  methods=('POST', ))
def language_choice():
  if session['language']=='en': lang=0
  if session['language']=='fr': lang=1
  lang*=-1
  session['language']=['en','fr'][lang+1]
  return redirect(url_for('choices'))

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

@app.route('/season_choice',  methods=('POST', ))
def season_choice():
  form_season = forms.seasonForm(request.form)
  session['season']=form_season.seasons.data
  # put chosen at beginning of list
  index=session['season_avail'].index(session['season'])
  session['season_avail'][index],session['season_avail'][0]=session['season_avail'][0],session['season_avail'][index]
  return redirect(url_for('choices'))

@app.route('/indicator_choice',  methods=('POST', ))
def indicator_choice():
  form_indicator = forms.indicatorForm(request.form)
  session['indicator']=form_indicator.indicators.data
  # put chosen at beginning of list
  index=session['indicator_avail'].index(session['indicator'])
  session['indicator_avail'][index],session['indicator_avail'][0]=session['indicator_avail'][0],session['indicator_avail'][index]
  if ind_dict[session['indicator']]['time_step']=='yearly':  session["season_avail"]=['year']
  if ind_dict[session['indicator']]['time_step']=='monthly':  session["season_avail"]=season_dict[session['country']]
  if session["season"] not in session["season_avail"]: session["season"] = session["season_avail"][0]
  return redirect(url_for('choices'))


@app.route('/periodchoice',  methods=("POST", ))
def add_periodchoice():
  form_period = forms.PeriodField(request.form)

  if form_period.validate_on_submit():
    session["ref_period"]   = [int(t) for t in form_period.ref_period.data.split("-")]
    session["proj_period"]  = [int(t) for t in form_period.proj_period.data.split("-")]
  else:
    flash_errors(form_period)

  return redirect(url_for("choices"))

@app.route('/region_choice',  methods=('POST', ))
def region_choice():
  form_region = forms.regionForm(request.form)
  session['region']=form_region.regions.data
  if session['region'].split('(')[-1]!='full country)':
    COU=COUs[session['country']]
    area=COU.get_region_area(session['region'])['latxlon']*4
    print area
    if area<4:
      session['small_region_warning']=True
    else:
      session['small_region_warning']=False
  # put chosen at beginning of list
  index=session['region_avail'].index(session['region'])
  session['region_avail'][index],session['region_avail'][0]=session['region_avail'][0],session['region_avail'][index]
  return redirect(url_for('choices'))

@app.route('/country_choice',  methods=('POST', ))
def country_choice():
  form_country = forms.countryForm(request.form)
  session['country']=form_country.countrys.data
  # put chosen at beginning of list
  index=session['country_avail'].index(session['country'])
  session['country_avail'][index],session['country_avail'][0]=session['country_avail'][0],session['country_avail'][index]

  session["season_avail"]   = season_dict[session['country']]
  session["season"]   = 'year'

  session["indicator"]   = session["indicator_avail"][0]
  session["region_avail"]   = regions[session['country']]
  session['region']   = session["region_avail"][0]

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

  refP = "to".join(str(t) for t in s["ref_period"])
  proP = "to".join(str(t) for t in s["proj_period"])
  periods={refP:s["ref_period"],proP:s["proj_period"]}

  COU=COUs[s['country']]

  indicator_label=lang_dict[lang][s['indicator']]+' ['+ind_dict[s['indicator']]['unit']+']'

  if request_type=='EWEMBI_plot':  filename=EWEMBI_plot_func(s,COU,refP,proP,region,periods,lang,indicator_label,lang_dict,plot_format)
  if request_type=='Projection_plot':  filename=Projection_plot_func(s,COU,refP,proP,region,periods,lang,indicator_label,lang_dict,plot_format)
  if request_type=='transient_plot':  filename=transient_plot_func(s,COU,refP,proP,region,periods,lang,indicator_label,lang_dict,plot_format)
  if request_type=='annual_cycle_plot':  filename=annual_cycle_plot_func(s,COU,refP,proP,region,periods,lang,indicator_label,lang_dict,plot_format)

  if request_type=='get_data':  
    curretn_path=os.getcwd()
    os.chdir('../country_analysis/data/'+s['country']+'/')
    os.system('tar -vzcf ../'+s['country']+'_'+s['indicator']+'.tar.gz area_average/*-'+s['indicator']+'_* raw/*_'+s['indicator']+'_*')
    os.chdir(curretn_path)
    filename=s['country']+'_'+s['indicator']+'.tar.gz'

  print filename

  #print glob.glob(settings.basepath+'projection_sharing/app/'+'../../country_analysis/data/*')
  if 'get_data' in request_type.split('**'):
    return send_from_directory(directory=settings.basepath+'country_analysis/data/', filename=filename.replace('app/',''),as_attachment=True)

  if 'plot' in request_type.split('_'):
    return send_from_directory(directory=settings.basepath+'projection_sharing/app/', filename=filename.replace('app/',''),as_attachment=True)


###############################
# Navigation
###############################

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

@app.route('/documentation',  methods=('GET', ))
def render_docu():
  return render_template('documentation.html')



# @app.route('/go_to_model_agreement',  methods=("POST", ))
# def go_to_model_agreement():
#   return redirect(url_for("model_agreement"))

# @app.route('/go_to_bias_correction',  methods=("POST", ))
# def go_to_bias_correction():
#   return redirect(url_for("bias_correction"))

# @app.route('/model_agreement')
# def model_agreement():
#   try:
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
#   try:
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

