from flask import render_template
from . import main


def not_found(e):
    return render_template('404.html'), 404


def forbidden(e):
    return render_template('403.html'), 403


def internal_server(e):
    return render_template('500.html'), 500