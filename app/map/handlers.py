from app import db
from flask import render_template, url_for, flash, redirect, request
from app.map.forms import CbtForm, PathsForm, add_paths
from flask_login import login_required
from app.models import Cbt, Paths
from flask import abort
import json
import requests
from app.map import bp
from flask_restful import reqparse
from datetime import datetime
from flask import jsonify


def time_window_url(paths, public=True, lookback = 7, start_date = False, end_date = False, timezone = 'PST'):
    """
    helper function for cwms_read
    
    Arguments:  
        
        path -- cwms data path, 
        public -- boolean, 
        start_date -- date integer tuple format (YYYY, m, d)
        end_date -- date integer tuple format (YYYY, m, d)
        timezone -- optional keyword argument if time zone is specified.  
                    Defaults to 'PST' if nothing set
    Returns:
        
        url -- url string of CWMS data webservice for the specified 
               data path and time window
               
    """

    if isinstance(paths, list): 
        path = '%22%2C%22'.join(paths)
    else: path = paths
        
    if public:
        url = r'http://pweb.crohms.org/dd/common/web_service/webexec/getjson?timezone=TIMEZONE_&query=%5B%22PATH%22%5D&'
    else:
        url = r'http://nwp-wmlocal2.nwp.usace.army.mil/common/web_service/webexec/getjson?timezone=TIMEZONE_&query=%5B%22PATH%22%5D&'
    
    url = url.replace('PATH', path).replace('TIMEZONE_', timezone)
    if lookback:
        time = 'backward=' + str(lookback) + 'd'
        url = url + time
    else:
        url = url + 'startdate=START_MONTH%2FSTART_DAY%2FSTART_YEAR+00%3A00&enddate=END_MONTH%2FEND_DAY%2FEND_YEAR+23%3A00'
        url = url.replace('START_MONTH', str(start_date.month)).replace('START_DAY', str(start_date.day)).replace('START_YEAR', str(start_date.year))
        url = url.replace('END_MONTH', str(end_date.month)).replace('END_DAY', str(end_date.day)).replace('END_YEAR', str(end_date.year))
    
    return url


@bp.route('/')
@bp.route('/index')
def index():
    cbts = Cbt.query.all()
    return render_template('map/index.html', cbts=cbts) 


@bp.route('/add_cbt/<cbt>', methods = ['GET', 'POST'])
@login_required
def add_cbt(cbt):
    cbt_form = CbtForm()
    cbt = cbt.upper()
    
    url = "http://www.nwd-wc.usace.army.mil/dd/common/web_service/webexec/getjson?tscatalog=%5B%22{}%22%5D".format(cbt)
    r = requests.get(url)
    data = json.loads(r.text)
    try:
        cbt_data = data[cbt]
    except KeyError:
        #error handling
        abort(404)
    if request.method == 'GET':
        cbt_form.name.data = cbt_data['name']
        cbt_form.latitude.data = cbt_data['coordinates']['latitude']
        cbt_form.longitude.data = cbt_data['coordinates']['longitude']
    if request.method == 'POST':
        if cbt_form.delete.data:
            Cbt.query.filter_by(cbt = cbt).delete()
            db.session.commit()
            flash('{} Deleted'.format(cbt))
            return redirect(url_for('map.index'))
        if cbt_form.validate_on_submit() and cbt_form.add.data:
            cbt = Cbt(cbt = cbt, name = cbt_form.name.data, latitude = cbt_form.latitude.data, longitude = cbt_form.longitude.data)
            db.session.add(cbt)
            db.session.commit()
            flash('{} added to map'.format(cbt_form.name.data))
        return redirect(url_for('map.edit_cbt', cbt = cbt.cbt))
    return render_template('map/add_cbt.html', data=data, cbt_form=cbt_form)



@bp.route('/edit_cbt/<cbt>', methods = ['GET','POST'])
@login_required
def edit_cbt(cbt):
    cbt = Cbt.query.filter_by(cbt=cbt.upper()).first_or_404()    
    url = "http://www.nwd-wc.usace.army.mil/dd/common/web_service/webexec/getjson?tscatalog=%5B%22{}%22%5D".format(cbt.cbt)
    r = requests.get(url)
    data = json.loads(r.text)[cbt.cbt]
    paths = list(data['timeseries'].keys())
    class F(PathsForm):
        pass
    F = add_paths(F,paths)
    form = F()
    form.cbt.data = cbt.cbt
    added_paths = 0
    
    if form.validate_on_submit():
        Paths.query.filter_by(cbt = cbt.cbt).delete()
        db.session.commit()
        for row in form.form_rows:
            if form.__dict__[row[0]].data or form.__dict__[row[1]].data:
                if row[0]:
                    parameter = form.__dict__[row[0]].data
                else:
                    parameter = form.__dict__[row[1]].data
                path = form.__dict__[row[2]].data
                p = Paths.query.filter_by(path=path, cbt = cbt.cbt).first()
                if p:
                    p.parameter = parameter
                else:
                    p = Paths(path = path, cbt = cbt.cbt, parameter= parameter)
                db.session.add(p)
                db.session.commit()
                added_paths+=1
        flash('{} paths added to {}'.format(str(added_paths), cbt.name))
        return redirect(url_for('map.index'))
    
    elif request.method == 'GET':
        table_rows = Paths.query.filter_by(cbt=cbt.cbt)
        form_rows = form.form_rows
        #rows = query.statement.execute.fetchall()
        for index,table_row in enumerate(table_rows):
            parameter = table_row.parameter
            path = table_row.path
            if (parameter, parameter) in form.parameter_choices:
                form.__dict__[form_rows[index][0]].data = parameter
            else:
                form.__dict__[form_rows[index][1]].data = parameter
            form.__dict__[form_rows[index][2]].data = path
            
    return render_template('map/edit_cbt.html', cbt=cbt, form=form,form_rows=form.form_rows)

@bp.route('/<cbt>/modal',methods = ['GET'])
def cbt_modal(cbt):
    cbt = Cbt.query.filter_by(cbt=cbt.upper()).first()
    paths = Paths.query.filter_by(cbt = cbt.cbt)
    return render_template('map/cbt_modal.html', cbt = cbt.cbt, title = cbt.name, paths = paths)

@bp.route('/cwms', methods = ['GET', 'POST'])
def cwms():
    parser = reqparse.RequestParser()
    parser.add_argument('paths', action='append')
    parser.add_argument('lookback', type=int)
    parser.add_argument('startdate', type=lambda x: datetime.strptime(x,'%Y-%m-%d') )
    parser.add_argument('enddate', type=lambda x: datetime.strptime(x,'%Y-%m-%d') )
    args = parser.parse_args()
    paths = args['paths']
    lookback = args['lookback']
    if lookback:
        start_date = False
        end_date = False
    else:
        start_date = args['startdate']
        end_date = args['enddate']
        lookback = False
    url = time_window_url(paths, public=True, lookback = lookback, start_date = start_date, end_date = end_date, timezone = 'PST')
    requests.packages.urllib3.disable_warnings() 
    data = json.loads(requests.get(url, verify = False).text)
    data_list = []
    for key,value in data.items():
        value['cbt'] = key
        pathname = list(value['timeseries'])[0]
        value['pathname'] = pathname
        vals = value['timeseries'][pathname]['values']
        ts_list = []
        for val in vals:
            ts_list.append({'date':val[0],'value':val[1],'flag':val[2]})
        value['timeseries'] = value['timeseries'][pathname]
        value['timeseries']['values'] = ts_list
        data_list.append(value)
    return jsonify(data_list)
