from app import db
from flask import render_template, url_for, flash, redirect, request
from app.map.forms import CbtForm, PathsForm, add_paths
from flask_login import login_required
from app.models import Cbt, Paths
from flask import abort
import json
import requests
from app.map import bp




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
    fb = Paths.query.filter_by(cbt = cbt.cbt, parameter = "Forebay Elevation").first()
    
    tw = Paths.query.filter_by(cbt = cbt.cbt, parameter = "Tailwater Elevation").first()
    return render_template('map/cbt_modal.html', cbt = cbt.cbt, 
                           title = cbt.name, 
                           paths = paths, 
                           fb = fb,
                           tw = tw)

