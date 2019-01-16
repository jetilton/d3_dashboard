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

def path_check(field_2, field_3):
    message = 'Need to set a path' 

    def _path_check(form, field):
        if not field.data and  (form.__dict__[field_2].data or form.__dict__[field_3].data):
            raise ValidationError(message)
    
    return _path_check

def path_parameter_check(field_2, field_3):
    message_1 = 'Need to set a parameter name' 
    message_2 = 'Need to set a path'
    def _path_parameter_check(form, field):
        if field.data and not (form.__dict__[field_2].data or form.__dict__[field_3].data):
            raise ValidationError(message_1)
        if not field.data and  (form.__dict__[field_2].data or form.__dict__[field_3].data):
            raise ValidationError(message_2)
    
    return _path_parameter_check

def duplicate_path_check(paths):
    message = "Can not select duplicate paths"
    
        
    def duplicate_path_check(form, field):
        data_list = []
        for i in range(len(paths)):
            path_name = 'path_{}'.format(str(i))
            data = form.__dict__[path_name].data
            if data: data_list.append(data)
        d = [x for x in data_list if x == field.data]
        if len(d)>1:
            raise ValidationError(message)
        
    
    return duplicate_path_check


def duplicate_param_check(paths):
    message = "Parameter already set"
    
        
    def _duplicate_param_check(form, field):
        data_list = []
        for i in range(len(paths)):
            param_name = 'param_{}'.format(str(i))
            custom_param_name = 'custom_param_{}'.format(str(i))
            data = form.__dict__[param_name].data
            if data: data_list.append(data)
            data = form.__dict__[custom_param_name].data
            if data: data_list.append(data)
        d = [x for x in data_list if x == field.data]
        if len(d)>1:
            raise ValidationError(message)
        
    
    return _duplicate_param_check

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
                                validators = [parameter_check(custom_param_name),duplicate_param_check(paths)])
        parameter.id = param_name
        custom_parameter = StringField('Custom Parameter', validators = [parameter_check(param_name),duplicate_param_check(paths)])
        custom_parameter.id = custom_param_name
    
        path_field = SelectField('Path', choices = choices, validators = [path_parameter_check(param_name, custom_param_name), duplicate_path_check(paths)])
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
    
    

    
        
        
    
        
        
    
        