# -*- coding: utf-8 -*-
"""
Created on Wed Aug 28 20:28:44 2024

@author: User
"""
# python -m flask --app names_to_flags run --port 8000 --debug

from flask import Blueprint, render_template
# By default, Flask expects your templates to be in a templates/ directory.
# Therefore, you don’t need to include templates/ in the path of the templates.

bp = Blueprint("pages", __name__)

@bp.route("/")
def home():
    return render_template("pages/home.html")

@bp.route("/about")
def about():
    return render_template("pages/about.html")

@bp.route("/donate")
def donate():
    return render_template("pages/donate.html")
