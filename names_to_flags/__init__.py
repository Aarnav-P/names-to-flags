# -*- coding: utf-8 -*-
"""
Created on Wed Aug 28 17:30:15 2024

@author: User
"""
from flask import Flask

from names_to_flags import pages

def create_app():
    app = Flask(__name__, static_folder ="static")
    app.register_blueprint(pages.bp)
    return app
