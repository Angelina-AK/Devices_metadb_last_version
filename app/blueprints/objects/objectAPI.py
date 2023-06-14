import json
import re
from typing import Union

from flask import (Blueprint, flash, jsonify, redirect, render_template,
                   request, url_for)
from flask_breadcrumbs import (breadcrumb_root_path, current_breadcrumbs,
                               default_breadcrumb_root, register_breadcrumb)
from flask_login import current_user, login_required

from app import Breadcrumbs
from app.models import (Attribute, AttributeType, AttributeValue, Device,
                        Object, ObjectDevice, ObjectRelation, ObjectType, db)

from .breadcrumbs import edit_attribute_dlc

object_api = Blueprint('object_api', __name__,
                        static_folder='static',
                        template_folder='templates', 
                        url_prefix='/objects')

default_breadcrumb_root(object_api, '.')

# +-----------------------------------------------------------
# Объекты                                                     |
# +-----------------------------------------------------------

# relationships creation functions
def create_objects_rel(parent: Object, childs: list[Object]):
    objects_relations = []
    for child in childs:
        print(child)
        obj_rel = ObjectRelation(parent_object=parent, child_object=child)
        objects_relations.append(obj_rel)
    return objects_relations


def create_objects_atr_value_rel(object_: Object, attributes_with_values: list[tuple[str, Attribute]]):
    object_attrs_relations: list[AttributeValue] = []
    for attr in attributes_with_values:
        relation = AttributeValue(value=attr[0], object_=object_, attribute=attr[1])
        object_attrs_relations.append(relation)
    return object_attrs_relations


def possible_childs_set(current_object: Object) -> set[str]:
    root_parents: set[str] = set(current_object.get_root_parents())
    root_parents_obj: list[Object] = [Object.get_object_by_name(x) for x in root_parents]
    objects: set[str] = set(Object.get_all_object_names())

    childs: set[str] = set()

    for rpo in root_parents_obj:
        childs |= set(Object.get_all_childs_names(rpo, []))
    
    possible_childs: set[Object] = objects -  childs - root_parents
    
    return possible_childs

#for breadcrumbs
def view_object_id_dlc():
    object_id: str = request.view_args['id']
    obj: 'Object' = db.session.query(Object).where(Object.id == object_id).first()
    return [{
            'text': f'''Editing object '{obj.name}' ''',
            'url': f'/objects/object_edit/{object_id}'}]


def view_object_info_dlc():
    print('vo')
    object_id: str = request.view_args['id']
    obj: 'Object' = db.session.query(Object).where(Object.id == object_id).first() 
    return [{
            'text': f'"{obj.name}" information',
            'url':f'/objects/object_info/{object_id}'}]

def view_add_device_dlc():
    print('device')
    object_id: str = request.view_args['id']
    obj: 'Object' = db.session.query(Object).where(Object.id == object_id).first() 
    return [{
            'text': f'Adding device to {obj.name}',
            'url':f'/objects/add_device/{object_id}'}]

# routes
@object_api.route('/objects_view', methods=(['GET']))
@register_breadcrumb(object_api, '.objects_view', 'All objects')
@login_required
def objects_view():
    return render_template('objects/objects.html')


@object_api.route('/get_json_all_objects', methods=(['GET']))
@login_required
def get_json_all_objects():
    objs_roots = Object.get_top_level_objects()
    objects_in_hierarchy = {}
    for root in objs_roots:
        objects_in_hierarchy.update(Object.get_hierarchy_dict(root, None, {}))
    return objects_in_hierarchy


@object_api.route('/object_create', methods=('GET', 'POST'))
@register_breadcrumb(object_api, '.objects_view.object_create', 'Create object')
@login_required
def object_create():
    parents: list[str] = Object.get_all_object_names() 
    if request.method == 'POST':

        object_name: str = request.form.get('name')
        object_type: str = request.form.get('type')
        child_names: list[str] = [x for x in request.form.getlist('child-object-name') if x != '']
        parent_name: list[str] = request.form.get('parent-obj')
        
        # получить все инпуты-атрибутов с формы чтобы привязать их к объекту 
        attrs_values: list[dict] = []
        for key in request.form.keys():
            if re.search(r'attr-\w*', key):
                attrs_values.append({key[5:]: request.form[key]})

        if object_name == '':
            return render_template('objects/object_create.html', parents=parents, e='Object name is required')
        
        obj: Object = Object.query.filter(Object.name==object_name).first()
        if obj is not None:
            return render_template('objects/object_create.html', parents=parents, e='Object {object_name} is exists')

        obj = Object(name=object_name)
        db.session.add(obj)

        object_type = db.session.query(ObjectType).where(ObjectType.type_name == object_type).first()
        if not object_type == None:
            obj.object_type=object_type

            if len(attrs_values) != 0:
                attributes = Attribute.get_attrs_by_name_with_values(attrs_values)
                objects_attributes_values_relations = create_objects_atr_value_rel(obj, attributes)
                db.session.add_all(objects_attributes_values_relations)


        # нельзя пересекать вложенные элементы с выбранным родительским
        if parent_name in child_names:
            return render_template('objects/object_create.html', parents=parents, e=f'Object {parent_name} in selected childs')


        parent: Object = Object.get_object_by_name(parent_name)
        # ничего не делать если не нашёлся выбранный родитель
        if parent != None:
            obj_parent_rel: ObjectRelation = ObjectRelation(parent_object=parent, child_object=obj)
            db.session.add(obj_parent_rel)

        
        # в случае добаления вложенных объектов, нужно установить связь объек-объект со всеми детьми(вложенными)
        # либо просто создать объект одиночный
        if len(child_names) != 0:
            child_objects = Object.get_child_objects_by_names(child_names)
            objects_relations = create_objects_rel(obj, child_objects)
            db.session.add_all(objects_relations)

        
        db.session.commit()

        return redirect(url_for('object_api.objects_view'))
    else:
        return render_template('objects/object_create.html', parents=parents)


@object_api.route('/delete_object/<int:id>', methods=(['GET']))
@login_required
def delete_object(id: int):
    object_for_deletion = db.session.query(Object).where(Object.id == id).first()
    print(object_for_deletion.parent_in_relations, object_for_deletion.child_in_relation)

    # если удаляемый элемент не является родителем
    if len(object_for_deletion.parent_in_relations) == 0:
        
        # если у удаляемого элемента есть родители
        if object_for_deletion.child_in_relation != []:
            relations = object_for_deletion.child_in_relation
            for rel in relations:
                db.session.delete(rel)
            # db.session.commit()
        db.session.delete(object_for_deletion)
        db.session.commit()

    # если элемент ялвяется родителем
    else:
        child_relations = object_for_deletion.parent_in_relations


        # ! задуматься об этом

        # если у элемента есть родитель
        if object_for_deletion.child_in_relation != []:
            parents_for_deletion_object: list['Object'] = list()
            for ch_rel in object_for_deletion.child_in_relation:
                parents_for_deletion_object.append(ch_rel.parent_object)
            db.session.delete(ch_rel)
            db.session.commit()  
            
            for rel in child_relations:
                rel.parent_object = parents_for_deletion_object[0]
        else:
            for rel in child_relations:
                db.session.delete(rel)
        
        db.session.delete(object_for_deletion)
        db.session.commit()  
  
    return redirect(url_for('.objects_view'))


@object_api.route('/view_object/<int:id>', methods=(['GET']))
@login_required
def view_object():
    return {}


@object_api.route('/object_edit/<int:id>', methods=(['GET', 'POST']))
@login_required
@register_breadcrumb(object_api, '.objects_view.object_edit', '',
                                 dynamic_list_constructor=view_object_id_dlc)
def object_edit(id):
    obj: Object = db.session.query(Object).where(Object.id == id).first()
    attributes_values: list[AttributeValue] = obj.get_attributes_values()
    childs: set[str] = set(obj.get_childs_name())
    #критерий для родительсткого объекта такой же как и для дочернего
    possible_parents: list[str] = list(possible_childs_set(obj))
    current_parents: list[str] = list(x.parent_object.name for x in obj.child_in_relation)

    if request.method == 'GET':
        return render_template('objects/object_edit.html', 
                                obj=obj, 
                                attributes_values=attributes_values,
                                childs=childs,
                                current_parents=current_parents,
                                possible_parents=possible_parents)
    else:
        
        attrs_values: list[dict[str, str]] = []
        for key in request.form.keys():
            if re.search(r'attr-\w*', key):
                attrs_values.append({key[5:]: request.form[key]})

        form_type: str = request.form['type']
        current_type: ObjectType = obj.object_type

        # Если типы сходятся то обновляем значения аттрибутов
        if current_type != None and form_type == current_type.type_name:
            if len(attrs_values) != 0:
                attributes = Attribute.get_attrs_by_name_with_values(attrs_values)
                for atr_val_old in obj.attributes_values:
                    db.session.delete(atr_val_old)

                objects_attributes_values_relations = create_objects_atr_value_rel(obj, attributes)
                db.session.add_all(objects_attributes_values_relations)
                
        # Назначаем новый тип, новые значения аттрибутов, старые стираем
        else:
            if form_type != '':
                object_type: ObjectType = db.session.query(ObjectType).where(ObjectType.type_name == form_type).first()
                if object_type == None :
                    return render_template('objects/object_edit.html', 
                                            obj=obj, 
                                            attributes_values=attributes_values,
                                            childs=childs,
                                            current_parents=current_parents,
                                            possible_parents=possible_parents,
                                            e=f'Type {form_type} not exists')
                
                obj.object_type = object_type

                db.session.query(AttributeValue).where(AttributeValue.object_id == obj.id).delete()
                
                for atr_val in attrs_values:
                    atr_name: str = list(atr_val.keys())[0]
                    attribute: Attribute = db.session.query(Attribute).where(Attribute.attribute_name == atr_name).first()
                    atr_val_new_rel: AttributeValue = AttributeValue(object_=obj, attribute=attribute, value=atr_val[atr_name])
                    db.session.add(atr_val_new_rel)

        # проверка все ли старые пложенные объекты присутствуют в форме, 
        # если не все - значит пользователь удалил некоторые, надо удалить
        # соответсвующие записи из базы данных
        form_child_names: set[str] = set([x for x in request.form.getlist('current-child')])
        if (form_child_names & childs) != childs:
            del_childs = childs - (form_child_names & childs)
            for dc in del_childs:
                d_child: Object = db.session.query(Object).where(Object.name == dc).first()
                db.session.query(ObjectRelation)\
                    .where(ObjectRelation.child_id == d_child.id and ObjectRelation.object_parent_id == obj.id)\
                        .delete()


        #добавление новых вложенных объектов
        child_names: list[str] = [x for x in request.form.getlist('child-object-name') if x != '']
        
     
        if len(child_names) != 0:
            child_objects: list[Object] = Object.get_child_objects_by_names(child_names)
            child_objects_clear: list[Object] = list()
            for ch in child_objects:
                if ch not in child_objects_clear and not ch.id is obj.id:
                    child_objects_clear.append(ch)


            objects_relations = create_objects_rel(obj, child_objects_clear)
            db.session.add_all(objects_relations)

        #проверка изменись ли родители
        #если старые не прилетели в форме - удалить те, которые не прилетели
        form_parents: set[str] = set(request.form.getlist('parent-obj'))
        parent_for_delation: set[str] = set()
        current_parrent_set: set[str] = set(current_parents)
        parent_for_delation: set[str] = current_parrent_set - form_parents
        for pfd in parent_for_delation:
            pr_o: Object = Object.get_object_by_name(pfd)
            db.session.delete(Object.get_rel_by_id(pr_o.id, obj.id))

        new_parent: set[str] = form_parents - current_parrent_set
        for np in new_parent:
            if np in child_names:
                return render_template('objects/object_edit.html', 
                                            obj=obj, 
                                            attributes_values=attributes_values,
                                            childs=childs,
                                            current_parents=current_parents,
                                            possible_parents=possible_parents,
                                            e=f'{np} in selected childs')
            
            pr_o: Object = Object.get_object_by_name(np)
            if pr_o != None:
                new_perent_obj_rel: ObjectRelation = ObjectRelation(
                                                            parent_object=pr_o,
                                                            child_object=obj)
                db.session.add(new_perent_obj_rel)

        db.session.commit()

        return redirect(url_for('object_api.objects_view'))


@object_api.route('/add_device/<int:id>', methods=(['GET', 'POST']))
@login_required
# @register_breadcrumb(object_api, '.add_device', '', dynamic_list_constructor=view_add_device_dlc)
def add_device(id: int) -> str:
    devices: Device = db.session.query(Device)\
        .where(Device.user_id == current_user.id).all()
    available_devices = list()
    for dev in devices:
        if dev.object_relation == None:
            available_devices.append(dev)
    if request.method == 'GET':
        return render_template('objects/add_device.html', id=id, devices=available_devices)
    else:
        device_name: int = request.form['device']
        object_id: int = id
        device: Device = db.session.query(Device).where(Device.name == device_name).first()

        if device == None:
            return render_template('objects/add_device.html', 
                                    id=id, 
                                    devices=available_devices, 
                                    e=f'Device {device_name} not found')

        obj: Object = db.session.query(Object).where(Object.id == object_id).first()
        obj_device_rel: ObjectDevice = ObjectDevice(device=device, obj=obj)
        
        db.session.add(obj_device_rel)
        db.session.commit()

        return redirect(url_for('object_api.objects_view'))

@object_api.route('/<int:obj_id>/delete_device/<int:dev_id>', methods=(['GET', 'POST']))
@login_required
def delete_device(obj_id: int, dev_id: int):
    rel_for_delation: ObjectDevice = db.session.\
        query(ObjectDevice).where(ObjectDevice.device_id == dev_id and ObjectDevice.object_id == obj_id).first()
    db.session.delete(rel_for_delation)
    db.session.commit()
    return redirect(url_for('object_api.objects_view'))


@object_api.route('/delete_relation/<int:rel_id>', methods=(['GET', 'POST']))
@login_required
def delete_relation(rel_id:int):
    relation: ObjectRelation = db.session.query(ObjectRelation).where(ObjectRelation.id == rel_id).first()
    if not relation:
        return 'relation not found', 400
    db.session.delete(relation)
    db.session.commit()
    return redirect(url_for('object_api.objects_view')), 301


@object_api.route('/get_all', methods=(['GET']))
@login_required
def get_all():
    objects: list[Object] = db.session.query(Object).all()
    for obj in objects:
        obj.devices_relations = []
    response = jsonify(objects)

    return response


@object_api.route('/get_object/<int:id>', methods=(['GET']))
def get_object(id: int):
    obj = db.session.query(Object).where(Object.id == id).first()
    if obj == None:
        return {}
    obj_json: dict = obj.get_json()
    return json.dumps(obj_json, ensure_ascii=False, sort_keys=True, default=str)

@object_api.route('/get_objects', methods=(['GET']))
def get_objects():
    objects = db.session.query(Object).all()
    res = dict()
    for obj in objects:
        res[f'{obj.name}'] = obj.get_json()
    return json.dumps(res, ensure_ascii=False, sort_keys=True, default=str)


@object_api.route('/get_all_possible_childs/<int:id>', methods=(['GET']))
@login_required
def get_all_possible_childs(id) -> str:
    current_object: 'Object' = db.session.query(Object).where(Object.id == id).first()
    possible_childs = possible_childs_set(current_object)
    response = jsonify(list(possible_childs))
    return response


@object_api.route('/object_info/<int:id>', methods=(['GET']))
# @register_breadcrumb(object_api, '.object_info', '', dynamic_list_constructor=view_object_info_dlc)
@login_required
def object_info(id: int):
    object_: Object = db.session.query(Object).where(Object.id == id).first()
    type_: str = object_.get_object_type_name()
    attributes_values: list[dict[str, str]] = object_.get_attributes_values()
    childs: list[str] = object_.get_childs_name()
    
    # девайсы и файлы еще 
    data: dict = {
            'object': object_,
            'type': type_,
            'attributes_val': attributes_values,
            'childs': childs
            }

    return render_template('objects/object_info.html', data=data)



# +-----------------------------------------------------------
# Атрибуты                                                     |
# +-----------------------------------------------------------

@object_api.route('/attributes_view', methods=(['GET']))
@register_breadcrumb(object_api, '.objects_view.attributes_view', 'All attributes')
@login_required
def attributes_view():
    attributes = db.session.query(Attribute).all()
    return render_template('attributes/attributes.html', attributes=attributes)


@object_api.route('/attribute_create', methods=('GET', 'POST'))
@register_breadcrumb(object_api, '.objects_view.attributes_view.attribute_create', 'Create attribute')
@login_required
def attribute_create():
    if request.method == 'POST':
        atr_name = request.form['atr_name']
        if atr_name == '':
                return render_template('attributes/attribute_create.html', e='Attribute name is required')
        

        if db.session.query(Attribute).where(Attribute.attribute_name == atr_name).first():
                return render_template('attributes/attribute_create.html', e='Attribute is exist')

        atr = Attribute(attribute_name=atr_name)
        db.session.add(atr)
        db.session.commit()
        return redirect(url_for('.attributes_view'))
    else:  
        return render_template('attributes/attribute_create.html')

@object_api.route('/attribute_delete/<int:id>', methods=(['DELETE']))
@login_required
def attribute_delete(id: int):
    attribute_for_deletion: Attribute = db.session.query(Attribute).where(Attribute.id == id).first()
    db.session.delete(attribute_for_deletion)
    db.session.commit()
    return {'msg': f'Attribute with id {id} was successfully removed'}, 200


@object_api.route('/attribute_edit/<int:id>', methods=(['GET', 'POST']))
@register_breadcrumb(object_api, '.objects_view.attributes_view.attribute_edit', '', dynamic_list_constructor=edit_attribute_dlc)
@login_required
def attribute_edit(id: int):
    edit_attribute: Attribute = db.session.query(Attribute).where(Attribute.id == id).first()

    if request.method == 'POST':
        form_name: str = request.form.get('atr_name')
        atr: Attribute = Attribute.get_attibute_by_name(form_name)

        if atr:
            return render_template('attributes/attribute_edit.html', atr=edit_attribute, e=f'Attribute {form_name} is exists')

        edit_attribute.attribute_name = form_name
        db.session.commit()
        return redirect(url_for('object_api.attributes_view'))

    return render_template('attributes/attribute_edit.html', atr=edit_attribute)


@object_api.route('/attributes_names', methods=(['GET']))
@login_required
def get_all_attributes():
    keys: list[str] = ['id', 'name']
    attributes: list[dict[int, str]] = list(dict(zip(keys, d)) for d in Attribute.get_id_name())
    return jsonify(attributes)


# +-----------------------------------------------------------
# Типы                                                    |
# +-----------------------------------------------------------

def edit_type_dlc(*args):
    type_id: int = args
    type_id: str = request.view_args['id']
    obj_type: 'ObjectType' = db.session.query(ObjectType).where(ObjectType.id == type_id).first()
    return [{'text': f'''Editing type '{obj_type.type_name}' ''',
             'url': f'/objects/type_edit/{id}'}]


def create_attribute_type_rel(o_type: ObjectType, atrs:list[Attribute]) -> list[AttributeType]:
    type_attribute_relations: list[AttributeType] = list()
    for atr in atrs:
        ty_atr = AttributeType(object_type=o_type, attribute=atr)
        type_attribute_relations.append(ty_atr)

    return type_attribute_relations


def view_all_type_dlc():
    return [{
            'text': 'All object types',
            'url': '/objects/types_view'}]


def type_create_dlc():
    return [{
            'text': 'Create a new type',
            'url': '/objects/type_create'}]


@object_api.route('/types_view', methods=(['GET']))
@register_breadcrumb(object_api, '.objects_view.types_view', '', dynamic_list_constructor=view_all_type_dlc)
@login_required
def types_view():
    objects_types: ObjectType = db.session.query(ObjectType).all()
    print(objects_types)
    return render_template('types/types.html', types=objects_types)


@object_api.route('/type_create', methods=('GET', 'POST'))
@register_breadcrumb(object_api, '.objects_view.types_view.type_create', '', dynamic_list_constructor=type_create_dlc)
@login_required
def type_create():
    if request.method == 'POST':
        type_name = request.form['type_name']
        attributes = request.form.getlist('attribute')
        type_: Union[ObjectType, None] = db.session.query(ObjectType).where(ObjectType.type_name == type_name).first()
        if type_name == '':
            return render_template('types/type_create.html', e='Type name is required')

        if type_ is not None:
            return render_template('types/type_create.html', e=f'''Type '{type_name}' is exists''')


        attrs_object = Attribute.get_attrs_by_name(attributes)
        print(attrs_object)
        
        new_type = ObjectType(type_name=type_name)
        atrs_type_rel = create_attribute_type_rel(new_type, attrs_object)
        #add all objects in session
        db.session.add_all(atrs_type_rel)
        db.session.add(new_type)

        db.session.commit()
        return redirect(url_for('object_api.types_view'))
    else:  
        return render_template('types/type_create.html')


@object_api.route('/type_delete/<int:id>', methods=(['GET']))
@login_required
def type_delete(id: int):
    type_for_delation: ObjectType = db.session.query(ObjectType).where(ObjectType.id == id).first()
    type_for_delation.delete_type()
    return redirect((url_for('object_api.types_view')))


@object_api.route('/type_edit/<int:id>', methods=(['GET', 'POST']))
@register_breadcrumb(object_api, '.objects_view.types_view.type_edit', '', dynamic_list_constructor=edit_type_dlc)
@login_required
def type_edit(id: int):
    type_for_editing: ObjectType = db.session.query(ObjectType).where(ObjectType.id == id).first()
    if request.method == 'GET':
        current_attributes: list[Attribute] = type_for_editing.get_attributes()
        return render_template('types/type_edit.html', type=type_for_editing, attributes=current_attributes)
    else:
        form_name: str = request.form.get('type_name')
        is_exsist_type: ObjectType = db.session.query(ObjectType)\
            .where(ObjectType.type_name == form_name).first()

        if is_exsist_type and not is_exsist_type != type_for_editing.type_name:
            current_attributes: list[Attribute] = type_for_editing.get_attributes_entity()
            return render_template(
                                'types/type_edit.html',
                                type=type_for_editing,
                                attributes=current_attributes,
                                e=f"Type {form_name} is exists")

        if type_for_editing.type_name != form_name:
            type_for_editing.type_name = form_name
            db.session.commit()
        

        current_attributes: set[str] = type_for_editing.get_attributes_set()
        form_attributes: set[str] = set(request.form.getlist('attribute'))

        new_attributes: set[str] = form_attributes - current_attributes
        for_delation_attributes: set[str] = current_attributes - (current_attributes & form_attributes)

        # current - аттрибуты текущего типа, new - новые, 
        # которые нужно нгазначить типу, f_delation - необходимо удалить 
        # удалить из текущего типа,
        for d_atr_name in for_delation_attributes:
            d_atr: Attribute = db.session.query(Attribute).where(Attribute.attribute_name == d_atr_name).first()

            # удаление существующих значений аттрибутов у объектов с редактируемым типом
            d_atr_val: list[AttributeValue] = db.session.query(AttributeValue).\
                where(AttributeValue.attribute_id == d_atr.id and AttributeValue.object_.object_type_id == type_for_editing.id)\
                    .delete()

            # удаление существующих аттрибутов у редактируемого типа
            d_atr_type: AttributeType = db.session.query(AttributeType).\
                where(AttributeType.attribute_id == d_atr.id and AttributeType.object_type_id == type_for_editing.id)\
                    .delete()

            # db.session.delete(d_atr_val, d_atr_type)
            db.session.commit()
        
        arts_type: AttributeType = create_attribute_type_rel(type_for_editing, Attribute.get_attrs_by_name(new_attributes))
        db.session.add_all(arts_type)
        db.session.commit()

        # print(current_attributes, form_attributes, sep='\n')
       
        return redirect((url_for('object_api.types_view')))


@object_api.route('/types', methods=(['GET']))
def get_all_types():
    objects_types = db.session.query(ObjectType).all()
    for obj_type in objects_types:
        obj_type.attributes = obj_type.get_attributes()
    response = jsonify(objects_types)
    print(response)
    return response