from flask import render_template
from flask_breadcrumbs import  register_breadcrumb
from flask_login import current_user, login_required
from werkzeug.exceptions import abort

from app import app, db
from app.models import *


@app.before_first_request
def setup():
    db.create_all()


@app.route('/')
@register_breadcrumb(app, '.', 'Home')
@login_required
def index():
    namepage="DashBoard"
    devices = Device.query.filter(Device.user_id == current_user.id).all()
    count_devices = len(devices)
    count_records = 0;
    for device in devices:
        count_records += Record.query.filter(Record.device_id == device.id).count()
    
    return render_template('indexleo.html', namepage=namepage, count_devices=count_devices, count_records=count_records )
    # return render_template('index.html', namepage=namepage, count_devices=count_devices, count_records=count_records )


def get_param_value(id):
    param_value = DeviceParam.query.filter(DeviceParam.id == id).all()
    if param_value is None:
        abort(404)
    return param_value


"""
@app.route('/users', methods=['POST', 'GET'])
def handle_users():
    if request.method == 'GET':
        users = User.query.all()
        results = [
            {
                "name": user.username,
                "email": user.email
            } for user in users]
        return {"count": len(results), "users": results}
"""