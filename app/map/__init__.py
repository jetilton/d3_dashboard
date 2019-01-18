# -*- coding: utf-8 -*-

from flask import Blueprint

bp = Blueprint('map', __name__, template_folder='templates')

from app.map import handlers