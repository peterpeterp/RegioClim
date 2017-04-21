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
from flask import redirect, render_template, url_for, request, flash, get_flashed_messages, g, session, jsonify, Flask
from collections import OrderedDict
from werkzeug.routing import BuildError
import settings
import forms

import sys,glob,os,pickle,time
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import pandas as pd


import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt



def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field: %s" % (
                getattr(form, field).label.text,
                error
            ))

COU=settings.COU
indicator_dict=settings.indicator_dict

@app.route('/')
def index():
  session["country_avail"]   = settings.countrys
  session['country']   = settings.countrys[0]

  session["reference_period"]   = settings.reference_period
  session["projection_period"]  = settings.projection_period

  session["scenario_avail"]   = settings.scenarios
  session["scenario"]   = settings.scenarios[0]
  session["indicator_avail"]   = list(set([data.var_name for data in COU[session['country']]._DATA]))
  session["indicator"]   = session["indicator_avail"][0]
  session["region_avail"]   = COU[session['country']]._masks['360x720_lat_89.75_-89.75_lon_-179.75_179.75']['lat_weighted'].keys()
  session['region']   = session["region_avail"][0]

  print session


  return redirect(url_for("choices"))

@app.route('/choices')
def choices():
  print session
  country=session['country']
  indicator=session['indicator']

  form_scenario = forms.scenarioForm(request.form)
  form_scenario.scenarios.choices = zip(session['scenario_avail'],session['scenario_avail'])

  form_indicator = forms.indicatorForm(request.form)
  form_indicator.indicators.choices = zip(session['indicator_avail'],session['indicator_avail'])

  form_country = forms.countryForm(request.form)
  form_country.countrys.choices = zip(session['country_avail'],session['country_avail'])

  form_region = forms.regionForm(request.form)
  form_region.regions.choices = zip(session['region_avail'],session['region_avail'])

  refP = "-".join(str(t) for t in session["reference_period"])
  proP = "-".join(str(t) for t in session["projection_period"])

  form_period = forms.PeriodField(request.form, reference_period=refP, projection_period=proP)
  periods={'ref':session["reference_period"],'projection':session["projection_period"]}




  cordex=COU[country].selection([indicator,session["scenario"],'CORDEX_BC','ensemble_mean'])[0]
  CORDEX_BC_plot='static/images/'+country+'/'+indicator+'_'+session["scenario"]+'_CORDEX_BC_'+proP+'-'+refP+'.png'
  if os.path.isfile(CORDEX_BC_plot)==False:
    COU[country].period_averages(periods=periods,filters=[indicator,session["scenario"],'CORDEX_BC'])
    COU[country].model_agreement()
    cordex.display_map(period='diff_projection-ref',out_file=CORDEX_BC_plot,polygons=COU[country]._adm_polygons,title='projections',color_label=indicator_dict[indicator]['ylabel'])

  ewembi=COU[country].selection([indicator,'EWEMBI'])[0]
  EWEMBI_plot='static/images/'+country+'/'+indicator+'_EWEMBI_'+refP+'.png'
  if os.path.isfile(EWEMBI_plot)==False:
    COU[country].period_averages(periods=periods,filters=[indicator,'EWEMBI'])
    ewembi.display_map(period='ref',out_file=EWEMBI_plot,polygons=COU[country]._adm_polygons,title='observations',color_label=indicator_dict[indicator]['ylabel'])

  transient_plot='static/images/'+country+'/'+indicator+'_'+session['region']+'_transient.png'
  if os.path.isfile(transient_plot)==False:
    fig,ax=plt.subplots(nrows=1,ncols=1,figsize=(5,4))
    print ewembi.average['lat_weighted'].keys()
    ewembi.plot_transient(mask_style='lat_weighted',region=session['region'],running_mean_years=5,ax=ax,title='',ylabel=None,label='observation')
    cordex.plot_transient(mask_style='lat_weighted',region=session['region'],running_mean_years=5,ax=ax,title='',ylabel=None,label='projection')
    ax.set_ylabel(indicator_dict[indicator]['ylabel'])
    ax.set_title('transient plot')
    plt.legend(loc='best')
    plt.savefig(transient_plot)

  if cordex.time_step=='monthly':
    annual_cycle_plot='static/images/'+country+'/'+indicator+'_'+session['region']+'_annual_cycle_'+proP+'-'+refP+'.png'
    if os.path.isfile(annual_cycle_plot)==False:
      fig,ax=plt.subplots(nrows=1,ncols=1,figsize=(5,4))
      ewembi.plot_annual_cycle(period=session["reference_period"],mask_style='lat_weighted',region=session['region'],ax=ax,title='',ylabel=None,label='observation')
      cordex.plot_annual_cycle(period=session["projection_period"],mask_style='lat_weighted',region=session['region'],ax=ax,title='',ylabel=None,label='projection')
      ax.set_title('annual cycle plot')
      ax.set_ylabel(indicator_dict[indicator]['ylabel'])
      plt.legend(loc='best')
      plt.savefig(annual_cycle_plot)
  else:
    annual_cycle_plot='bla'

  context = { 
    'form_country':form_country,
    'form_region':form_region,
    'form_period':form_period,
    'form_scenario':form_scenario,
    'form_indicator':form_indicator,
    'EWEMBI_plot':EWEMBI_plot,
    'CORDEX_BC_plot':CORDEX_BC_plot,
    'annual_cycle_plot':annual_cycle_plot,
    'transient_plot':transient_plot
  }
  print EWEMBI_plot

  return render_template('choices.html',**context)

@app.route('/details')
def details():
  country=session['country']

  refP = "-".join(str(t) for t in session["reference_period"])
  proP = "-".join(str(t) for t in session["projection_period"])

  form_period = forms.PeriodField(request.form, reference_period=refP, projection_period=proP)
  periods={'ref':session["reference_period"],'projection':session["projection_period"]}

  CORDEX_BC_plot_detail='static/images/'+country+'/'+session["indicator"]+'_'+session["scenario"]+'_CORDEX_BC_'+proP+'-'+refP+'_detials.png'
  if os.path.isfile(CORDEX_BC_plot_detail)==False:
    COU[country].period_averages(periods=periods,filters=[session["indicator"],session["scenario"],'CORDEX_BC'])
    COU[country].model_agreement()
    fig,axes=plt.subplots(nrows=1,ncols=5,figsize=(6,4))
    axes=axes.flatten()
    selection=COU[country].selection([session["indicator"],session["scenario"],'CORDEX_BC'])
    for model,i in zip(selection,range(len(selection))):
      print model.period.keys()
      im=model.display_map(period='diff_projection-ref',ax=axes[i],title=model.model,color_bar=False)
    cbar_ax=fig.add_axes([0.3,0.2,0.4,0.6])
    cbar_ax.axis('off')
    cb=fig.colorbar(im,orientation='horizontal',label='')
    plt.savefig(CORDEX_BC_plot_detail)

  context = { 
    'CORDEX_BC_plot_detail':CORDEX_BC_plot_detail
  }

  return render_template('details.html',**context)


@app.route('/go_to_choices',  methods=("POST", ))
def go_to_choices():
  return redirect(url_for("choices"))

@app.route('/go_to_details',  methods=("POST", ))
def go_to_details():
  return redirect(url_for("details"))

@app.route('/periodchoice',  methods=("POST", ))
def add_periodchoice():

  form_period = forms.PeriodField(request.form)

  if form_period.validate_on_submit():
    session["reference_period"] = [int(t) for t in form_period.reference_period.data.split("-")]
    session["projection_period"]   = [int(t) for t in form_period.projection_period.data.split("-")]

  else:
    flash_errors(form_period)

  return redirect(url_for("choices"))

@app.route('/scenario_choice',  methods=('POST', ))
def scenario_choice():
  form_scenario = forms.scenarioForm(request.form)
  session['scenario']=form_scenario.scenarios.data
  # put chosen at beginning of list
  index=session['scenario_avail'].index(session['scenario'])
  session['scenario_avail'][index],session['scenario_avail'][0]=session['scenario_avail'][0],session['scenario_avail'][index]
  return redirect(url_for('choices'))

@app.route('/indicator_choice',  methods=('POST', ))
def indicator_choice():
  form_indicator = forms.indicatorForm(request.form)
  session['indicator']=form_indicator.indicators.data
  # put chosen at beginning of list
  index=session['indicator_avail'].index(session['indicator'])
  session['indicator_avail'][index],session['indicator_avail'][0]=session['indicator_avail'][0],session['indicator_avail'][index]
  return redirect(url_for('choices'))

@app.route('/period_choice',  methods=('POST', ))
def period_choice():
  form_period = forms.periodForm(request.form)
  session['period']=form_period.periods.data
  # put chosen at beginning of list
  index=session['period_avail'].index(session['period'])
  session['period_avail'][index],session['period_avail'][0]=session['period_avail'][0],session['period_avail'][index]
  return redirect(url_for('choices'))

@app.route('/region_choice',  methods=('POST', ))
def region_choice():
  form_region = forms.regionForm(request.form)
  session['region']=form_region.regions.data
  # put chosen at beginning of list
  index=session['region_avail'].index(session['region'])
  session['region_avail'][index],session['region_avail'][0]=session['region_avail'][0],session['region_avail'][index]
  return redirect(url_for('choices'))

@app.route('/country_choice',  methods=('POST', ))
def country_choice():
  print '------------------------'
  form_country = forms.countryForm(request.form)
  session['country']=form_country.countrys.data
  # put chosen at beginning of list
  index=session['country_avail'].index(session['country'])
  session['country_avail'][index],session['country_avail'][0]=session['country_avail'][0],session['country_avail'][index]

  session["indicator_avail"]   = list(set([data.var_name for data in COU[session['country']]._DATA]))
  session["indicator"]   = session["indicator_avail"][0]
  session["region_avail"]   = COU[session['country']]._masks['360x720_lat_89.75_-89.75_lon_-179.75_179.75']['lat_weighted'].keys()
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


