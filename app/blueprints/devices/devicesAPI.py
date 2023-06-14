import json
import secrets

import jsonschema
import pytz
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_breadcrumbs import register_breadcrumb, default_breadcrumb_root
from flask_login import current_user, login_required
from genson import SchemaBuilder
from jsonschema import validate
from werkzeug.exceptions import abort

from app.models import (Building, Decoder, Device, DeviceFloor, DeviceFlow,
                        DeviceParam, DeviceSchema, Sensor, Task, db)
from app.timeAPI import get_time

devices_api = Blueprint('devices_api', __name__, template_folder='templates')

default_breadcrumb_root(devices_api, '.')

def get_device(id):
    device = Device.query.get(id)
    if device is None:
        abort(404)
    return device

def get_sensor(id):
    sensor = Sensor.query.get(id)
    if sensor is None:
        return None
    return sensor

def get_buildings():
    buildings = Building.query.all()
    if buildings is None:
        return None
    return buildings

def get_task(id):
    task = Task.query.get(id)
    if task is None:
        abort(404)
    return task


def get_device_flows(id):
    device_flows = DeviceFlow.query.filter(DeviceFlow.device_id == id).all()
    if device_flows is None:
        abort(404)
    return device_flows



def get_device_schema(id):
    device_schema = DeviceSchema.query.filter(DeviceSchema.device_id == id).first()
    #device_schema = "s"
    if device_schema is None:
        return None
    return device_schema

def get_device_params(id):
    device_params = DeviceParam.query.filter(DeviceParam.device_id == id).all()
    if device_params is None:
        abort(404)
    return device_params


@devices_api.route('/devices')
@register_breadcrumb(devices_api, '.devices_view', 'Devices')
@login_required
def devices_view():
    namepage="Список устройств"
    devices = Device.query.filter(Device.user_id == current_user.id).all()
    return render_template('devices.html', devices=devices, namepage=namepage)


@devices_api.route('/devices/create', methods=('GET', 'POST'))
@register_breadcrumb(devices_api, '.devices_view.device_create', 'Create device')
@login_required
def device_create():
    if request.method == 'POST':
        name = request.form['name']

        if not name:
            flash('Title is required!')
        else:
            key = secrets.token_urlsafe(10)
            user_id = current_user.id
            new_device = Device(user_id, name, key)
            db.session.add(new_device)
            db.session.commit()
            return redirect(url_for('devices_api.devices_view'))
    return render_template('device_create.html')


def view_device_dlc(*args, **kwargs):
    device_id = request.view_args['id']
    device = Device.query.get(device_id)
    return [{'text': device.name, 'url': f'/devices/{device.id}'}]


def view_device_edit_dlc(*args, **kwargs):
    device_id = request.view_args['id']
    device = Device.query.get(device_id)
    return [{'text': 'Edit device: ' + device.name, 
            'url': f'/devices/{device.id}/edit'}]


def view_sensor_dlc(*args, **kwargs):
    sensor_id = request.view_args['id']
    sensor = Sensor.query.get(sensor_id)
    device = '/devices/'+str(sensor.device.id) +'/edit'
    # return [ {'text': 'adsadas', 'url': device}, {'text': sensor.name + 'asdadsad', 'url': f'devices/sensors/{sensor_id}'}]
    return [{'text': 'Edit ' + sensor.device.name, 'url': device}, {'text': sensor.name, 'url': f'/devices/sensors/{sensor_id}'}]


def view_sensor_add_dlc():
    device_id = str(request.view_args['id'])
    device =  Device.query.get(device_id)
    device_url = '/devices/' + device_id + '/edit'
    return [{'text': 'Edit ' + device.name, 'url': device_url}, {'text': 'Add sensor', 'url': f'/devices/{device_id}/add_sensor'}]

@devices_api.route('/devices/<int:id>')
@register_breadcrumb(devices_api, '.devices_view.device_view', '',
                                 dynamic_list_constructor=view_device_dlc)
@login_required
def device_view(id):
    device = get_device(id)
    flows = get_device_flows(id)
    params = get_device_params(id)


    floor = None
    if device.floor is not None:
        floor = device.floor

    if(device.user_id == current_user.id):
        namepage = "Устройство: " + device.name
        return render_template('device.html', device=device, namepage=namepage, flows=flows, params=params, floor=floor)
    else:
        return redirect(url_for('devices_api.devices_view'))


@devices_api.route('/devicesn/<int:id>')
# @register_breadcrumb(devices_api, '.devices', '',
#                                  dynamic_list_constructor=view_device_dlc)
@login_required
def device_view_new(id):
    device = get_device(id)
    flows = get_device_flows(id)
    params = get_device_params(id)
    decoder = get_device_decoder(id)

    buildings = get_buildings()

    if decoder is None:
        decoder = "function decoder(input) {return data:input;}"
    else:
        decoder = decoder.value

    if (device.user_id == current_user.id):
        if request.method == 'POST':
            name = request.form['name']
            key = request.form['key']

            if not name:
                flash('Title is required!')
            else:
                device.name = name
                device.key = key
                db.session.commit()

                return redirect(url_for('devices_api.devices_view'))
        namepage = "Редактирование: " + device.name

        floor = None
        if device.floor is not None:
            floor = device.floor

        return render_template('devices/device_new.html', device=device, namepage=namepage, flows=flows, params=params,
                               decoder=decoder, floor=floor, buildings=buildings)
    else:
        return redirect(url_for('devices_api.devices_view'))


@devices_api.route('/devices/<int:id>/addparam', methods=('POST',))
@login_required
def device_param_add(id):
    if request.method == 'POST':
        device_id = id
        name = request.form['name']
        val = ""
        new_param = DeviceParam(name, val, device_id)
        if not device_id:
            flash('Title is required!')
        else:
            db.session.add(new_param)
            db.session.commit()
            return redirect( url_for('devices_api.device_edit', id=device_id))
    #return render_template('records/record_create.html')


@devices_api.route('/devices/<int:id>/rmparam/<int:paramid>', methods=('POST', 'GET'))
@login_required
def device_param_remove(id, paramid):
    if request.method == 'GET':
        param_data = DeviceParam.query.filter(DeviceParam.id == paramid).first()
        db.session.delete(param_data)
        db.session.commit()

        return redirect( url_for('devices_api.device_edit', id=id))


@devices_api.route('/devices/<int:id>/addflow', methods=('POST',))
@login_required
def device_flow_add(id):
    if request.method == 'POST':
        device_id = id
        name = request.form['name']
        new_flow = DeviceFlow(name, device_id)
        if not device_id:
            flash('Title is required!')
        else:
            db.session.add(new_flow)
            db.session.commit()
            return redirect( url_for('devices_api.device_edit', id=device_id))


@devices_api.route('/devices/<int:id>/add_sensor', methods=('POST', 'GET'))
@register_breadcrumb(devices_api, '.devices_view.device_sensor_add', '',
                                 dynamic_list_constructor=view_sensor_add_dlc)
@login_required
def device_sensor_add(id):
    if request.method == 'POST':
        device_id = id
        name = request.form['name']
        new_sensor = Sensor(device_id, name)
        if not device_id:
            flash('Title is required!')
        else:
            db.session.add(new_sensor)
            db.session.commit()

            return redirect(url_for('devices_api.device_sensor_edit', id=new_sensor.id))

    return render_template('sensor_edit.html')

@devices_api.route('/devices/sensors/<int:id>/remove', methods=('POST', 'GET'))
@login_required
def device_sensor_remove(id):
    sensor = get_sensor(id)
    device_id = sensor.device_id
    db.session.delete(sensor)
    db.session.commit()
    return redirect(url_for('devices_api.device_edit', id=device_id))


@devices_api.route('/devices/sensors/<int:id>', methods=('POST', 'GET'))
@register_breadcrumb(devices_api, '.devices_view.device_sensor_edit',  '', dynamic_list_constructor=view_sensor_dlc)
@login_required
def device_sensor_edit(id):
    sensor = get_sensor(id)
    namepage = "Редактирование: " + sensor.name

    if request.method == 'POST':
        name = request.form['name']
        decode_key = request.form['decode_key']
        description = request.form['description']

        #type_id = db.Column(db.Integer, db.ForeignKey('sensor_types.id'))
        #unit_id = db.Column(db.Integer, db.ForeignKey('type_units.id'))
        #prefix_id = db.Column(db.Integer, db.ForeignKey('prefixes.id'))
        #color_ranges = db.relationship('SensorColorRange', backref='sensor')
        #precision = db.Column(db.String(255))
        #icon = db.Column(db.String(255))
        #color = db.Column(db.String(255))


        if not name:
            flash('Title is required!')
        else:
            sensor.name = name
            sensor.decode_key = decode_key
            sensor.description = description
            db.session.commit()

            return redirect(url_for('devices_api.device_sensor_edit', id=id))


        return render_template('sensor_edit.html', sensor=sensor, namepage=namepage)
    else:
        return render_template('sensor_edit.html', sensor=sensor, namepage=namepage)


@devices_api.route('/devices/<int:id>/rmflow/<int:flowid>', methods=('POST', 'GET'))
@login_required
def device_flow_remove(id, flowid):
    if request.method == 'GET':
        flow_id = flowid
        flows_data = DeviceFlow.query.filter(DeviceFlow.id == flow_id).first()
        db.session.delete(flows_data)
        db.session.commit()

        return redirect( url_for('devices_api.device_edit', id=id))


@devices_api.route('/devices/<int:id>/setparam', methods=('POST',))
@login_required
def device_param_set(id):
    """if request.is_json:
        data = request.get_json()
        device_id = id
        for i in range(len(data['data'])):
            new_device_param_set = DeviceParamSet(value=data['data'][i]['value'], device_id=device_id,
                                                  device_param_id=data['data'][i]['device_param_id'])
            db.session.add(new_device_param_set)
            db.session.commit()
            """
    if request.method == 'POST':
        #amounts = request.form.getlist('amount')
        items = request.form.getlist('paramval')

        device_id = id
        params = get_device_params(device_id)

        for i in range(len(items)):

            params[i].value = items[i]
            db.session.commit()
            print(items[i])

        return redirect(url_for('devices_api.device_edit', id=device_id))
        """      
        new_param = DeviceParamSet(value, device_id, device_param_id=device_param_id)
        if not device_id:
            flash('Title is required!')
        else:
            db.session.add(new_param)
            db.session.commit()
            return redirect( url_for('device_edit', id=device_id))
            """

def get_device_decoder(id):
    device_decoder = Decoder.query.filter(Decoder.device_id == id).first()

    if device_decoder is None:
        return None
    return device_decoder

@devices_api.route('/devices/<int:id>/edit', methods=('GET', 'POST'))
@register_breadcrumb(devices_api, '.devices_view.device_view.device_edit', '',
                                 dynamic_list_constructor=view_device_edit_dlc)
@login_required
def device_edit(id):
    device = get_device(id)
    flows = get_device_flows(id)
    params = get_device_params(id)
    decoder = get_device_decoder(id)

    buildings = get_buildings()

    if decoder is None:
        decoder = "function decoder(input) {return data:input;}"
    else:
        decoder=decoder.value

    if (device.user_id == current_user.id):
        if request.method == 'POST':
            name = request.form['name']
            key = request.form['key']

            if not name:
                flash('Title is required!')
            else:
                device.name = name
                device.key = key
                db.session.commit()

                return redirect(url_for('devices_api.devices_view'))
        namepage = "Редактирование: " + device.name


        floor = None
        if device.floor is not None:
            floor = device.floor


        return render_template('device_edit.html', device=device, namepage=namepage, flows=flows, params=params,
                               decoder=decoder, floor=floor, buildings=buildings)
    else:
        return redirect(url_for('devices_api.devices_view'))


@devices_api.route('/devices/<int:id>/delete', methods=('POST',))
@login_required
def device_delete(id):
    device = get_device(id)
    db.session.delete(device)
    db.session.commit()
    return redirect(url_for('devices_api.devices_view'))

@devices_api.route('/devices/<int:id>/savedecoder', methods=('POST',))
def decoder_save(id):


    if request.method == 'POST':
        decoder = get_device_decoder(id)
        code = request.form['code']

        if decoder is None:

            newdecoder = Decoder(id, code)
            db.session.add(newdecoder)
            db.session.commit()

        else:
            decoder.value = code
            db.session.commit()

    return redirect(url_for('devices_api.device_edit', id=id))


@devices_api.route('/devices/<int:id>/setfloor', methods=('POST',))
def device_floor_set(id):
    if request.method == 'POST':

        floor_id = request.form['floor_id']
        lng = request.form['lng']
        lat = request.form['lat']

        if lng == "":
            lng = 0

        if lat == "":
            lat = 0

        floors = DeviceFloor.query.filter(DeviceFloor.device_id == id).all()
        for floor in floors:
            db.session.delete(floor)
            db.session.commit()

        if floor_id is not None:

            device_floor = DeviceFloor(id, floor_id, lng, lat)
            db.session.add(device_floor)
            db.session.commit()



    return redirect(url_for('devices_api.device_edit', id=id))


@devices_api.route('/getschema', methods=('POST',))
def new():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()

            builder = SchemaBuilder()
            builder.add_object(data['payload'])
            out = builder.to_json(indent=2)
            out = json.dumps(out)
            schema = get_device_schema(1)
            if schema is None:
                new_schema = DeviceSchema(out, 1)
                db.session.add(new_schema)
                db.session.commit()
            else:
                schema.schema = out
                db.session.commit()
            #out = json.loads(out)

            return out


@devices_api.route("/check")
def accountList():
    return "list of accounts"