from flask import Blueprint, request, render_template, flash, url_for, redirect

from flask_login import login_required, current_user



import datetime
import pytz

time_api = Blueprint('time_api', __name__, template_folder='templates')


def get_time():
    if current_user.timezone is not None:
        tz = pytz.timezone(current_user.timezone)
        ct = datetime.datetime.now(tz=tz)
    else:
        ct = datetime.datetime.now
    return ct

