# main.py

from flask import Blueprint, render_template, redirect, request
from flask_login import login_required, current_user
from .models import Preference
from . import db

main = Blueprint('main', __name__)


@main.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('add_artists.html')
    else:
        return render_template('index.html')


@main.route('/')
@login_required
def index_auth():
    return render_template('add_artists.html')


@main.route('/', methods=['POST'])
@login_required
def index_post():
    return rate(request.form.get('name'))


@main.route('/rate')
@login_required
def rate(name):
    return render_template('rate.html', name=name)


@main.route('/rate', methods=['POST'])
@login_required
def rate_post():
    artist = request.form.get('artist')
    print(artist)
    rate = request.form.get('rate')
    user = current_user
    new_prefrence = Preference(name=artist, user_id=current_user.id, rate=rate)
    db.session.add(new_prefrence)
    db.session.commit()
    return redirect('/')


@main.route('/profile')
@login_required
def profile():
    userId = current_user.id
    preferences = Preference.query.all()
    artists = []
    for i in preferences:
        if i.user_id == current_user.id:
            print(i.user_id, current_user.id)
            artists.append(i.name)
    return render_template('profile.html', name=current_user.name, preferences=artists)
