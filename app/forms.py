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


from wtforms import RadioField, SelectMultipleField, TextField, IntegerField, SelectField, StringField
from flask.ext.wtf import Form, validators
from wtforms.validators import ValidationError, Required, Regexp


class countryForm(Form):
  countrys = SelectField(' ', choices=[],
            validators=[Required("Please select at least one region.")])

class regionForm(Form):
  regions = SelectField(u'Administrative region:<br>(only relevant for transient and annual cycle)', choices=[],
            validators=[Required("Please select at least one region.")])

class indicatorForm(Form):
  indicators = SelectField(u'Climate Indicator', choices=[],
            validators=[Required("Please select at least one region.")])

class scenarioForm(Form):
  scenarios = SelectField(u'Available Scenarios', choices=[],
            validators=[Required("Please select at least one region.")])

class datasetForm(Form):
  datasets = SelectField(u'Available Datasets', choices=[],
            validators=[Required("Please select at least one region.")])




class periodForm(Form):
  periods = SelectField(u'Available periods', choices=[],
            validators=[Required("Please select at least one period.")])

class seasonForm(Form):
  seasons = SelectField(u'Available seasons', choices=[],
            validators=[Required("Please select at least one season.")])

# class PeriodField(Form):
#   regex = "[1-2][0-9]{3}-[1-2][0-9]{3}"

#   reference_period    = TextField(u'Refernce  Period', validators=[Regexp(regex, message="Please use YYYY-YYYY format.")])
#   projection_period   = TextField(u'Projection Period', validators=[Regexp(regex, message="Please use YYYY-YYYY format.")])

