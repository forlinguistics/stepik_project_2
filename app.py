from flask import Flask
from flask import render_template, request, abort
import json
import random

app = Flask(__name__)

days = {'mon': 'Понедельник', 'tue': 'Вторник', 'wed': 'Среда', 'thu': 'Четверг', 'fri': 'Пятница'}


def data_for_id(id):
    profiles = {}
    with open("teachers_db.json", "r") as database:
        profiles = json.load(database)
    profile = [i for i in profiles if i['id'] == id]
    if profile == []:
        return abort(404)
    return profile[0]


def save_user_input(input, file_name):
    data = {}
    with open(file_name, "r") as database:
        data = json.load(database)
    data.append(input)
    with open(file_name, "w") as database:
        new_data = json.dumps(data)
        database.write(new_data)


@app.route('/')
def main_page():
    id_list = list(range(0, 12))
    rand_profile_ids = random.sample(id_list, k=6)
    rand_profiles = []
    for i in rand_profile_ids:
        rand_profiles.append(data_for_id(i))
    return render_template('index.html', data=rand_profiles)


@app.route('/all/')
def return_all_profiles():
    profiles = []
    with open("teachers_db.json", "r") as database:
        profiles = json.load(database)
    return render_template('all.html', data=profiles)


@app.route('/profiles/<int:id>/')
def get_profile(id):
    profile = data_for_id(id)
    with open("goals_db.json", "r") as database:
        goals = json.load(database)
    t_goals = [goals[i] for i in profile['goals']]
    return render_template('profile.html', data=profile, goals=t_goals, days=days)


@app.route('/booking/<int:id>/<day>/<time>/')
def get_booking_form(id, day, time):
    profile = data_for_id(id)
    if not (day in days.keys() or int(time) in list(range(8, 24))):
        return abort(404)
    return (render_template('booking.html', id=id, day=day, time=time, name=profile['name'], pic=profile['picture'],
                            day_rus=days[day]))


@app.route('/booking_done/', methods=['POST'])
def save_booking():
    booking_dict = {}
    booking_dict['teacher_id'] = request.form['clientTeacher']
    booking_dict['day'] = request.form['clientWeekday']
    booking_dict['time'] = request.form['clientTime']
    booking_dict['name'] = request.form['clientName']
    booking_dict['phone'] = request.form['clientPhone']
    save_user_input(booking_dict, 'booking.json')
    return render_template('booking_done.html', day=days[booking_dict['day']], time=booking_dict['time'],
                           name=booking_dict['name'], phone=booking_dict['phone'])


@app.route('/request/')
def get_request():
    return render_template('request.html')


@app.route('/request_done/', methods=['POST'])
def save_request():
    request_dict = {}
    request_dict['goal'] = request.form['goal']
    request_dict['time'] = request.form['time']
    request_dict['name'] = request.form['clientName']
    request_dict['phone'] = request.form['clientPhone']
    save_user_input(request_dict, 'request.json')
    return render_template('request_done.html', goal=request_dict['goal'], time=request_dict['time'],
                           name=request_dict['name'], phone=request_dict['phone'])


@app.route('/goals/<goal>')
def get_teachers_by_goal(goal):
    profiles = {}
    with open("goals_db.json", "r") as database:
        goals = json.load(database)
    if  goal not in goals.keys():
        return abort(404)
    with open("teachers_db.json", "r") as database:
        profiles = json.load(database)
    return render_template('goal.html', data=[i for i in profiles if goal in i['goals']], goal=goals[goal])


if __name__ == '__main__':
    app.run()
