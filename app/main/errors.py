from flask import render_template
from . import main


@main.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@main.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403


@main.errorhandler(500)
def internal_server(e):
    return render_template('500.html'), 500