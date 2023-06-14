import datetime
from queue import Queue

from flask import url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


from dataclasses import dataclass, field, InitVar
from typing import Union

db:SQLAlchemy = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    timezone = db.Column(db.String(120))
    password_hash = db.Column(db.String(128))
    created = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)
    updated = db.Column(db.DateTime(), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    devices = db.relationship('Device', backref='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __init__(self, username, email):
        self.username = username
        self.email = email

    def __repr__(self):
        return '<User %r>' % self.username


class Decoder(db.Model):
    __tablename__ = 'decoders'

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'))
    value = db.Column(db.Text)
    created = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)
    updated = db.Column(db.DateTime(), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __init__(self, device_id, value):
        self.device_id = device_id
        self.value = value

    def __repr__(self):
        return '<Device %r>' % self.value




@dataclass
class Device(db.Model):
    __tablename__ = 'devices'

    id: int
    name: str
    key: str
    user_id: int
    created: datetime.timedelta
    updated: datetime.timedelta

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    key = db.Column(db.String(255), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)
    updated = db.Column(db.DateTime(), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    records = db.relationship('Record', backref='device')
    payload = db.relationship('Payload', backref='device')
    floor = db.relationship('DeviceFloor', backref='device', uselist=False)
    sensors = db.relationship('Sensor', backref='device')
    dev_dir = db.relationship('Dev_dir', backref='device', uselist=True)

    object_relation: db.relationship = db.relationship(
                                'ObjectDevice',
                                back_populates='device',
                                foreign_keys='[ObjectDevice.device_id]',
                                uselist=False,
                                cascade="all, delete")

    def __init__(self, user_id, name, key):
        self.user_id = user_id
        self.name = name
        self.key = key

    def __repr__(self):
        return '<Device %r>' % self.name


class DeviceFloor(db.Model):
    __tablename__ = 'floor_devices'

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'))
    floor_id = db.Column(db.Integer, db.ForeignKey('floors.id'))
    lng = db.Column(db.String(80))
    lat = db.Column(db.String(80))
    created = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)
    updated = db.Column(db.DateTime(), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __init__(self, device_id, floor_id, lng, lat):
        self.device_id = device_id
        self.floor_id = floor_id
        self.lng = lng
        self.lat = lat

    def __repr__(self):
        return '<Device %r>' % self.floor_id


class Floor(db.Model):
    __tablename__ = 'floors'

    id = db.Column(db.Integer, primary_key=True)
    building_id = db.Column(db.Integer, db.ForeignKey('buildings.id'))
    name = db.Column(db.String(80))
    description = db.Column(db.String(80))
    image = db.Column(db.String(80))
    width = db.Column(db.Float)
    height = db.Column(db.Float)
    created = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)
    updated = db.Column(db.DateTime(), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    devices = db.relationship('DeviceFloor', backref='floor')

    def __init__(self, building_id, name):
        self.building_id = building_id
        self.name = name


    def __repr__(self):
        return '<Device %r>' % self.name


class Building(db.Model):
    __tablename__ = 'buildings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(80))
    description = db.Column(db.String(80))
    address = db.Column(db.String(80))
    lng = db.Column(db.String(80))
    lat = db.Column(db.String(80))
    icon = db.Column(db.String(80))
    created = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)
    updated = db.Column(db.DateTime(), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    floors = db.relationship('Floor', backref='building')

    def __init__(self, user_id, name):
        self.user_id = user_id
        self.name = name


    def __repr__(self):
        return '<Device %r>' % self.name


class DeviceParamSet(db.Model):
    __tablename__ = 'device_param_set'

    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(100))
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'))
    device_param_id = db.Column(db.Integer, db.ForeignKey('device_params.id'))
    created = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)
    updated = db.Column(db.DateTime(), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __init__(self, value, device_id, device_param_id):
        self.value = value
        self.device_id = device_id
        self.device_param_id = device_param_id

    def __repr__(self):
        return '<Device %r>' % self.value


class DeviceSchema(db.Model):
    __tablename__ = 'device_schema'

    id = db.Column(db.Integer, primary_key=True)
    schema = db.Column(db.String(1000))
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'))
    created = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)
    updated = db.Column(db.DateTime(), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __init__(self, schema, device_id):
        self.device_id = device_id
        self.schema = schema

    def __repr__(self):
        return '<Device %r>' % self.schema


class DeviceFlow(db.Model):
    __tablename__ = 'device_flows'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'))
    created = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)
    updated = db.Column(db.DateTime(), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __init__(self, name, device_id):
        self.device_id = device_id
        self.name = name

    def __repr__(self):
        return '<Device %r>' % self.name


class DeviceParam(db.Model):
    __tablename__ = 'device_params'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    value = db.Column(db.String(100))
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'))
    created = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)
    updated = db.Column(db.DateTime(), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __init__(self, name, value, device_id):
        self.name = name
        self.value = value
        self.device_id = device_id

    def __repr__(self):
        return '<Device %r>' % self.name


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    # user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)
    updated = db.Column(db.DateTime(), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)

    def __init__(self, title, content):
        self.title = title
        self.content = content

    def __repr__(self):
        return "Post(%r, %r)" % (self.title, self.content)


class RecordData(db.Model):
    __tablename__ = 'record_data'
    id = db.Column(db.Integer, primary_key=True)
    record_id = db.Column(db.Integer, db.ForeignKey('records.id'))
    name = db.Column(db.String(255))
    value = db.Column(db.Text)
    created = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)
    updated = db.Column(db.DateTime(), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __init__(self, record_id, name, value):
        self.record_id = record_id
        self.name = name
        self.value = value

    def __repr__(self):
        return "Post(%r, %r)" % (self.name, self.value)


class PayloadLimit(db.Model):
    __tablename__ = 'payload_limits'
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'))
    value = db.Column(db.Integer)
    created = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)
    updated = db.Column(db.DateTime(), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __init__(self, device_id):
        self.device_id = device_id,

    def __repr__(self):
        return "Post(%r, %r)" % self.created


class Payload(db.Model):
    __tablename__ = 'payloads'
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'))
    value = db.Column(db.Text)
    created = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)
    updated = db.Column(db.DateTime(), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __init__(self, device_id, value):
        self.device_id = device_id,
        self.value = value

    def __repr__(self):
        return "Payload(%r, %r)" % (self.device_id, self.created)

    def get_dict(self) -> dict:
        '''Return dict ID, created, dev_id for displaying in /records'''
        return {
            'id': self.id,
            'created': self.created,
            'device_name':self.device.name,
            'config': [f'/records/{self.id}']
        }

    def toDict(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}


class Record(db.Model):
    __tablename__ = 'records'
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'))
    created = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)
    updated = db.Column(db.DateTime(), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            'created': self.created,
            'device': self.device.name
        }

    def __init__(self, device_id):
        self.device_id = device_id

    def __repr__(self):
        return "Post(%r, %r)" % self.created


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'))
    url = db.Column(db.String(255))
    created = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)
    updated = db.Column(db.DateTime(), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __init__(self, user_id, device_id, url):
        self.user_id = user_id,
        self.device_id = device_id,
        self.url = url,

    def __repr__(self):
        return "Post(%r, %r)" % self.created


class Sensor(db.Model):
    __tablename__ = 'sensors'

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'))
    name = db.Column(db.String(255))
    decode_key = db.Column(db.String(255))
    description = db.Column(db.String(255))

    type_id = db.Column(db.Integer, db.ForeignKey('sensor_types.id'))
    unit_id = db.Column(db.Integer, db.ForeignKey('type_units.id'))
    prefix_id = db.Column(db.Integer, db.ForeignKey('prefixes.id'))
    color_ranges = db.relationship('SensorColorRange', backref='sensor')
    precision = db.Column(db.String(255))
    icon = db.Column(db.String(255))
    color = db.Column(db.String(255))
    created = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)
    updated = db.Column(db.DateTime(), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __init__(self, device_id, name):
        self.device_id = device_id,
        self.name = name,

    def __repr__(self):
        return "Post(%r, %r)" % self.created


class SensorColorRange(db.Model):
    __tablename__ = 'sensor_color_ranges'

    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey('sensors.id'))
    min = db.Column(db.String(255))
    max = db.Column(db.String(255))
    color = db.Column(db.String(255))

    created = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)
    updated = db.Column(db.DateTime(), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __init__(self, sensor_id, min, max, color):
        self.sensor_id = sensor_id,
        self.min = min,
        self.max = max,
        self.color = color

        def __repr__(self):
            return "Post(%r, %r)" % self.created


class SensorType(db.Model):
    __tablename__ = 'sensor_types'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    units = db.relationship('TypeUnit', backref='sensor_type')
    created = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)
    updated = db.Column(db.DateTime(), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __init__(self, name):
        self.name = name

        def __repr__(self):
            return "Post(%r, %r)" % self.created


class TypeUnit(db.Model):
    __tablename__ = 'type_units'

    id = db.Column(db.Integer, primary_key=True)
    sensor_type_id = db.Column(db.Integer, db.ForeignKey('sensor_types.id'))
    name = db.Column(db.String(255))
    value = db.Column(db.String(255))

    created = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)
    updated = db.Column(db.DateTime(), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __init__(self, sensor_type_id, name, value):
        self.sensor_type_id = sensor_type_id,
        self.name = name,
        self.value = value

    def __repr__(self):
        return "Post(%r, %r)" % self.created


class Prefix(db.Model):

    __tablename__ = 'prefixes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    value = db.Column(db.String(255))

    created = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)
    updated = db.Column(db.DateTime(), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __init__(self, name, value):
        self.name = name,
        self.value = value

    def __repr__(self):
        return "Post(%r, %r)" % self.created


class ObjectRelation(db.Model):
    __tablename__ = 'object_relations'

    id = db.Column(db.Integer, primary_key=True)

    child_id = db.Column(db.Integer, db.ForeignKey('objects.id'), nullable=False)
    object_parent_id = db.Column(db.Integer, db.ForeignKey('objects.id'), nullable=False)

    child_object = db.relationship('Object', 
                                    back_populates='child_in_relation',
                                    foreign_keys=[child_id], 
                                    uselist=False)
    parent_object = db.relationship('Object', 
                                    back_populates='parent_in_relations',
                                    foreign_keys=[object_parent_id], 
                                    uselist=False)
    

    def __repr__(self):
        return f'''\nObjectRelation(
        \t id={self.id},
        \t child_id={self.child_id},
        \t par_id={self.parent_object.id}'''


@dataclass
class Object(db.Model):
    __tablename__ = 'objects'

    id: int
    name: str
    description: str
    object_type_id: int
    created: datetime.datetime
    updated: datetime.datetime


    id = db.Column(db.Integer, primary_key=True)    
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(150), nullable=True)
    object_type_id = db.Column(db.Integer, db.ForeignKey('objects_types.id'))
    created = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)
    updated = db.Column(db.DateTime(), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    child_in_relation = db.relationship('ObjectRelation', 
                                    back_populates='child_object',
                                    foreign_keys=[ObjectRelation.child_id], 
                                    uselist=True)
    parent_in_relations = db.relationship(
                                    'ObjectRelation', 
                                    back_populates='parent_object', 
                                    foreign_keys=[ObjectRelation.object_parent_id], 
                                    uselist=True)
    object_type = db.relationship('ObjectType',
                                    back_populates='objects',
                                    foreign_keys=[object_type_id],
                                    uselist=False)
    attributes_values = db.relationship(
                                    'AttributeValue',
                                    back_populates='object_',
                                    foreign_keys='[AttributeValue.object_id]',
                                    uselist=True,
                                    cascade="all, delete")
    devices_relations: db.relationship = db.relationship(
                                'ObjectDevice',
                                back_populates='obj',
                                foreign_keys='[ObjectDevice.object_id]',
                                uselist=True,
                                cascade="all, delete")

    def get_object_type_name(self) -> str:
        if not self.object_type == None:
            return self.object_type.type_name 
        else:
            return 'Have not type'

    def get_attributes_values_to_hierarchy(self):
        attributes_value: list[dict[str, str]] = []
        if len(self.attributes_values) == 0:
            if self.object_type == None:
                attributes_value.append({'Type not selected': 'have not attributes'})
            else:
                attributes = self.get_attributes()
                for atr in attributes:
                    attributes_value.append({atr: 'have not value'})
        else:
            for atr_val in self.attributes_values:
                attributes_value.append({atr_val.attribute.attribute_name: atr_val.value})

            attributes: list[str] = self.get_attributes()
            keys: list[str] = list()
            for e in attributes_value:
                keys.append(*e)     
            for atr in attributes:
                if atr not in keys:
                    attributes_value.append({atr: ''})

        return attributes_value

    @classmethod
    def get_child_objects_by_names(cls, names: list[str]) -> list['Object']:
        child_objects: list['Object'] = []
        for child_name in names:
           child: 'Object' = db.session.query(cls).where(cls.name == child_name).first()
           if child != None:
            child_objects.append(child)
        return child_objects

    # все объекты-родители первого уровня, от них через 
    # parent_in_relations спускаемся до последних потомков
    @classmethod
    def get_top_level_objects(cls) -> list['Object']:
        objects = db.session.query(Object).all()
        top_level_object: list[Object] = []
        for obj in objects:
            if obj.child_in_relation == []:
                top_level_object.append(obj)
        return top_level_object

    @staticmethod
    def get_childs(parent_node: 'Object') -> list['Object']:
        childs: list['Object'] = []
        for parent_in_rels in parent_node.parent_in_relations:
            childs.append(parent_in_rels.child_object)
        return childs

    def get_devices_to_hierarchy(self: 'Object'):
        devices: list['ObjectDevice'] = list()

        if self.devices_relations == []:
            devices.append({'device_name': 'Have not devices', 'id': '' })
        else:
            for obj_device_rel in self.devices_relations:
                if (obj_device_rel.device == None): continue
                devices.append({'device_name': obj_device_rel.device.name, 'id': obj_device_rel.device.id })
        
        return devices

    @classmethod
    def get_hierarchy_dict(cls, current_node: 'Object', prev_node: 'Object', hierarchy_dict: dict) -> Union[dict, None]:
        obj_id: int = current_node.id
        obj_type: str = current_node.get_object_type_name()
        obj_name: str = current_node.name
        obj_attributes_value: list[dict] = current_node.get_attributes_values_to_hierarchy()
        obj_devices: list['ObjectDevice'] = current_node.get_devices_to_hierarchy()
        relation_id: str = '#' if prev_node == None else db.session.query(ObjectRelation)\
            .where(ObjectRelation.child_id == current_node.id and ObjectRelation.device_id == prev_node.id).first().id  
        
        hierarchy_dict[obj_name] = {
                                    'object_type': obj_type,
                                    'name': obj_name,
                                    'attributes': obj_attributes_value, 
                                    'id': obj_id,
                                    'devices': obj_devices,
                                    'relation_id': relation_id
                                    }
        childs: list['Object'] = cls.get_childs(current_node)
        if childs == []:
            return hierarchy_dict
        else:
            hierarchy_dict[f'{current_node.name}']['childs'] =  {}
            for child in childs:
                cls.get_hierarchy_dict(child, current_node, hierarchy_dict[f'{current_node.name}']['childs'])
        return hierarchy_dict
        

    def get_childs_name(self) -> list[str]:
        child_names: list[str] = []
        for relation in self.parent_in_relations:
           child_names.append(relation.child_object.name)
        return child_names


    def get_attributes(self) -> list[str]:
        atrs: list[str] = []
        if self.object_type != None:
            for atr_type_rel in self.object_type.attribute_type:
                atrs.append(atr_type_rel.attribute.attribute_name)
        return atrs


    def get_attributes_values(self) -> list[dict[str, str]]:
        atrs_values: list[dict[str, str]] = []
        if self.attributes_values != []:
            for atr_type_rel in self.attributes_values:
                atrs_values.append({'atr_name': atr_type_rel.attribute.attribute_name, 'value': atr_type_rel.value})
            for attribute in self.object_type.attribute_type:
                exsists_with_values = list(x['atr_name'] for x in atrs_values)
                if attribute.attribute.attribute_name not in exsists_with_values:
                    atrs_values.append({'atr_name': attribute.attribute.attribute_name, 'value': ''})
        else:
            if self.object_type is not None:
                for atr_type_rel in self.object_type.attribute_type:
                    atrs_values.append({'atr_name': atr_type_rel.attribute.attribute_name, 'value': ''})

        return atrs_values

    def get_devices(self):
        devices: Union(list[dict], str) = []

        if self.devices_relations == []:
            devices = 'Have not devices'
        else:
            for dev_rel in self.devices_relations:
                if dev_rel.device == None : continue
                devices.append({'device_name': dev_rel.device.name, 'device_id': dev_rel.device.id, 'device_url': f'http://metadb.ru/devices/{dev_rel.device.id}'})

        return devices 

    @staticmethod
    def get_object_by_name(name: str) -> 'Object':
        o: Object = db.session.query(Object).where(Object.name == name).first()
        return o
    
    @staticmethod
    def get_rel_by_id(parent: str, child:str) -> 'ObjectRelation':
        rel: ObjectRelation = db.session.query(ObjectRelation)\
            .where(ObjectRelation.object_parent_id == parent and ObjectRelation.child_id == child).first()
        return rel

    @classmethod
    def get_all_childs(cls, obj, child_list):
        for rel in obj.parent_in_relations:
            if rel.child_object.parent_in_relations != []:
                child_list.append(rel.child_object)
                cls.get_all_childs(rel.child_object, child_list)
            else:
                child_list.append(rel.child_object)
        return child_list


    @classmethod
    def get_all_childs_names(cls, obj: 'Object', child_list: list[str]) -> list[str]:
        for rel in obj.parent_in_relations:
            child_list.append(rel.child_object.name)
            if rel.child_object.parent_in_relations != []:
                cls.get_all_childs_names(rel.child_object, child_list)
        return child_list


    @classmethod
    def get_all_parent_names(cls, obj: 'Object', parent_list: list[str]) -> list[str]:
        rel: 'ObjectRelation' = None
        for rel in obj.child_in_relation:
            parent_list.append(rel.parent_object.name)
            if rel.parent_object.parent_in_relations != []:
                cls.get_all_parent_names(rel.parent_object, parent_list)
        return parent_list
    
    @classmethod
    def get_all_object_names(cls) -> list[str]:
        objects: list['Object'] = db.session.query(Object).all() 
        objects_names: list[str] = list(x.name for x in objects)
        return objects_names
    
   
    def get_root_parents(self) -> list[str]:
        root_parents: list[str] = list()
        q: Queue['Object'] = Queue()
        q.put(self)
        while(not q.empty()):
            node: 'Object' = q.get()
            if node.child_in_relation == []:
                root_parents.append(node.name)
            else:
                ch_rel: 'ObjectRelation'
                for ch_rel in node.child_in_relation:
                    q.put(ch_rel.parent_object)
        return root_parents


    def get_json(self):
        obj_json: dict = dict()
        obj_json['children_all_levels'] = [x.name for x in Object.get_all_childs(self, list())]
        obj_json['parents'] = [x.parent_object.name for x in self.child_in_relation]
        obj_json['created'] = self.created
        obj_json['updated'] = self.updated
        obj_json['description'] = self.description if self.description != None else ''
        obj_json['id'] = int(self.id)
        obj_json['name'] = self.name
        obj_json['type'] = self.get_object_type_name()
        obj_json['attributes_values'] = self.get_attributes_values()
        obj_json['devices'] = self.get_devices()

        return obj_json

        
    def __repr__(self):
        parent_in_relations: str = ''
        child_in_relation: list[str] = [] 

        if self.parent_in_relations != None:
            parent_in_relations =  ', '.join(str(rel.id) for rel in self.parent_in_relations)

        if self.child_in_relation == []:
            child_in_relation.append('not child')
        else:
            for ch_rel in self.child_in_relation:
                child_in_relation.append(ch_rel.id)

        return f'''\n
        Object (
        id={self.id},
        name={self.name},
        descr={ self.description},
        child_in_relation={child_in_relation},
        parent_in_relation={parent_in_relations},
        object_type={self.object_type_id})\n'''


# связывает атрибуты с типами, нужна для разрешения многие-ко-многим
@dataclass
class AttributeType(db.Model):
    __tablename__ = 'attributes_types'

    id: int
    object_type_id: int
    attribute_id: int
    object_type: 'ObjectType'
    attribute: 'Attribute'

    id = db.Column(db.Integer, primary_key=True)
    object_type_id = db.Column(db.Integer, db.ForeignKey('objects_types.id'))
    attribute_id = db.Column(db.Integer, db.ForeignKey('attributes.id'))
    created = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)
    updated = db.Column(db.DateTime(), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    object_type = db.relationship('ObjectType',
                                back_populates='attribute_type',
                                foreign_keys=[object_type_id],
                                uselist=False) 
                            
    attribute = db.relationship('Attribute',
                                back_populates='attribute_type',
                                foreign_keys=[attribute_id],
                                uselist=False)
    
    def __repr__(self):
        return f'''\nAttributeType(
        \t id={self.id},
        \t object_type_id={self.object_type_id},
        \t attribute_id={self.attribute_id},
        \t object_type = {self.object_type.type_name},
        \t attribute = {self.attribute.attribute_name}
        )\n'''


@dataclass
class ObjectType(db.Model):
    __tablename__ = 'objects_types'

    id: int
    type_name: str
    created: datetime.datetime
    updated: datetime.datetime
    attributes: Union[list[str], None] = None

    id = db.Column(db.Integer, primary_key=True)
    type_name = db.Column(db.String(150), nullable=False)
    created = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)
    updated = db.Column(db.DateTime(), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


    objects = db.relationship('Object',
                            back_populates='object_type',
                            foreign_keys=[Object.object_type_id],
                            uselist=True)

    # объекты пары атрибут-тип
    attribute_type = db.relationship(
                                'AttributeType',
                                back_populates='object_type',
                                foreign_keys=[AttributeType.object_type_id],
                                uselist=True,
                                cascade="all, delete")                            

    
    def get_attributes(self) -> list[str]:
        attributes: list[str] = []
        for atr_type_rel in self.attribute_type:
            attributes.append(atr_type_rel.attribute.attribute_name)
        return attributes
    
    def get_attributes_set(self) -> set[str]:
        atr_set: set[str] = set()
        for atr_type_rel in self.attribute_type:
            atr_set.add(atr_type_rel.attribute.attribute_name)
        return atr_set

 
    def get_attributes_entity(self) -> list['Attribute']:
        attributes: list['Attribute'] = []
        for atr_type_rel in self.attribute_type:
            attributes.append(atr_type_rel.attribute)
        return attributes

    def delete_type(self):
        for obj in self.objects:
            obj.object_type = None
            obj.attributes_values = []
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        attributes = ', '.join(atr.attribute.attribute_name for atr in self.attribute_type)
        return f'''\nObjectType(
        id={self.id},
        type_name={self.type_name},
        objects=[],
        attributes = {attributes})\n'''

@dataclass
class AttributeValue(db.Model):
    __tablename__ = 'attributes_values'

    id: int 
    value: str
    attribute_id: int
    object_id: int

    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(100), nullable=False)
    attribute_id = db.Column(db.Integer, db.ForeignKey('attributes.id'))
    object_id = db.Column(db.Integer, db.ForeignKey('objects.id'))

    attribute = db.relationship('Attribute',
                                back_populates='values',
                                foreign_keys=[attribute_id],
                                uselist=False)
    object_ = db.relationship('Object',
                            back_populates='attributes_values',
                            foreign_keys=[object_id],
                            uselist=False)
    
    def __repr__(self):
        return f'''\n
        AttributeValue(
        \t id={self.id},
        \t value={self.value},
        \t attribute_id={self.attribute_id},
        \t object_id={self.object_id},
        \t object_name={self.object_.name},
        \t attribute_name={self.attribute.attribute_name}
        )'''


@dataclass
class Attribute(db.Model):
    __tablename__ = 'attributes'

    id: int 
    attribute_name: str
    created: datetime.datetime
    updated: datetime.datetime

    id = db.Column(db.Integer, primary_key=True)
    attribute_name = db.Column(db.String(150), nullable=False, unique=True)
    created = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)
    updated = db.Column(db.DateTime(), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # объекты пары атрибут-тип
    attribute_type = db.relationship('AttributeType',
                                back_populates='attribute',
                                foreign_keys=[AttributeType.attribute_id],
                                uselist=True,
                                cascade="all, delete") 

    # объекты пары атрибут-значение аттрибута с объектом
    values = db.relationship('AttributeValue',
                            back_populates='attribute',
                            foreign_keys=[AttributeValue.attribute_id],
                            uselist=True,
                            cascade="all, delete")

    
    def __repr__(self):
        return f'''\nAttribute( 
        \t id={self.id}, 
        \t name={self.attribute_name}
        )'''
    
    @classmethod
    def get_attibute_by_name(cls, name) -> Union['Attribute', None]:
        finded_atr: Attribute = db.session.query(cls).where(cls.attribute_name == name).first()
        
        return finded_atr

    @classmethod
    def get_attrs_by_name(cls, names: list[str]) -> list['Attribute']:
        attributes: list['Attribute'] = []
        for name in names:
            atr: 'Attribute' = db.session.query(cls).where(cls.attribute_name == name).first()
            if atr not in attributes and not atr is None:
                attributes.append(atr)
        return attributes

    @classmethod
    def get_attrs_by_name_with_values(cls, attrs_with_values: list[dict[str, str]]) -> list[tuple[str, 'Attribute']]:
        atrs_object_with_value: list[tuple[str, 'Attribute']] = []
        for atr in attrs_with_values:
            keys = list(atr.keys())
            atrs_object_with_value.append((
                    atr[keys[0]], 
                    db.session.query(cls).where(cls.attribute_name == keys[0]).first(),
                ))
        return atrs_object_with_value

    @classmethod
    def get_id_name(cls) -> list[dict[int, str]]:
        return db.session.query(cls.id, cls.attribute_name).all()


@dataclass
class ObjectDevice(db.Model):
    __tablename__ = 'object_devices'

    id: int
    device_id: int
    object_id: int


    id: db.Column = db.Column(db.Integer, primary_key=True)
    device_id: db.Column = db.Column(db.Integer, db.ForeignKey('devices.id'))
    object_id: db.Column = db.Column(db.Integer, db.ForeignKey('objects.id'))

    device: db.relationship = db.relationship('Device',
                                back_populates='object_relation',
                                foreign_keys=[device_id],
                                uselist=False,
                                # cascade="all, delete-orphan"
                                )
    obj: db.relationship = db.relationship('Object',
                                back_populates='devices_relations',
                                foreign_keys=[object_id],
                                uselist=False,
                                # cascade="all, delete-orphan"
                                )
    
    def __rerp__(self):
        return f'''\ObjectDevice( 
        \t id={self.id}, 
        \t device_id={self.device_id},
        \t object_id={self.object_id}
        )'''


class Dev_dir(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'))
    directory_id = db.Column(db.Integer, db.ForeignKey('directory.id'))

class Dir_sensor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(50))

    # Дети
    rng = db.relationship('Range', backref = 'dir_sensor', uselist=True)



class Directory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(50))

    # Дети
    dev_dir = db.relationship('Dev_dir', backref = 'directory', uselist=True)
    rng = db.relationship('Range', backref = 'directory', uselist=True)


class Range(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Min = db.Column(db.Float)
    Max = db.Column(db.Float)
    Name = db.Column(db.String(50))
    Directory_Id = db.Column(db.Integer, db.ForeignKey('directory.id'))
    Sensor_Id = db.Column(db.Integer, db.ForeignKey('dir_sensor.id'))

    # Дети
    prob = db.relationship('Problem', backref = 'range', uselist=True)


class Problem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(50))
    Range_Id = db.Column(db.Integer, db.ForeignKey('range.id'))

    # Дети
    adv = db.relationship('Advice', backref='problem', uselist=True)



class Advice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Content = db.Column(db.String(200))
    Problem_Id = db.Column(db.Integer, db.ForeignKey('problem.id'))

