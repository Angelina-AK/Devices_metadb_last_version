from flask import Blueprint, request, render_template, flash, url_for, redirect
from flask_login import login_required, current_user
from app.models import Building, User, Floor

from app.models import db
from werkzeug.exceptions import abort
import os
from uuid import uuid4

from werkzeug.utils import secure_filename

from PIL import Image
from flask_breadcrumbs import register_breadcrumb

buildings_api = Blueprint('buildings_api', __name__, template_folder='templates/buildings')


def get_building(id):
    building = Building.query.get(id)
    if building is None:
        abort(404)
    return building

def get_floor(id):
    floor = Floor.query.get(id)
    if floor is None:
        return None
    return floor

@buildings_api.route('/buildings')
@register_breadcrumb(buildings_api, '.', 'Buildings')
@login_required
def buildings_view():
    buildings = Building.query.all()
    namepage = "Здания"
    return render_template('buildings.html', buildings=buildings, namepage=namepage)


@buildings_api.route('/buildings/create', methods=('GET', 'POST'))
@register_breadcrumb(buildings_api, '.buildings', 'Create building')
@login_required
def building_create():
    namepage = "Создание здания"
    if request.method == 'POST':
        name = request.form['name']

        user_id = current_user.id
        new_building = Building(user_id, name)
        if not name:
            flash('Title is required!')
        else:
            db.session.add(new_building)
            db.session.commit()

            return redirect(url_for('buildings_api.buildings_view'))
    """elif request.method == 'GET':
        buildings = Building.query.all()
        results = [
            {
                "title": building.title,
                "content": building.content
            } for post in posts]

        return {"count": len(results), "posts": results}
        """
    return render_template('building_create.html', namepage=namepage)



def view_floor_dlc(*args, **kwargs):
    floor_id = request.view_args['id']
    floor = Floor.query.get(floor_id)
    building = floor.building
    return [{'text': building.name, 'url': '/buildings/' + str(building.id)}, {'text': floor.name, 'url': floor.id}]

def view_floor_edit_dlc(*args, **kwargs):
    floor_id = request.view_args['id']
    floor = Floor.query.get(floor_id)
    building = floor.building
    return [{'text': building.name, 'url': '/buildings/' + str(building.id)+ '/floors'} , {'text': floor.name, 'url': '/buildings/floors/'+ str(floor.id)+'/edit'}]



def view_building_floor_dlc(*args, **kwargs):
    building_id = request.view_args['id']
    building = Building.query.get(building_id)
    return [{'text': building.name, 'url': '/buildings/'+str(building.id)}, {'text': 'Floors', 'url': '/buildings/'+str(building.id)+'/floors'}]




def view_building_dlc(*args, **kwargs):
    building_id = request.view_args['id']
    building = Building.query.get(building_id)
    return [{'text': building.name, 'url': building.id}]


def view_building_edit_dlc(*args, **kwargs):
    building_id = request.view_args['id']
    building = Building.query.get(building_id)
    return [{'text': building.name, 'url': '/buildings/'+str(building.id) + '/edit'}]


@buildings_api.route('/buildings/<int:id>')
@register_breadcrumb(buildings_api, '.buildings/id', '', dynamic_list_constructor=view_building_dlc)
@login_required
def building_view(id):
    building = get_building(id)
    namepage = "Здание: " + building.name
    return render_template('building.html', building=building, namepage=namepage)


@buildings_api.route('/buildings/<int:id>/edit', methods=('GET', 'POST'))
@register_breadcrumb(buildings_api, '.buildings/id/edit', '', dynamic_list_constructor=view_building_edit_dlc)
@login_required
def building_edit(id):
    building = get_building(id)
    namepage = "Изменение дания: " + building.name
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        address = request.form['address']
        icon = request.form['icon']

        if not name:
            flash('Title is required!')
        else:

            building.name = name
            building.description = description
            building.address = address
            building.icon = icon

            db.session.commit()

            return redirect(url_for('buildings_api.buildings_view'))

    return render_template('building_edit.html', building=building, namepage=namepage)


@buildings_api.route('/buildings/<int:id>/delete', methods=('POST',))
@login_required
def building_delete(id):
    building = get_building(id)
    db.session.delete(building)
    db.session.commit()
    return redirect(url_for('buildings_api.buildings_view'))


@buildings_api.route('/buildings/<int:id>/floors')
@register_breadcrumb(buildings_api, '.buildings/id/floors',  'Floors', dynamic_list_constructor=view_building_floor_dlc )
@login_required
def floors_view(id):
    namepage = "Этажи"
    building = get_building(id)

    return render_template('floors.html', building=building, namepage=namepage)

@buildings_api.route('/buildings/floors/<int:id>')
@register_breadcrumb(buildings_api, '.buildings/floors/id',  '', dynamic_list_constructor=view_floor_dlc )
@login_required
def floor_view(id):
    floor = get_floor(id)
    namepage = "Этаж " + floor.name



    return render_template('floor.html', floor=floor, namepage=namepage)


@buildings_api.route('/buildings/floors/<int:id>/edit', methods=('POST', 'GET'))
@register_breadcrumb(buildings_api, '.buildings/floors/id/edit',  '', dynamic_list_constructor=view_floor_edit_dlc )
@login_required
def floor_edit(id):
    floor = get_floor(id)
    namepage = "Изменение этажа: " + floor.name

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        image = request.form['image']

        if not name:
            flash('Title is required!')
        else:

            floor.name = name
            floor.description = description
            floor.image = image

            db.session.commit()

            return redirect(url_for('buildings_api.floor_edit', id=id))

    return render_template('floor_edit.html', floor=floor, namepage=namepage)


@buildings_api.route('/buildings/<int:id>/floors/create', methods=('GET', 'POST'))
@login_required
def floor_create(id):
    namepage = "Создание этажа"
    if request.method == 'POST':
        name = request.form['name']
        new_floor = Floor(id, name)

        if not name:
            flash('Title is required!')
        else:
            db.session.add(new_floor)
            db.session.commit()

            return redirect(url_for('buildings_api.floor_view', id=new_floor.id))

    return render_template('floor_create.html', namepage=namepage)


@buildings_api.route('/buildings/floors/<int:id>/delete', methods=('POST',))
@login_required
def floor_delete(id):
    floor = get_floor(id)
    db.session.delete(floor)
    db.session.commit()
    return redirect(url_for('buildings_api.floors_view'))

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

import svgutils


@buildings_api.route('/buildings/floors/<int:id>/upload_image', methods=['GET', 'POST'])
def upload_file(id):
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'there is no file in form!'
        file = request.files['file']




        filename = secure_filename(file.filename)
        file_extension = filename.split(".")[1].lower()



        unique_filename = uuid4().__str__() + '.'+ file_extension


        path = os.path.join('app/static/upload', unique_filename)
        file.save(path)

        if file_extension == "svg":
            svg = svgutils.transform.fromfile(path)
            width = svg.width.split("px")[0]
            height = svg.height.split("px")[0]
        else:
            im = Image.open(path)
            width, height = im.size

        floor = get_floor(id)
        floor.image = unique_filename
        floor.width = width
        floor.height = height
        db.session.commit()





        return redirect(url_for('buildings_api.floor_view', id=id))