from flask import Blueprint, request, render_template, flash, url_for, redirect
from flask_login import login_required, current_user
from app.models import Task

from app.models import db
from werkzeug.exceptions import abort

tasks_api = Blueprint('tasks_api', __name__, template_folder='templates')


def get_task(id):
    task = Task.query.get(id)
    if task is None:
        abort(404)
    return task


@tasks_api.route('/tasks')
@login_required
def tasks_view():
    namepage = "Список задач"
    tasks = Task.query.filter(Task.user_id == current_user.id).all()
    return render_template('tasks/tasks.html', tasks=tasks, namepage=namepage)


@tasks_api.route('/tasks/create', methods=('GET', 'POST'))
@login_required
def task_create():
    if request.method == 'POST':
        name = request.form['name']
        device_id = request.form['device_id']
        url = ""
        if not device_id:
            flash('Title is required!')
        else:
            user_id = current_user.id
            new_task = Task(user_id, device_id, url)
            db.session.add(new_task)
            db.session.commit()
            return redirect(url_for('tasks_api.tasks_view'))
    return render_template('tasks/task_create.html')


@tasks_api.route('/tasks/<int:id>')
@login_required
def task_view(id):
    task = get_task(id)
    if(task.user_id == current_user.id):
        namepage = "Задача: " + task.name
        return render_template('tasks/task.html', task=task, namepage=namepage)
    else:
        return redirect(url_for('tasks_api.tasks_view'))


@tasks_api.route('/tasks/<int:id>/edit', methods=('GET', 'POST'))
@login_required
def task_edit(id):
    task = get_task(id)
    if (task.user_id == current_user.id):
        if request.method == 'POST':
            name = request.form['name']
            device_id = request.form['device_id']
            url = request.form['url']

            if not device_id:
                flash('Title is required!')
            else:
                task.name = name
                task.device_id = device_id
                task.url = url
                db.session.commit()

                return redirect(url_for('tasks_view'))
        namepage = "Редактирование: " + task.name
        return render_template('tasks/task_edit.html', task=task, namepage=namepage)
    else:
        return redirect(url_for('tasks_api.tasks_view'))


@tasks_api.route('/tasks/<int:id>/delete', methods=('POST',))
@login_required
def task_delete(id):
    task = get_task(id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('tasks_api.tasks_view'))



