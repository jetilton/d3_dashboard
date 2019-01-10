from app import app, db
from flask import render_template, url_for, flash, redirect, request
from app.forms import LoginForm, CbtForm, PathsForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Cbt 
from werkzeug.urls import url_parse
from flask import abort, jsonify
import json
import requests
from app import csrf
 
@app.route('/')
@app.route('/index')
def index():
	cbts = Cbt.query.all()
	return render_template('index.html', cbts=cbts) 


@app.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user is None or not user.check_password(form.password.data):
			flash('Invalid username or password')
			return redirect(url_for('login'))
		login_user(user, remember=form.remember_me.data)
		next_page = request.args.get('next')
		if not next_page or url_parse(next_page).netloc != '':
			next_page = url_for('index')
		return redirect(next_page)
	return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))

@app.route('/add_cbt/<cbt>', methods = ['GET', 'POST'])
@login_required
def add_cbt(cbt):
	form = CbtForm()
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
		form.name.data = cbt_data['name']
		form.latitude.data = cbt_data['coordinates']['latitude']
		form.longitude.data = cbt_data['coordinates']['longitude']
		form.tw_el_path.choices = [' ']+list(cbt_data['timeseries'].keys())
		form.fb_el_path.choices = [' ']+list(cbt_data['timeseries'].keys())
		form.flow_out_path.choices = [' ']+list(cbt_data['timeseries'].keys())
		form.spill_flow_path.choices = [' ']+list(cbt_data['timeseries'].keys())
		form.gen_flow_path.choices = [' ']+list(cbt_data['timeseries'].keys())

	if form.validate_on_submit() and form.add.data:
		cbt = Cbt(cbt = cbt, name = form.name.data, latitude = form.latitude.data, longitude = form.longitude.data)
		db.session.add(cbt)
		db.session.commit()
		flash('{} added to map'.format(form.name.data))
		return redirect(url_for('index'))
	return render_template('add_cbt.html', data=data, form=form)

@app.route('/edit_cbt/<cbt>', methods = ['GET','POST'])
@login_required
def edit_cbt(cbt):
	cbt = Cbt.query.filter_by(cbt=cbt.upper()).first_or_404()	
	url = "http://www.nwd-wc.usace.army.mil/dd/common/web_service/webexec/getjson?tscatalog=%5B%22{}%22%5D".format(cbt.cbt)
	r = requests.get(url)
	data = json.loads(r.text)[cbt.cbt]
	paths = list(data['timeseries'].keys())
	choices = [(path, path) for path in paths]
	form = PathsForm()
	form.paths.choices = choices
	form.cbt_id.data = cbt.id
	return render_template('edit_cbt.html', cbt=cbt, form=form)

@app.route('/process_cbt', methods = ['POST'])
@login_required
def process_cbt():
	form = PathsForm()
	choice = request.form.get('paths')
	form.paths.choices = [(choice,choice)]
	if form.validate_on_submit():
		return jsonify(data={'message':'success'})
	return jsonify(data={'message': 'Failure'})
