from flask import Flask
from flask import render_template, request, abort
import json
import random
import flask_sqlalchemy
import os
from sqlalchemy.dialects.postgresql import JSON, ARRAY
from flask_migrate import Migrate
print(os.environ)
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = flask_sqlalchemy.SQLAlchemy(app)
migrate = Migrate(app, db)
days = {'mon': 'Понедельник', 'tue': 'Вторник', 'wed': 'Среда', 'thu': 'Четверг', 'fri': 'Пятница'}


class TeacherModel(db.Model):
    __tablename__ = "teachers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    about = db.Column(db.String(), nullable=False, unique=True)
    rating = db.Column(db.Float)
    picture = db.Column(db.String(), nullable=False)
    price = db.Column(db.Integer)
    goals = db.Column(ARRAY(db.String))
    free = db.Column(db.String(), nullable=False)
    bookings = db.relationship("BookingModel")


class BookingModel(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    teacher = db.relationship("TeacherModel")
    teacher_id = db.Column(db.Integer, db.ForeignKey("teachers.id"))
    day = db.Column(db.String(3))
    time = db.Column(db.String())
    name = db.Column(db.String())
    phone = db.Column(db.String())


class RequestModel(db.Model):
    __tablename__ = "requests"
    id = db.Column(db.Integer, primary_key=True)
    goal = db.Column(db.String())
    time = db.Column(db.String())
    name = db.Column(db.String())
    phone = db.Column(db.String())


def create_teachers_db():
    teachers = []
    with open("teachers_db.json", "r") as database:
        profiles = json.load(database)
        for teacher in profiles:
            teachers.append(TeacherModel(name=teacher['name'], about=teacher['about'], rating=teacher['rating'],
                                         picture=teacher['picture'], price=teacher['price'], goals=teacher['goals'],
                                         free=json.dumps(teacher['free'])))
    db.session.add_all(teachers)
    db.session.commit()


@app.route('/')
def main_page():
    #    db.create_all()
    #    create_teachers_db()
    id_list = list(range(0, 12))
    rand_profile_ids = random.sample(id_list, k=6)
    rand_profiles = []
    for i in rand_profile_ids:
        rand_profiles.append(db.session.query(TeacherModel).get_or_404(i))
    return render_template('index.html', data=rand_profiles)


@app.route('/all/', methods=['GET', 'POST'])
def return_all_profiles():
    profiles = db.session.query(TeacherModel).all()
    if request.method == 'POST':
        if request.form['ord_select'] == '1':
            profiles = db.session.query(TeacherModel).order_by(TeacherModel.price.desc()).all()
        if request.form['ord_select'] == '2':
            profiles = db.session.query(TeacherModel).order_by(TeacherModel.price).all()
        if request.form['ord_select'] == '3':
            profiles = db.session.query(TeacherModel).order_by(TeacherModel.rating.desc()).all()
    return render_template('all.html', data=profiles)


@app.route('/profiles/<int:id>/')
def get_profile(id):
    profile = db.session.query(TeacherModel).get_or_404(id)
    with open("goals_db.json", "r") as database:
        goals = json.load(database)
    t_goals = [goals[i] for i in profile.goals]
    return render_template('profile.html', data=profile, goals=t_goals, days=days, free=json.loads(profile.free))
    if request.method == 'POST':
        booking = BookingModel(teacher_id=request.form['clientTeacher'], day=request.form['clientWeekday'],
                               time=request.form['clientTime'], name=request.form['clientName'],
                               phone=request.form['clientPhone'])
        db.session.add(booking)
        db.session.commit()
        return render_template('booking_done.html', day=days[booking.day], time=booking.time,
                               name=booking.name, phone=booking.phone)


@app.route('/booking/<int:id>/<day>/<time>/', methods=['GET', 'POST'])
def get_booking_form(id, day, time):
    if request.method == 'POST':
        booking = BookingModel(teacher_id=request.form['clientTeacher'], day=request.form['clientWeekday'],
                               time=request.form['clientTime'], name=request.form['clientName'],
                               phone=request.form['clientPhone'])
        db.session.add(booking)
        db.session.commit()
        return render_template('booking_done.html', day=days[booking.day], time=booking.time,
                               name=booking.name, phone=booking.phone)
    profile = db.session.query(TeacherModel).get_or_404(id)
    if not (day in days.keys() or int(time) in list(range(8, 24))):
        return abort(404)
    return (render_template('booking.html', id=id, day=day, time=time, name=profile.name, pic=profile.picture,
                            day_rus=days[day]))


@app.route('/request/')
def get_request():
    return render_template('request.html')


@app.route('/request/', methods=['POST'])
def save_request():
    req = RequestModel(goal=request.form['goal'], time=request.form['time'], name=request.form['clientName'],
                       phone=request.form['clientPhone'])
    return render_template('request_done.html', goal=req.goal, time=req.time,
                           name=req.name, phone=req.phone)


@app.route('/goals/<goal>')
def get_teachers_by_goal(goal):
    profiles = {}
    with open("goals_db.json", "r") as database:
        goals = json.load(database)
    if goal not in goals.keys():
        return abort(404)
    profiles = db.session.query(TeacherModel).filter(TeacherModel.goals.contains([goal])).all()
    return render_template('goal.html', data=profiles, goal=goals[goal])


if __name__ == '__main__':
    app.run()
