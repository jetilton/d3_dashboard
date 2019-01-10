from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FloatField, SelectField, HiddenField
from wtforms.validators import DataRequired

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
	tw_el_path = SelectField('Tailwater Elevation Path')
	fb_el_path = SelectField('Forebay Elevation Path')
	flow_out_path = SelectField('Outflow Path')
	spill_flow_path = SelectField('Spill Flow Path')
	gen_flow_path = SelectField('Generation Flow Path')
	submit = SubmitField('Submit')

class PathsForm(FlaskForm):
	name = StringField('Name', validators = [DataRequired()])
	paths = SelectField('Path')
	cbt_id = HiddenField('CBT ID', validators = [DataRequired()])
