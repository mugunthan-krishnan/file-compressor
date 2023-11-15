from flask import Blueprint, render_template
home = Blueprint('home', __name__, url_prefix='/')

@home.route('/')
def homePage():
    return render_template('home.html')