
import json

import js2py
from flask import (Blueprint, flash, jsonify, redirect, render_template,
                   request, url_for)
from flask_breadcrumbs import default_breadcrumb_root, register_breadcrumb
from flask_login import login_required
from werkzeug.exceptions import abort

from app.models import Decoder, Device, Payload, Record, RecordData, db

records_api = Blueprint('records_api', __name__, template_folder='templates', static_folder='static', url_prefix='/records')

default_breadcrumb_root(records_api, '.')



def get_record(id):
    record = Record.query.get(id)

    if record is None:
        abort(404)
    return record

def get_record_data(id):
    record_data = RecordData.query.filter(RecordData.record_id == id).all()
    if record_data is None:
        abort(404)
    return record_data


def get_payload(id):
    payload = Payload.query.get(id)

    if payload is None:
        return None
    return payload

def get_decoder_payload(id):
    decoder_payload = Decoder.query.filter(Decoder.device_id == id).first()

    if decoder_payload is None:
        return None
    return decoder_payload


@records_api.route('/')
@register_breadcrumb(records_api, '.records_view', 'Last 1000 records')
@login_required
def records_view():
    #records = Record.query.order_by(Record.created.desc()).limit(1000).all()
    payloads = Payload.query.order_by(Payload.created.desc()).limit(1000).all()
    return render_template('records.html', payloads=payloads)


@records_api.route('/get')
@login_required
def records_get():
    payloads: list['Payload'] = Payload.query.order_by(Payload.created.desc()).limit(1000).all()
    response: list[dict] = list()
    for i in range(len(payloads)):
        response.append(payloads[i].get_dict())
    return {'data': response}


@records_api.route('/all')
@login_required
def records_all():
    records = Record.query.all()
    return render_template('records.html', records=records)


def paylaod_decode(decoder_format, payload):

    try:
        temp = json.loads(payload)

        js = decoder_format

        decoder = js2py.eval_js(js)
        return decoder(temp)
    except Exception:
        return "error"
    except:
        return "error"


@records_api.route('/devices/<int:device_id>/last_payload')
def get_last_data(device_id):
    payload = Payload.query.filter(Payload.device_id == device_id).order_by(Payload.created.desc()).first()
    payload = payload.toDict()

    return jsonify(payload)

@records_api.route('/add', methods=('POST',))
def post_add():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()

            device = Device.query.filter(Device.key == data['key']).first()
            data = json.dumps(data['payload'], sort_keys=True)
          #  decoder_format = get_decoder_payload(device.id)



           # if decoder_format is not None:
            #    decoded = (paylaod_decode(decoder_format.value, data))
            #    if decoded != "error":

            new_record = Payload(device_id=device.id, value=data)
            db.session.add(new_record)
            db.session.commit()
            db.session.flush()  # updates the objects of the session
            return "ok"


@records_api.route('/create', methods=('GET', 'POST'))
@login_required
def record_create():
    if request.method == 'POST':
        device_id = request.form['device_id']
        new_record = Record(device_id)
        if not device_id:
            flash('Title is required!')
        else:
            db.session.add(new_record)
            db.session.commit()
            return redirect(url_for('records_api.records_view'))
    return render_template('record_create.html')


@records_api.route('/<int:id>')
@register_breadcrumb(records_api, '.records_view.record_view', 'Record')
@login_required
def record_view(id):
    #record = get_record(id)

    payload = get_payload(id)
    decoder_format = get_decoder_payload(payload.device.id)

    if decoder_format is not None:
        decoded = (paylaod_decode(decoder_format.value, payload.value))
    else:
        decoded = ""

    #record_data_all = get_record_data(id)
    return render_template('record.html', payload=payload, decoded=str(decoded), decoder_format=decoder_format)


@records_api.route('/<int:id>/edit', methods=('GET', 'POST'))
@login_required
def record_edit(id):
    payload = get_payload(id)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            payload.title = title
            payload.content = content
            db.session.commit()

            return redirect(url_for('records_api.records_view'))

    return render_template('record_edit.html', payload=payload)


@records_api.route('/<int:id>/delete', methods=('POST',))
@login_required
def record_delete(id):
    payload = get_payload(id)
    db.session.delete(payload)
    db.session.commit()
    return redirect(url_for('records_api.records_view'))
