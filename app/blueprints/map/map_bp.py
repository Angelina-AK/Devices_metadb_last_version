
from flask import Blueprint, render_template

from app.models import *

map_bp = Blueprint('map_bp', __name__, template_folder='templates', static_folder='static')


"""
@app.route('/map')
def map():
    namepage="Карта"
    return render_template('map.html', namepage=namepage)
"""


@map_bp.route('/map')
def map():
    jsond = ""
    namepage="Карта"
    return render_template('gmap.html', namepage=namepage)
