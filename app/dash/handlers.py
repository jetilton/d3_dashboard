from app import db
from flask import render_template, url_for, flash, redirect, request
from app.models import Cbt


from app.dash import bp
from cwms_read.cwms_read import get_cwms





@bp.route('/<cbt>/dash', methods = ['GET'])
def dash_cbt(cbt):
    return render_template('dash/dash.html')
    
    
@bp.route('/hydrographdata/<cbt>', methods = ['GET'])
def dash_data(cbt):
    cbt = Cbt.query.filter_by(cbt=cbt).first()
    
    return render_template('dash/dash.html')