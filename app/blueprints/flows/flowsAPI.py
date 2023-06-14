from flask import Blueprint
import json
from datetime import datetime,timezone
from app.models import Decoder, Payload
from flask import jsonify

from py_mini_racer import py_mini_racer
ctx = py_mini_racer.MiniRacer()


flows_api = Blueprint('flows_api', __name__, template_folder='templates/flows')


def get_decoder_payload(id):
    decoder_payload = Decoder.query.filter(Decoder.device_id == id).first()

    if decoder_payload is None:
        return None
    return decoder_payload


@flows_api.route('/flows/<int:device_id>')
def get_flow(device_id):
    payload = Payload.query.filter(Payload.device_id == device_id).order_by(Payload.created.desc()).first()
    decoder_format = get_decoder_payload(device_id)

    command = decoder_format.value+"""function run(){return decoder("""+payload.value+""")}"""

    ctx.eval(command)

    obj = ctx.call("run")
    try:
        obj["data"]["time"] = datetime.utcfromtimestamp(obj["data"]["time"]).strftime('%d.%m.%Y, %H:%M:%S')

    except:
        obj["data"]["time"] = payload.created

    return (jsonify(obj["data"]))


@flows_api.route('/flows/<int:device_id>/<name>')
def get_flow_val(device_id, name):
    payload = Payload.query.filter(Payload.device_id == device_id).order_by(Payload.created.desc()).first()
    decoder_format = get_decoder_payload(device_id)

    command = decoder_format.value+"""function run(){return decoder("""+payload.value+""")}"""

    ctx.eval(command)

    obj = ctx.call("run")

    data = obj["data"]
    try:
        obj["data"]["time"] = datetime.utcfromtimestamp(obj["data"]["time"]).strftime('%d.%m.%Y, %H:%M:%S')

    except:
        obj["data"]["time"] = payload.created

    return jsonify(data[name])


@flows_api.route('/flows/<int:device_id>/all')
def get_flow_all(device_id):
    payloads = Payload.query.filter(Payload.device_id == device_id).order_by(Payload.created.desc()).all()
    decoder_format = get_decoder_payload(device_id)
    export = []
    for payload in payloads:
        command = decoder_format.value + """function run(){return decoder(""" + payload.value + """)}"""

        ctx.eval(command)

        obj = ctx.call("run")
        try:
            obj["data"]["time"] = datetime.utcfromtimestamp(obj["data"]["time"]).strftime('%d.%m.%Y, %H:%M:%S')

        except:
            obj["data"]["time"] = payload.created

        export.append(obj["data"])

    return jsonify(export)


