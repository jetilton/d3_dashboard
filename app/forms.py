from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FloatField, SelectField, HiddenField
from wtforms.validators import DataRequired
from app.models import Paths
from flask import flash

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



class PathsForm(FlaskForm):
    parameter = SelectField('Parameter', choices = [('',''),
                                                    ('forebay_elevation', 'Forebay Elevation'),
                                                    ('tailwater_elevation', 'Tailwater Elevation'),
                                                    ('flow_out', 'Flow Out')])
    custom_parameter = StringField('Custom Parameter')
    
    path_field = SelectField('Path')
    
    def __init__(self, paths, *args, **kwargs):
        
        
        super(PathsForm,self).__init__(*args, **kwargs)
        self.paths = paths
        
        i=0
        row_list = []
        for path in self.paths:
            param_name = 'param_{}'.format(str(i))
            custom_param_name = 'custom_param_{}'.format(str(i))
            path_name = 'path_{}'.format(str(i))
            
            self.path_field.choices = [('','')]+[(path,path) for path in self.paths]
            
            setattr(self, param_name, self.parameter)
            setattr(self, custom_param_name, self.custom_parameter)
            setattr(self, path_name, self.path_field)
            
            row_list.append((param_name, custom_param_name, path_name))
            i += 1
        self.row_list = row_list
    
    cbt_id = HiddenField('CBT ID', validators = [DataRequired()])
    submit = SubmitField('Submit')
        
#    def validate(self): 
#        paths = set()
#        params = list()
#        for row in self.row_list:
#            errors = tuple(' ')
#            if self.__getattribute__(row[0]).data and self.__getattribute__(row[0]).data:
#                self.__getattribute__(row[0]).errors=errors
#                self.__getattribute__(row[1]).errors=errors
#                flash('Can only set one parameter name')
#                return False
#            if not self[row[0]].data and not self[row[1]].data and self[row[2]].data:
#                self[row[0]].errors=errors
#                self[row[1]].errors=errors
#                flash('Path must have parameter name')
#                return False
#            if self[row[2]].data in paths:
#                self[row[2]].errors=errors
#                flash('Path already exists')
#                return False
#            elif self[row[2]].data:
#                paths.add(self[row[2]].data)
#            if (self[row[0]].data or self[row[1]].data) and not self[row[2]].data:
#                self[row[2]].errors=errors
#                flash('No path set')
#                return False
#            if (self[row[0]].data or self[row[1]].data):
#                if self[row[0]].data:
#                    param = self[row[0]].data
#                    self[row[0]].errors=errors
#                else:
#                    param = self[row[1]].data
#                    self[row[1]].errors=errors
#                if param in params:
#                    flash("Parameter already exists")
#                    return False
#                else:
#                    params.append(param)
#        return True




