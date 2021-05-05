# main.py

from flask import Blueprint, render_template, redirect, request, flash
from flask_login import login_required, current_user
from .models import Preference
from . import recommender_system
from . import db

main = Blueprint('main', __name__)


@main.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('add_artists.html')
    else:
        return render_template('index.html')


# @main.route('/', methods=['POST'])
# @login_required
# def index_post():
#     return 0


# @main.route('/rate')
# @login_required
def render_rate_page(artist_name):
    print("\nName from rate func")
    return render_template('rate.html', name=artist_name)


@main.route('/rate', methods=['GET', 'POST'])
@login_required
def rate_get():
    if request.method == 'GET':
        artist = request.args.get('artist_name', None)
        rate = request.args.get('rate', None)
        # rate = request.form.get('rate')
        print("RATE:{}".format(rate))
        if rate is None:
            return render_rate_page(artist)
        print("\nName from rate post func", artist)
        user = current_user
        new_prefrence = Preference(name=artist, user_id=current_user.id, rate=int(rate))
        db.session.add(new_prefrence)
        db.session.commit()
        return redirect('/')
    else:
        return redirect('/recommendations')


@main.route('/recommendations')
@login_required
def recommendations():
    userId = current_user.id
    preferences = Preference.query.all()
    artists_dict = dict()
    for i in preferences:
        if i.user_id == current_user.id:
            artists_dict[i.name] = i.rate
    if len(artists_dict) == 0:
        flash('Add some artists')
        return render_template('add_artists.html', name=current_user.name, recommendations=[])
    recommendations_dict = recommender_system.songs_dict(artists_dict, 10)
    artists_list = list(recommendations_dict['artists'].values())
    return render_template('recommendations.html', name=current_user.name, recommendations=artists_list)


@main.route('/profile')
@login_required
def profile():
    userId = current_user.id
    preferences = Preference.query.all()
    artists = []
    for i in preferences:
        if i.user_id == current_user.id:
            artists.append(i.name)
    return render_template('profile.html', name=current_user.name, preferences=artists)
