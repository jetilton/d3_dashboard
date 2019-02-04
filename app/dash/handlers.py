from app import db
from flask import render_template, url_for, flash, redirect, request
from app.map.forms import CbtForm, PathsForm, add_paths
from flask_login import login_required
from app.models import Cbt, Paths
from flask import abort
import json
import requests
from app.dash import bp





@bp.route('/<cbt>/dash', methods = ['GET'])
def dash_cbt(cbt):
        return render_template('dash/dash.html')