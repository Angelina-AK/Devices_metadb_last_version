import json
import secrets

import jsonschema
import pytz
from flask import Blueprint, flash, redirect, render_template, request, url_for, jsonify
from flask_breadcrumbs import register_breadcrumb, default_breadcrumb_root
from flask_login import current_user, login_required
from genson import SchemaBuilder
from jsonschema import validate
from werkzeug.exceptions import abort

from app.models import (Building, Decoder, Payload, Device, Dev_dir, Dir_sensor, Directory, Range,Problem,Advice ,DeviceFloor, DeviceFlow,
                        DeviceParam, DeviceSchema, Sensor, Task, db)
from app.timeAPI import get_time

from  app.blueprints.visual.visualAPI import get_decoder_payload
from  app.blueprints.flows.flowsAPI import get_flow

directories_api = Blueprint('directories_api', __name__, template_folder='templates', static_folder='static')

default_breadcrumb_root(directories_api, '.')


#               Функции для путей в breadcrumbs
#____________________________________________________________________________

def view_selected_device(*args, **kwargs):
    device_id = request.view_args['device_id']
    device = Device.query.get(device_id)
    dirict_id = request.view_args['dir_id']
    return [{'text': "Directories", 'url': f"/directories/{dirict_id}"}, \
            {'text': device.name, 'url': device.id}]

def view_selected_directory(*args, **kwargs):
    dirict_id = request.view_args['dir_id']
    directory = Directory.query.get(dirict_id)
    return [{'text': "Directories", 'url': f"/directories/{dirict_id}"}, \
            {'text': directory.Name, 'url': f"/directories/sprav_info/{directory.id}"}]

def edit_selected_range(*args, **kwargs):
    range_id = request.view_args['rng_id']
    range = Range.query.get(range_id)
    directory = Directory.query.get(range.Directory_Id)
    range_text = "Range: " + range.Name
    return [{'text': "Directories", 'url': f"/directories/{range.Directory_Id}"}, \
            {'text': directory.Name, 'url': f"/directories/sprav_info/{range.Directory_Id}"}, \
            {'text': range_text, 'url': f"/directories/edit/{range.id}"} ]

def view_selected_directory_devices(*args, **kwargs):
    dirict_id = request.view_args['dir_id']
    directory = Directory.query.get(dirict_id)
    return [{'text': "Directories", 'url': f"/directories/{dirict_id}"}, \
            {'text': directory.Name, 'url': f"/directories/sprav_info/{directory.id}"}, \
            {'text': "Анализируемые устройства", 'url': f"/directories/sprav_info/{directory.id}/devices"}]




#        Страница устройств
#--------------------------------------------------------------------------------
@directories_api.route('/directories/<int:dir_id>')
@register_breadcrumb(directories_api, '.directory_view', 'Directories')
@login_required
def directory_process_devices(dir_id):
    if dir_id == 0:
        first_dir = Directory.query.first()
        dir_id = first_dir.id

    namepage="Обработка справочниками"
    try:
        dev_dirs = Dev_dir.query.filter(Dev_dir.directory_id == dir_id).all()
        list = []
        tmp = []

        devices_info = [] #Будущий список с информацией об устройствах

        for dv in dev_dirs:
            device = Device.query.filter(Device.id == dv.device_id).first()
            payload = Payload.query.filter(Payload.device_id == dv.device_id).order_by(Payload.created.desc()).first()
            sensors = Sensor.query.filter(Sensor.device_id == dv.device_id).all()  # 3 см. ниже

            # Декодирование данных
            if payload.value[0] == '{':
                data = json.loads(payload.value)
            else:
                data = get_flow(dv.device_id)
                data = json.loads(data.data)

            # Заполнение вложенного списка с информацией, где элемент это список из:
            # 1 - имя устройства
            # 2 - флаг о текущем состоянии устройста (True-все хорошо, False-с каким-то показателем что-то не так)
            # 3 - Описание устройства: список датчиков прибора
            # 4 - id прибора

            device_name = device.name  # 1
            device_id = device.id  # 4

            # Состояние устройства (при проверке может измениться)
            condition = True # 2

            bad_sensors = []

            # Определение состояния, в котором находится устройство
            # -------------------------------------------------------
            for d in data:
                try:
                    # Есть ли в БД информация про этот тип датчика
                    type = Dir_sensor.query.filter_by(Name=d).first()
                    if type:

                        try:
                            # Есть ли в БД информация из выбранного справочника для этого типа датчика
                            ranges = Range.query.filter_by(Sensor_Id=type.id,Directory_Id=dir_id).all()
                            if ranges:

                                for r in ranges:
                                    # Значение попало в диапазон с проблемой
                                    if data[d] >= r.Min and data[d] <= r.Max and r.prob:
                                        condition = False # 2
                                        bad_sensors.append(d)
                                        break
                                        break

                            else:
                                print("Для данного датчика нет диапазонов выбранном справочнике")
                                continue

                        except:
                            print("Не получилось считать диапазоны из БД")

                    else:
                        print("Про данный датчик нет информации в БД")
                        continue

                except:
                    print("Не получилось считать тип датчика из БД")

            # Заполнение вложенного списка
            devices_info.append([device_name, condition, sensors, device_id, bad_sensors])


    except:
        print("Ошибка подключения к базе данных для считывания Dev_Dir")

    # Для выпадающего списка справочников
    try:
        directories = Directory.query.all()
        selected_dir = Directory.query.filter(Directory.id == dir_id).first()

    except:

        print("Ошибка считывания справочников из БД")

    return render_template('directories.html', devices_info=devices_info, directories=directories, dir_id=dir_id, selected_dir=selected_dir.Name, namepage=namepage)



#        Страница графиков по данным с устройств
#--------------------------------------------------------------------------------
@directories_api.route('/directories/<int:dir_id>/<int:device_id>')
@register_breadcrumb(directories_api, '.directory_process_devices', '', dynamic_list_constructor=view_selected_device)
@login_required
def directory_process_selected_device(dir_id,device_id):
    namepage = "Обработка справочниками выбранного устройства"
    try:
        decoder_format = get_decoder_payload(device_id)

        # Выбранный датчик устройства
        sensors = Sensor.query.filter(Sensor.device_id==device_id).all()
        # if sensor=="default":
        #     if sensors:
        #         sensor=sensors[0].decode_key

        sprav_info = []
        for s in sensors:
            try:
                # проверка, есть ли описание в справочнике
                dir_sensor = Dir_sensor.query.filter(Dir_sensor.Name==s.decode_key).first()
                if dir_sensor:
                    try:
                        ranges = Range.query.filter(Range.Directory_Id==dir_id,Range.Sensor_Id==dir_sensor.id).all()
                        if ranges:
                            rngs = []
                            for r in ranges:
                                rngs.append({'Name': r.Name, 'Min': r.Min, 'Max': r.Max})
                            sprav_info.append({s.decode_key : rngs})
                    except:
                        print("Не удалось считать диапазоны из базы данных")
            except:
                print("Не получилось считать данные о справочных сенсорах из базы данных")


    except:
        print("Не получилось считать данные из базы данных")
    return render_template('selected_device.html',  sensors=sensors, sprav_info=sprav_info, device_id=device_id, decoder_format=decoder_format, namepage=namepage)




@directories_api.route('/directories/<int:device_id>/get_data')
def get_data(device_id):
    payloads = Payload.query.filter(Payload.device_id == device_id).order_by(Payload.created.desc()).limit(3000).all()
    data = []
    for payload in payloads:
        data.append(payload.toDict())
    return jsonify(data)



#        Страница содержимого справочника
#--------------------------------------------------------------------------------
@directories_api.route('/directories/sprav_info/<int:dir_id>')
@register_breadcrumb(directories_api, '.directory_view_info', '', dynamic_list_constructor=view_selected_directory)
@login_required
def directory_view_info(dir_id):
    try:
        namepage = "Содержимое справочника"

        ranges = Range.query.filter(Range.Directory_Id == dir_id).all()

        info = []
        # Заполнение списка из словарей для таблицы
        # Sensor | Min | Max | Problems | Advices
        #__________________________________________
        for r in ranges:
            sensor = Dir_sensor.query.filter(Dir_sensor.id == r.Sensor_Id).first()
            problems = Problem.query.filter(Problem.Range_Id == r.id).all()
            problem_text = ""
            advice_text = ""
            if not problems:
                problem_text = "No problems"
                advice_text = "No advices"
            else:
                i = 0
                any_problem = False
                for p in problems:
                    i+=1
                    if i == len(problems):
                        problem_text += p.Name + ""
                    else:
                        problem_text += p.Name + ",                                  "

                    advices = Advice.query.filter(Advice.Problem_Id == p.id).all()
                    if advices:
                        any_problem = True
                        j = 0
                        for a in advices:
                            j += 1
                            if j == len(advices):
                                advice_text += a.Content + ".                                  "
                            else:
                                advice_text += a.Content + ", "

                if not any_problem:
                    advice_text = "No advices"
            info.append({'Name': r.Name,'Sensor': sensor.Name, 'Min': r.Min, 'Max': r.Max, 'Problems': problem_text, 'Advices': advice_text, 'id': r.id})

        directory = Directory.query.filter(Directory.id == dir_id).first()
    except:
        print("Ошибка взаимодействия с БД")

    return render_template('directory_info.html', name = directory.Name, dir_id=dir_id, json_info = info, namepage=namepage)


#          Изменение имени выбранного справочника
#---------------------------------------------------------------
@directories_api.route('/directories/rename/<int:dir_id>', methods=('POST',))
@login_required
def rename_directory(dir_id):
    if request.method == 'POST':
        try:
            input_name = request.form['Dir_Name']
            all_directories = Directory.query.all()

            name_exist = False
            for d in all_directories:
                if d.Name == input_name and d.id != dir_id:
                    name_exist = True

            if name_exist:
                flash(f"Введенное имя справочника принадлежит уже существующему справочнику, изменения имени отменены", "error")
                return redirect(url_for('directories_api.directory_view_info', dir_id=dir_id))

            else:
                try:
                    directory = Directory.query.filter(Directory.id == dir_id).first()
                    directory.Name = input_name
                    db.session.commit()
                    flash(f"Имя справочника успешно сохранено", "success")
                    return redirect(url_for('directories_api.directory_view_info', dir_id=dir_id))
                except:
                    db.session.rollback()
                    print("Ошибка изменения имя справочника в БД")
        except:
            print("Не получается считать справочники из БД")


#  Добавление нового диапазона и перенаправление на страницу его редактирования
#--------------------------------------------------------------------------------
@directories_api.route('/directories/add/new_range/<int:dir_id>')
@login_required
def add_new_range(dir_id):
    # К новому диапазону добавится тип датчика - unknown
    try:
        dir_sensor = Dir_sensor.query.filter(Dir_sensor.Name == 'unknown').first()
        if not dir_sensor:
            dir_sensor = Dir_sensor(Name='unknown')
            try:
                db.session.add(dir_sensor)
                db.session.commit()
            except:
                db.session.rollback()
                print("Не получилось создать дефолтный тип датчика для справочников в БД")

        # Добавление диапазона в БД
        try:
            range = Range(Name = "new range", Directory_Id = dir_id, Sensor_Id = dir_sensor.id)
            db.session.add(range)
            db.session.commit()
            print(range.id)
            return redirect(url_for('directories_api.directory_edit_range', rng_id=range.id))
        except:
            db.session.rollback()
            print("Ошибка добавления диапазона в БД")
    except:
        print("Ошибка взаимодействия с БД")




#        Удаление диапазона и каскадное удаление его проблем и советов
#--------------------------------------------------------------------------------
@directories_api.route('/directories/delete/<int:range_id>')
@login_required
def delete_range(range_id):
    try:
        range = Range.query.filter(Range.id == range_id).first()
        range_name = range.Name
        dir_id = range.Directory_Id

        problems = Problem.query.filter(Problem.Range_Id == range_id).all()
        if problems:
            for p in problems:
                # Удаление всех советов к каждой из проблемы диапазона
                advices = Advice.query.filter(Advice.Problem_Id == p.id).all()
                if advices:
                    for a in advices:
                        try:
                            db.session.delete(a)
                        except:
                            db.session.rollback()
                            print("Не получилось удалить совет")
                # Удаление каждой проблемы (теперь уже точно без советов в БД)
                try:
                    db.session.delete(p)
                except:
                    db.session.rollback()
                    print("Не получилось удалить проблему")

        # Удаление самого диапазона
        try:
            db.session.delete(range)
            db.session.commit()
            flash(f"Диапазон \"{range_name}\" успешно удален из справочника", "success")
            return redirect(url_for('directories_api.directory_view_info', dir_id=dir_id))
        except:
            # db.session.rollback()
            print("Не получилось удалить диапазон из справочника")
    except:
        print("Ошибка взаимодейтсвия с БД")


#_________________________________________________________________________________________________________________________________

#        Страница изменения диапазона
#--------------------------------------------------------------------------------
@directories_api.route('/directories/edit/<int:rng_id>')
@register_breadcrumb(directories_api, '.directory_edit_range', '', dynamic_list_constructor=edit_selected_range)
@login_required
def directory_edit_range(rng_id):
    namepage = "Изменение диапазона справочника"

    try:
        #           Основная информация о диапазоне
        #__________________________________________________________
        range = Range.query.filter(Range.id == rng_id).first()
        sensor = Dir_sensor.query.filter(Dir_sensor.id == range.Sensor_Id).first()
        # Данные о диапазоне в списке
        # Name | тип датчика | Min | Max
        if sensor.Name != 'unknown':
            range_info = [range.Name, sensor.Name, range.Min, range.Max, range.id]
        else:
            range_info = ["", "", "", "", range.id]

        #           Проблемы в диапазоне
        #__________________________________________________________
        problems = Problem.query.filter(Problem.Range_Id == rng_id).all()
        null_problems = True
        problem_info = []
        if problems:
            null_problems = False
            for p in problems:
                problem_info.append({'Name': p.Name, 'id': p.id, 'delete_id': p.id})


        #           Советы к решению проблем
        #__________________________________________________________
        advice_info = []
        if problems:
            for p in problems:
                try:
                    p_advice = Advice.query.filter(Advice.Problem_Id == p.id).all()
                    for a in p_advice:
                        advice_info.append({'Problem' : p.Name, 'Advice' : a.Content, 'Save_id' : a.id, 'Delete_id' : a.id })
                except:
                    print("Ошибка считывания советов из БД")

        return render_template('edit_range.html',range_info = range_info, problem_info = problem_info, null_problems = null_problems, advice_info = advice_info, problems = problems, namepage=namepage)
    except:
        print("Ошибка взаимодействия с БД")





# Изменение основной информации о диапазоне
#********************************************
@directories_api.route('/directories/edit/update_range/<int:rng_id>', methods=('POST',))
@register_breadcrumb(directories_api, '.directory_edit_range_main', '', dynamic_list_constructor=edit_selected_range)
@login_required
def edit_range_main_info(rng_id):

    if request.method == 'POST':
        input_sensor_type = request.form['Sensor']
        input_name = request.form['Name']
        input_min = float(request.form['Min'])
        input_max = float(request.form['Max'])



        try:
            range = Range.query.filter(Range.id == rng_id).first()

            sensor = Dir_sensor.query.filter(Dir_sensor.id == range.Sensor_Id).first()

            #       Изменение типа датчика
            #____________________________________
            if input_sensor_type != sensor.Name:
                any_sensor = Dir_sensor.query.filter(Dir_sensor.Name == input_sensor_type).first()
                # Добавления нового типа датчика и привязка его к диапазону
                if not any_sensor:
                    new_sensor = Dir_sensor(Name = input_sensor_type)
                    try:
                        db.session.add(new_sensor)
                        db.session.commit()
                        try:
                            range.Sensor_Id = new_sensor.id
                            db.session.commit()
                            flash("Тип датчика для диапазона успешно сохранен", "success")

                        except:
                            db.session.rollback()
                            print("Ошибка изменения датчика диапазона БД")
                    except:
                        db.session.rollback()
                        print("Ошибка добавления датчика dir_sensor в БД")

                # Изменение типа датчика на существующий
                else:
                    try:
                        range.Sensor_Id = any_sensor.id
                        db.session.commit()
                        flash("Тип датчика для диапазона успешно изменен", "success")
                    except:
                        db.session.rollback()
                        print("Ошибка изменения датчика диапазона БД")


            #     Изменение имени диапазона
            # ____________________________________
            if range.Name != input_name:
                range.Name = input_name
                try:
                    db.session.commit()
                    flash("Имя диапазона успешно сохранено", "success")
                except:
                    db.session.rollback()
                    print("Ошибка изменения имени диапазона в БД")


            #   Изменение интервала в диапазоне
            # ____________________________________
            if range.Min != input_min or range.Max != input_max:

                # Проверка Max > Min
                if input_min < input_max:

                    # Проверка, не входит ли введенный диапазон в какой-то из уже существующих в выбранном справочнике
                    # кроме выбранного изменяемого диапазона
                    try:
                        ranges = Range.query.filter(Range.Directory_Id == range.Directory_Id, Range.Sensor_Id == range.Sensor_Id).all()
                        in_exist_range = False
                        if range.Min and range.Max:
                            for r in ranges:
                                if ( input_min > r.Min and input_min < r.Max and range.id != r.id) \
                                    or (input_max > r.Min and input_max < r.Max and range.id != r.id ) \
                                    or (input_min == r.Min and input_max == r.Max and range.id != r.id ) \
                                    or (input_min <= r.Min and input_max >= r.Max and range.id != r.id ):
                                    in_exist_range = True
                                    break


                        if not in_exist_range:
                            try:
                                # Изменение данных о диапазоне
                                range.Min = input_min
                                range.Max = input_max
                                db.session.commit()
                                flash("Данные диапазона Min, Max успешно сохранены", "success")
                            except:
                                db.session.rollback()
                                print("Ошибка изменения диапазона в БД")
                        else:
                            flash("Выбраннный диапазон является частью уже существующего, изменения отменены", "error")
                    except:
                        print("Не получилось считать диапазоны из БД и отсортировать по полям Directory_Id, Sensor_Id")
                else:
                    flash("Начальное значение интервала должно быть меньше конечного, изменения отменены", "error")
        except:
            print("Ошибка взаимодействия с БД")
        return redirect(url_for('directories_api.directory_edit_range', rng_id=rng_id))


#       Изменение проблемы в диапазоне
#********************************************
@directories_api.route('/directories/edit/prob/<int:prob_id>', methods=('POST',))
@login_required
def edit_range_problem(prob_id):
    try:
        problem = Problem.query.filter(Problem.id == prob_id).first()

        if request.method == 'POST':
            input_problem = request.form[problem.Name]
            change_possible = True

            # Проверка уникальности названия проблемы
            all_problems = Problem.query.filter(Problem.Range_Id == problem.Range_Id).all()
            for p in all_problems:
                if p.Name == input_problem and p.id != prob_id:
                    change_possible = False
                    break

            if change_possible:
                problem.Name = input_problem
                try:
                    db.session.commit()
                    flash("Имя проблемы успешно сохранено", "success")
                except:
                    db.session.rollback()
                    print("Ошибка изменения названия проблемы в БД")
            else:
                flash("Введенная проблема уже добавлена к данному диапазону, изменение отменено", "error")

    except:
        print("Ошибка взаимодействия с БД")

    return redirect(url_for('directories_api.directory_edit_range', rng_id=problem.Range_Id))


#       Удаление проблемы в диапазоне
#********************************************
@directories_api.route('/directories/delete/prob/<int:prob_id>', methods=('POST',))
@login_required
def delete_range_problem(prob_id):
    try:
        problem = Problem.query.filter(Problem.id == prob_id).first()
        p_advices = Advice.query.filter(Advice.Problem_Id == prob_id).all()
        try:
            for a in p_advices:
                db.session.delete(a)
            db.session.delete(problem)
            db.session.commit()
            flash("Проблема и все советы по ее решению (при наличии) успешно удалены", "success")
        except:
            db.session.rollback()
            print("Ошибка удаления проблемы из БД")

    except:
        print("Ошибка взаимодействия с БД")

    return redirect(url_for('directories_api.directory_edit_range', rng_id=problem.Range_Id))


#      Добавление проблемы в диапазоне
#********************************************
@directories_api.route('/directories/add/prob/<int:range_id>', methods=('POST',))
@login_required
def add_range_problem(range_id):
    if request.method == 'POST':
        input_name = request.form['Name']
        try:
            any_problem = Problem.query.filter(Problem.Name == input_name).first()
            if any_problem:
                flash("Введенная проблема уже добавлена к данному диапазону, добавление отменено", "error")
            else:
                try:
                    new_problem = Problem(Name = input_name, Range_Id = range_id)
                    db.session.add(new_problem)
                    db.session.commit()
                    flash("Проблема успешно добавлена", "success")
                except:
                    db.session.rollback()
                    print("Ошибка добавления проблемы в БД")
        except:
            print("Ошибка взаимодействия с БД")

        return redirect(url_for('directories_api.directory_edit_range', rng_id=range_id))


#       Изменение совета в диапазоне
#********************************************
@directories_api.route('/directories/edit/advice/<int:advice_id>', methods=('POST',))
@login_required
def edit_range_advice(advice_id):
    try:
        advice = Advice.query.filter(Advice.id == advice_id).first()
        problem = Problem.query.filter(Problem.id == advice.Problem_Id).first()

        if request.method == 'POST':
            input_advice = request.form[advice.Content]
            change_possible = True

            # Проверка уникальности совета для выбранной проблемы
            all_advices = Advice.query.filter(Advice.Problem_Id == advice.Problem_Id).all()
            for a in all_advices:
                if a.Content == input_advice and a.id != advice_id:
                    change_possible = False
                    break

            if change_possible:
                advice.Content = input_advice
                try:
                    db.session.commit()
                    flash(f"Совет по решению проблемы {problem.Name} успешно изменен на: \"{input_advice}\"", "success")
                except:
                    db.session.rollback()
                    print("Ошибка изменения совета в БД")
            else:
                flash(f"Введенный совет по решению проблемы {problem.Name} уже существует, изменения отменены", "error")

    except:
        print("Ошибка взаимодействия с БД")

    return redirect(url_for('directories_api.directory_edit_range', rng_id=problem.Range_Id))


#       Удаление совета в диапазоне
#********************************************
@directories_api.route('/directories/delete/advice/<int:advice_id>', methods=('POST',))
@login_required
def delete_range_advice(advice_id):
    try:
        advice = Advice.query.filter(Advice.id == advice_id).first()
        content = advice.Content
        problem = Problem.query.filter(Problem.id == advice.Problem_Id).first()

        try:
            db.session.delete(advice)
            db.session.commit()
            flash(f"Совет {content} по решению проблемы {problem.Name} успешно удален", "success")
        except:
            db.session.rollback()
            print("Ошибка изменения совета в БД")

    except:
        print("Ошибка взаимодействия с БД")

    return redirect(url_for('directories_api.directory_edit_range', rng_id=problem.Range_Id))



#      Добавление совета в диапазоне
#********************************************
@directories_api.route('/directories/add/advice', methods=('POST',))
@login_required
def add_range_advice():
    if request.method == 'POST':
        problem_id = request.form['Problem']
        input_advice = request.form['Advice']
        try:
            problem = Problem.query.filter(Problem.id == problem_id).first()
            try:
                new_advice = Advice(Content = input_advice, Problem_Id = problem_id)
                db.session.add(new_advice)
                db.session.commit()
                flash(f"Совет к проблеме {problem.Name}: \"{input_advice}\" - успешно добавлен", "success")
                return redirect(url_for('directories_api.directory_edit_range', rng_id=problem.Range_Id))
            except:
                db.session.rollback()
                print("Ошибка добавления совета в БД")
        except:
            print("Ошибка взаимодействия с БД")


#__________________________________________________________________________________________________________________________________

#        Страница анализируемых устройств
#--------------------------------------------------------------------------------
@directories_api.route('/directories/sprav_info/<int:dir_id>/devices')
@register_breadcrumb(directories_api, '.directory_view_info_devices', '', dynamic_list_constructor=view_selected_directory_devices)
@login_required
def directory_view_info_devices(dir_id):
    try:
        namepage = "Анализируемые справочником устройства"

        dev_dirs = Dev_dir.query.filter(Dev_dir.directory_id == dir_id).all()

        # Заполнение списка из словарей для таблицы уже анализируемых устройств
        # Device | Sensors | id (Delete from list)
        #_______________________________________________________________________
        device_info = []

        for dev in dev_dirs:
            try:
                device = Device.query.filter(Device.id == dev.device_id).first()
                try:
                    sensors = Sensor.query.filter(Sensor.device_id == dev.device_id).all()
                    sensors_text = ""
                    i = 0
                    for s in sensors:
                        i += 1
                        if i ==len(sensors):
                            sensors_text += s.decode_key + "."
                        else:
                            sensors_text += s.decode_key + ", "
                    device_info.append({'Device' : device.name, 'Sensors' : sensors_text, 'id' : device.id})
                except:
                    print("Не получилось считать Sensor из БД")
            except:
                print("Не получилось считать Device из БД")


        directory = Directory.query.filter(Directory.id == dir_id).first()
        title1 = f"Список устройств, анализируемых справочником {directory.Name}"
        title2 = f"Устройства, не анализируемые справочником {directory.Name}. Список для добавления устройств к анализу."


        # Заполнение списка из словарей для таблицы уже не анализируемых устройств
        # Device | Sensors | id (Add to list)
        #_______________________________________________________________________
        try:
            all_devices = Device.query.all()
            devices_to_add_info = []
            for d in all_devices:
                try:
                    check_device = Dev_dir.query.filter(Dev_dir.device_id == d.id, Dev_dir.directory_id == dir_id).first()
                    if not check_device:
                        try:
                            sensors = Sensor.query.filter(Sensor.device_id == d.id).all()
                            sensors_text = ""
                            i = 0
                            for s in sensors:
                                i += 1
                                if i == len(sensors):
                                    sensors_text += s.decode_key + "."
                                else:
                                    sensors_text += s.decode_key + ", "
                            devices_to_add_info.append({'Device': d.name, 'Sensors': sensors_text, 'id': d.id})
                        except:
                            print("Не получилось считать Sensor из БД")
                except:
                    print("Не получилось проверить наличие устройства в БД")

        except:
            print("Не получилось считать все устройства из БД")


    except:
        print("Не получилолось считать Dev_dir из БД")

    return render_template('directory_info_devices.html', title1 = title1, title2 = title2, device_info = device_info, dir_id = dir_id, devices_to_add_info = devices_to_add_info, namepage=namepage)



# Удаление устройства из списка анализируемых
#**********************************************
@directories_api.route('/directories/delete/device/<int:device_id>/from/<int:dir_id>')
@login_required
def delete_device_from_directory(device_id,dir_id):

    try:
        dev_dir = Dev_dir.query.filter(Dev_dir.device_id == device_id, Dev_dir.directory_id == dir_id).first()
        device = Device.query.filter(Device.id == device_id).first()
        directory = Directory.query.filter(Directory.id == dir_id).first()

        try:
            db.session.delete(dev_dir)
            db.session.commit()
            flash(f"Устройство {device.name} удалено из списка анализируемых справочником {directory.Name}", "success")
            return redirect(url_for('directories_api.directory_view_info_devices', dir_id=dir_id))
        except:
            db.session.rollback()

    except:
        print("Не получилось считать dev_dir, Device, Directory из БД")





# Добавление устройства к списку анализируемых справочником
#*************************************************************
@directories_api.route('/directories/add/device/<int:device_id>/to/<int:dir_id>')
@login_required
def add_device_to_directory(device_id,dir_id):

    try:
        new_dev_dir = Dev_dir(device_id = device_id, directory_id = dir_id)
        device = Device.query.filter(Device.id == device_id).first()
        directory = Directory.query.filter(Directory.id == dir_id).first()

        try:
            db.session.add(new_dev_dir)
            db.session.commit()
            flash(f"Устройство {device.name} добавлено к списку анализируемых справочником {directory.Name}", "success")

            return redirect(url_for('directories_api.directory_view_info_devices', dir_id=dir_id))

        except:
            db.session.rollback()
            print("Не получилось добавить устройство к списку анализируемых в БД")

    except:
        print("Не получилось считать dev_dir, Device, Directory из БД")


#_____________________________________________________________________________________________________________________________

#       Создание нового справочника и перенаправление на его страницу
#--------------------------------------------------------------------------------
@directories_api.route('/directories/add/new_directory')
@login_required
def add_new_directory():
    try:
        new_directory = Directory(Name = "Unknown")
        db.session.add(new_directory)
        db.session.commit()
        return redirect(url_for('directories_api.directory_view_info', dir_id = new_directory.id))

    except:
        db.session.rollback()
        print("Ошибка добавления диапазона в БД")


#     Удаление справчоника и перенаправление на страницу с панелями устройств
#--------------------------------------------------------------------------------
@directories_api.route('/directories/delete/directory/<int:dir_id>')
@login_required
def delete_directory_function(dir_id):
    try:
        dir_count = db.session.query(Directory.Name).count()
        if dir_count == 1:
            flash("Это единственный справочник, удаление невозможно", "error")
            return redirect(url_for('directories_api.directory_view_info', dir_id=dir_id))
        else:
            try:
                directory = Directory.query.filter(Directory.id == dir_id).first()
                ranges = Range.query.filter(Range.Directory_Id == dir_id).all()

                # Каскадное удаление: Советы -> Проблемы -> Диапазоны -> Справочник
                #___________________________________________________________________
                for r in ranges:
                    problems = Problem.query.filter(Problem.Range_Id == r.id).all()
                    for p in problems:
                        advices = Advice.query.filter(Advice.Problem_Id == p.id).all()
                        for a in advices:
                            try:
                                db.session.delete(a)
                                db.session.commit()
                            except:
                                db.session.rollback()
                                print("Не получилось удалить советы")
                        try:
                            db.session.delete(p)
                            db.session.commit()
                        except:
                            db.session.rollback()
                            print("Не получилось удалить проблемы")
                    try:
                        db.session.delete(r)
                        db.session.commit()
                    except:
                        db.session.rollback()
                        print("Не получилось удалить диапазон")
                try:
                    db.session.delete(directory)
                    db.session.commit()
                except:
                    db.session.rollback()
                    print("Не получилось удалить справочник")

                return redirect(url_for('directories_api.directory_process_devices', dir_id = 0))

            except:
                print("Не получилось считать directory, range")
    except:
        print("Не получилось считать  количество справочников")
