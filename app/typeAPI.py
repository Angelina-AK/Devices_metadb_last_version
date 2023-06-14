from flask import Blueprint, request, render_template, flash, url_for, redirect, jsonify
from flask_login import login_required
from flask_breadcrumbs import register_breadcrumb
from app.models import db, Attribute, AttributeType, ObjectType, AttributeValue

from .cfg import DEBUG

type_api = Blueprint('type_api', __name__, 
                        template_folder='templates', 
                        url_prefix='/types')


def view_edit_device_dlc():
    type_id: str = request.view_args['id']
    obj_type: 'ObjectType' = db.session.query(ObjectType).where(ObjectType.id == type_id).first() 
    return [{'text': f'Editing type {obj_type.type_name} with id={type_id}'}]


def create_attribute_type_rel(o_type: ObjectType, atrs:list[Attribute]) -> list[AttributeType]:
    type_attribute_relations: list[AttributeType] = list()
    for atr in atrs:
        ty_atr = AttributeType(object_type=o_type, attribute=atr)
        type_attribute_relations.append(ty_atr)

    return type_attribute_relations


@type_api.route('/types_view', methods=(['GET']))
@register_breadcrumb(type_api, '.', 'All objects types')
@login_required
def types_view():
    objects_types = db.session.query(ObjectType).all()
    print(objects_types)
    return render_template('types/types.html', objects_types=objects_types)


@type_api.route('/create', methods=('GET', 'POST'))
@register_breadcrumb(type_api, './create', 'Create new object type')
@login_required
def create():
    if request.method == 'POST':
        type_name = request.form['type_name']
        attributes = request.form.getlist('attribute')
        type_: Union[ObjectType, None] = db.session.query(ObjectType).where(ObjectType.type_name == type_name).first()
        if type_name == '':
            return render_template('types/type_create.html', e='Type name is required')

        if type_ is not None:
            return render_template('types/type_create.html', e=f'Type {type_name} is exists')

        
        # for atr in attributes:
        #     if atr == '':
        #         return render_template('types/type_create.html', e='All attributes must have name')

        
       

        attrs_object = Attribute.get_attrs_by_name(attributes)
        print(attrs_object)
        # if DEBUG == True:
        #     return render_template('types/type_create.html')

        new_type = ObjectType(type_name=type_name)
        atrs_type_rel = create_attribute_type_rel(new_type, attrs_object)
        #add all objects in session
        db.session.add_all(atrs_type_rel)
        db.session.add(new_type)

        db.session.commit()
        return redirect(url_for('type_api.types_view'))
    else:  
        return render_template('types/type_create.html')


@type_api.route('/delete/<int:id>', methods=(['GET']))
@login_required
def delete_type(id: int):
    type_for_delation: ObjectType = db.session.query(ObjectType).where(ObjectType.id == id).first()
    type_for_delation.delete_type()
    return redirect((url_for('type_api.types_view')))


@type_api.route('/edit/<int:id>', methods=(['GET', 'POST']))
@register_breadcrumb(type_api, './types_view', '', dynamic_list_constructor=view_edit_device_dlc)
@login_required
def edit_type(id: int):
    type_for_editing: ObjectType = db.session.query(ObjectType).where(ObjectType.id == id).first()
    if request.method == 'GET':
        current_attributes: list[Attribute] = type_for_editing.get_attributes_entity()
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
       
        return redirect((url_for('type_api.types_view')))


@type_api.route('/get_all', methods=(['GET']))
def get_all():
    objects_types = db.session.query(ObjectType).all()
    for obj_type in objects_types:
        obj_type.attributes = obj_type.get_attributes()
    response = jsonify(objects_types)
    return response