from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FloatField, SelectField, HiddenField
from wtforms.validators import DataRequired
from app.models import Paths

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class CbtForm(FlaskForm):
	name = StringField('Site Name', validators = [DataRequired()])
	latitude = FloatField('latitude', validators = [DataRequired()])
	longitude = FloatField('longitude', validators = [DataRequired()])
	add = BooleanField('Add to map')
	submit = SubmitField('Submit')


#class PathsForm(FlaskForm):
#    cbt_id = HiddenField('CBT ID', validators = [DataRequired()])
#    parameter = SelectField('Parameter', choices = [('',''),
#                                                    ('forebay_elevation', 'Forebay Elevation'),
#                                                    ('tailwater_elevation', 'Tailwater Elevation'),
#                                                    ('flow_out', 'Flow Out')])
#    custom_parameter = StringField('Custom Parameter')
#    path = SelectField('Path')
#    



class PathsForm(FlaskForm):
    pass
    
    

#    cbt_id = HiddenField('CBT ID', validators = [DataRequired()])
#    parameter = SelectField('Parameter', choices = [('',''),
#                                                    ('forebay_elevation', 'Forebay Elevation'),
#                                                    ('tailwater_elevation', 'Tailwater Elevation'),
#                                                    ('flow_out', 'Flow Out')])
#    custom_parameter = StringField('Custom Parameter')
#    path = SelectField('Path')