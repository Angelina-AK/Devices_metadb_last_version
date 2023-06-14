import json
import os
from uuid import uuid4

from flask import (Blueprint, flash, jsonify, redirect, render_template, request, url_for)
from flask_breadcrumbs import register_breadcrumb
from flask_login import current_user, login_required
from PIL import Image
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

from app.models import (Building, Decoder, Device, Floor, Payload, Record,
                        Sensor, User, db)

visual_api = Blueprint('visual_api', __name__, template_folder='templates', url_prefix='/chart', static_folder='static')


def get_decoder_payload(id):
    decoder_payload = Decoder.query.filter(Decoder.device_id == id).first()

    if decoder_payload is None:
        return None
    return decoder_payload


def view_device_dlc(*args, **kwargs):
    device_id = request.view_args['device_id']
    device = Device.query.get(device_id)
    return [{'text': device.name, 'url': device.id}]


def view_four_charts_dlc(*args, **kwargs):
    device_id = request.view_args['device_id']
    device = Device.query.get(device_id)
    return [{'text': device.name, 'url': f'/chart/chart_four/{device_id}'}]

def view_device_sensor_dlc(*args, **kwargs):
    sensor_id = request.view_args['sensor_id']
    sensor = Sensor.query.get(sensor_id)
    device = '/chart/' + str(sensor.device.id)
    return [{'text': sensor.device.name, 'url': device}, {'text': sensor.name, 'url': sensor.id}]


@visual_api.route('/<int:device_id>')
@register_breadcrumb(visual_api, '.chart/', '', dynamic_list_constructor=view_device_dlc)
@login_required
def chart_view_all(device_id):
    payloads = Payload.query.filter(Payload.device_id == device_id).order_by(Payload.created.desc()).limit(500).all()
    payloads = payloads[::4]
    decoder_format = get_decoder_payload(device_id)

    sensors = Sensor.query.filter(Sensor.device_id == device_id).all()

    return render_template('chartall.html', device_id=device_id, payloads=payloads, sensors=sensors, decoder_format=decoder_format)


@visual_api.route('/<int:device_id>/get_data')
def get_data(device_id):
    payloads = Payload.query.filter(Payload.device_id == device_id).order_by(Payload.created.desc()).limit(500).all()
    payloads = payloads[::4]
    data = []
    for payload in payloads:
        data.append(payload.toDict())
    return jsonify(data)


@visual_api.route('/chartn/<int:device_id>')
@register_breadcrumb(visual_api, '.chart/', '', dynamic_list_constructor=view_device_dlc)
@login_required
def chart_view_all_new(device_id):
    payloads = Payload.query.filter(Payload.device_id == device_id).order_by(Payload.created.desc()).limit(500).all()
    payloads = payloads[::4]
    decoder_format = get_decoder_payload(device_id)

    sensors = Sensor.query.filter(Sensor.device_id == device_id).all()

    return render_template('chartallnew.html', device_id=device_id, payloads=payloads, sensors=sensors, decoder_format=decoder_format)


@visual_api.route('/chart_four/<int:device_id>')
@register_breadcrumb(visual_api, '.devices_view', '', dynamic_list_constructor=view_four_charts_dlc)
def chart_four(device_id):
    payloads = Payload.query.filter(Payload.device_id == device_id).order_by(Payload.created.asc()).limit(500).all()
    payloads = payloads[::4]
    decoder_format = get_decoder_payload(device_id)
    room = Device.query.filter(Device.id == device_id).first().name.split('-')[0]
    sensors = Sensor.query.filter(Sensor.device_id == device_id).all()
    sensors = sensors[0:len(sensors)-2:1]


    return render_template('chart_four.html', device_id=device_id, payloads=payloads, sensors=sensors, decoder_format=decoder_format, room=room)


@visual_api.route('/four_chart/<int:device_id>/get_data')
def get_data_four_chart(device_id):
    payloads = Payload.query.filter(Payload.device_id == device_id).order_by(Payload.created.desc()).limit(2150).all()
    payloads = payloads[::50]
    data = []
    for payload in payloads:
        data.append(payload.toDict())
    return jsonify(data)


@visual_api.route('/chart/<int:device_id>/<int:sensor_id>')
@register_breadcrumb(visual_api, '.chart/device_id/', '',
                                 dynamic_list_constructor=view_device_sensor_dlc)
@login_required
def chart_view(device_id, sensor_id):
    payloads = Payload.query.filter(Payload.device_id == device_id).order_by(Payload.created.desc()).limit(200).all()
    decoder_format = get_decoder_payload(device_id)

    sensor = Sensor.query.get(sensor_id)

    return render_template('chart.html', payloads=payloads, sensor=sensor, decoder_format=decoder_format)


@visual_api.route('/')
@register_breadcrumb(visual_api, '.', 'Сharts')
@login_required
def devices_view():
    devices = Device.query.filter(Device.user_id == current_user.id).all()
    print(devices)
    return render_template('devices_chart.html', devices=devices)
