from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FloatField, SelectField, HiddenField
from wtforms.validators import DataRequired, ValidationError
from app.models import Paths
from flask import flash
import copy

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




def parameter_check(field_2):
    message = 'Can only set one parameter name' 

    def _parameter_check(form, field):
        if field.data and form.__dict__[field_2].data:
            raise ValidationError(message)
    
    return _parameter_check


def add_paths(PathsForm, paths):
    choices = [('','')]+[(path,path) for path in paths]
    i=0
    row_list = []
    for path in paths:
        param_name = 'param_{}'.format(str(i))
        custom_param_name = 'custom_param_{}'.format(str(i))
        path_name = 'path_{}'.format(str(i))
        row_list.append((param_name,custom_param_name,path_name))
        parameter = SelectField('Parameter', choices = [('',''),
                                                    ('forebay_elevation', 'Forebay Elevation'),
                                                    ('tailwater_elevation', 'Tailwater Elevation'),
                                                    ('flow_out', 'Flow Out')],
                                validators = [parameter_check(custom_param_name)])
        parameter.id = param_name
        custom_parameter = StringField('Custom Parameter', validators = [parameter_check(param_name)])
        custom_parameter.id = custom_param_name
    
        path_field = SelectField('Path', choices = choices)
        path_field.id = path_name
        
        setattr(PathsForm, param_name, parameter)
        setattr(PathsForm, custom_param_name, custom_parameter)
        setattr(PathsForm, path_name, path_field)
        i+=1
    setattr(PathsForm, 'submit', SubmitField('Submit'))
    setattr(PathsForm, 'row_list', row_list)
    return PathsForm

class PathsForm(FlaskForm):
    
    cbt_id = HiddenField('CBT ID', validators = [DataRequired()])
    
    

    
        
        
    
        
        
    
        