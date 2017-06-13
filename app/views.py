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


from app import app
from flask import redirect, render_template, url_for, request, flash, get_flashed_messages, g, session, jsonify, Flask, send_from_directory
from collections import OrderedDict
from werkzeug.routing import BuildError
import settings
import forms

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

  session["season_avail"]   = season_dict[session['country']]
  session["season"]   = session["season_avail"][0]

  print session
  return redirect(url_for("choices"))

@app.route('/choices')
def choices():
  if True: 
    print session
    s=session
    lang=s['language']

    form_country = forms.countryForm(request.form)
    form_country.countrys.choices = zip(s['country_avail'],s['country_avail'])
    form_country.countrys.label = form_labels[lang]['country']

    form_region = forms.regionForm(request.form)
    form_region.regions.choices = zip(s['region_avail'],s['region_avail'])
    form_region.regions.label = form_labels[lang]['region']

    form_scenario = forms.scenarioForm(request.form)
    form_scenario.scenarios.choices = zip(s['scenario_avail'],s['scenario_avail'])
    form_scenario.scenarios.label = form_labels[lang]['scenario']

    form_dataset = forms.datasetForm(request.form)
    form_dataset.datasets.choices = zip(s['dataset_avail'],s['dataset_avail'])
    form_dataset.datasets.label = 'Dataset'

    form_indicator = forms.indicatorForm(request.form)
    form_indicator.indicators.choices = zip(s['indicator_avail'],[lang_dict[lang][ind] for ind in s['indicator_avail']])
    form_indicator.indicators.label = form_labels[lang]['indicator']

    form_period = forms.PeriodField(request.form)
    ref_P = "-".join(str(t) for t in session["ref_period"])
    proj_P = "-".join(str(t) for t in session["proj_period"])
  
    form_period = forms.PeriodField(request.form, proj_period=proj_P, ref_period=ref_P)

    form_season = forms.seasonForm(request.form)
    form_season.seasons.choices = zip(s['season_avail'],[lang_dict[lang][sea] for sea in s['season_avail']])
    form_season.seasons.label = form_labels[lang]['season']

    refP = "-".join(str(t) for t in s["ref_period"])
    proP = "-".join(str(t) for t in s["proj_period"])
    periods={refP:s["ref_period"],proP:s["proj_period"]}

    print periods

    EWEMBI_plot='static/images/'+s['country']+'/'+s['indicator']+'_EWEMBI_ref_'+s['season']+'.png'
    transient_plot='static/images/'+s['country']+'/'+s['indicator']+'_'+s["dataset"]+'_'+s['region']+'_'+s['season']+'_transient.png'
    annual_cycle_plot='static/images/'+s['country']+'/'+s['indicator']+'_'+s["dataset"]+'_'+s['region']+'_annual_cycle_'+proP+'-ref.png'

    COU=COUs[s['country']]
    ens_selection=COU.selection([s['indicator'],s['dataset']])
    ens_mean=COU.selection([s['indicator'],s['dataset'],'ensemble_mean'])[0]


    Projection_plot='projection_sharing/app/static/images/'+s['country']+'_'+s['indicator']+'_'+s["scenario"]+'_'+s["dataset"]+'_'+proP+'-'+refP+'_'+s['season']+'_'+s['region']+'.png'
    COU.period_statistics(periods=periods,selection=ens_selection,ref_name=refP)
    COU.period_model_agreement()
    print ens_mean.period
    ens_mean.display_map(out_file=Projection_plot,
      highlight_region=s['region'],
      period='diff_'+proP+'-'+refP,
      color_label='bla',
      title='blala'
      )

    if s['user_type']=='advanced': advanced_col='white'
    if s['user_type']=='beginner':  advanced_col='gray'

    if lang=='fr':
      language=languages['en']
      EWEMBI_plot_title=u"Observations pour la période de réference 1986-2006"
      Projection_plot_title=u"Changement projeté pour la période "+proP+" par rapport à la période de réfernce 1986-2006"
      transient_plot_title='Moyenne régionale pour les observations et projections'
      annual_cycle_plot_title='Cycle annuel pour les observations durant la période de réference 1986-2006 et les projections pour la période '+proP

    if lang=='en':
      language=languages['fr']
      EWEMBI_plot_title=u"Observations over the reference period 1986-2006"
      Projection_plot_title=u"Change projected for the period "+proP+" with respect to the reference period 1986-2006"
      transient_plot_title='Regional average for observations and projections'     
      annual_cycle_plot_title='Annual cycle for observations over the reference period 1986-2006 and projections over the period '+proP

    context = { 
      'language':language,
      'advanced_col':advanced_col,
      'user_type':s['user_type'],
      'language_flag':languages[s['language']],
      'form_country':form_country,
      'form_country':form_country,
      'form_region':form_region,
      'form_period':form_period,
      'form_season':form_season,
      'form_scenario':form_scenario,
      'form_dataset':form_dataset,
      'form_indicator':form_indicator,
      'EWEMBI_plot':EWEMBI_plot,
      'EWEMBI_plot_title':EWEMBI_plot_title,
      'Projection_plot':Projection_plot.replace('projection_sharing/app/',''),
      'Projection_plot_title':Projection_plot_title,
      'annual_cycle_plot':annual_cycle_plot,
      'annual_cycle_plot_title':annual_cycle_plot_title,
      'transient_plot':transient_plot,
      'transient_plot_title':transient_plot_title
    }
    return render_template('choices.html',**context)

  # except KeyError:
  #   return redirect(url_for("index"))

@app.route('/model_agreement')
def model_agreement():
  try:
    country=session['country']

    form_period = forms.periodForm(request.form)
    form_period.periods.choices = zip(session['period_avail'],session['period_avail'])

    refP = "-".join(str(t) for t in session["ref_period"])
    proP = session['period']
    periods={'ref':session["ref_period"],'projection':session["proj_period"]}
    CORDEX_BC_plot_detail='static/images/'+country+'/'+session["indicator"]+'_'+session["scenario"]+'_'+session['dataset']+'_'+session['season']+'_details.png'

    context = { 
      'CORDEX_BC_plot_detail':CORDEX_BC_plot_detail,
    }
    return render_template('model_agreement.html',**context)

  except KeyError:
    return redirect(url_for("index"))

@app.route('/bias_correction')
def bias_correction():
  try:
    country=session['country']

    form_period = forms.PeriodField(request.form)
    form_period.periods.choices = zip(session['period_avail'],session['period_avail'])

    refP = "-".join(str(t) for t in session["ref_period"])
    proP = session['period']
    periods={'ref':session["ref_period"],'projection':session["proj_period"]}
    bias_corretion_check='static/images/'+country+'/'+session["indicator"]+'_BC_check_'+session['season']+'.png'

    context = { 
      'bias_corretion_check':bias_corretion_check
    }
    return render_template('bias_correction.html',**context)

  except KeyError:
    return redirect(url_for("index"))

@app.route('/go_to_choices',  methods=("POST", ))
def go_to_choices():
  return redirect(url_for("choices"))

@app.route('/go_to_model_agreement',  methods=("POST", ))
def go_to_model_agreement():
  return redirect(url_for("model_agreement"))

@app.route('/go_to_bias_correction',  methods=("POST", ))
def go_to_bias_correction():
  return redirect(url_for("bias_correction"))

@app.route('/<path:filename>', methods=['GET', 'POST'])
def download(filename):    
  return send_from_directory(directory='/Users/peterpfleiderer/Documents/Projects/projection_sharing/app/', filename=filename,as_attachment=True)

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


@app.route('/period_choice__',  methods=('POST', ))
def period_choice__():
  form_period = forms.periodForm(request.form)
  session['period']=form_period.periods.data
  # put chosen at beginning of list
  index=session['period_avail'].index(session['period'])
  session['period_avail'][index],session['period_avail'][0]=session['period_avail'][0],session['period_avail'][index]
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
  COU=COUs[session['country']]
  area=COU.get_region_area(session['region'])
  print area
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


