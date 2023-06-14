
from flask import Blueprint, request, render_template, flash, url_for, redirect, jsonify
from flask_login import login_required
from app.models import Record, RecordData, Device, Payload, Decoder

from py_mini_racer import py_mini_racer
ctx = py_mini_racer.MiniRacer()

from app.models import db
from werkzeug.exceptions import abort

import js2py
import json

gateway_api = Blueprint('gateway_api', __name__, template_folder='templates')

import pytz
import datetime


def get_decoder_payload(id):
    decoder_payload = Decoder.query.filter(Decoder.device_id == id).first()

    if decoder_payload is None:
        return None
    return decoder_payload


@gateway_api.route('/gateway/<key>', methods=('POST','GET'))
def add_data(key):
    device = Device.query.filter(Device.key == key).first()
    # decoder_format = get_decoder_payload(device.id)

    # if decoder_format is not None:
    #    decoded = (paylaod_decode(decoder_format.value, data))
    #    if decoded != "error":

    if request.method == 'POST':

        if request.is_json:
            print ("POST json")
            data = request.get_json()
            data = json.dumps(data, sort_keys=True)

        else:
            if len(request.form) > 0:
                print("POST form")
                data = request.form
                data = json.dumps(data, sort_keys=True)

            else:
                print("else post")
                data = request.stream.read().decode("utf-8")
                # data = repr(data)

    elif request.method == 'GET':
        print("get")
        data = request.args
        # data = jsonify(data)
        data = json.dumps(data, sort_keys=True)

    else:
        print("else")
        # data = request.get_data()

    new_record = Payload(device_id=device.id, value=data)
    db.session.add(new_record)
    db.session.commit()
    db.session.flush()  # updates the objects of the session

    return data
