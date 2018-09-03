import os
import json

from flask import (Flask, redirect, url_for, render_template,
        request, abort, send_from_directory)

from flask_misaka import Misaka

app = Flask(__name__)
mikasa = Misaka(app, fenced_code=True)

uri_root_path = os.environ['URI_ROOT_PATH']

@app.route('/')
def home():
    return redirect(url_for('user_home'))

@app.route(uri_root_path + '/')
def user_home():
    return redirect(url_for('terminal_home'))

@app.route(uri_root_path + '/terminal/')
def terminal_home():
    return 'whoops, how did I get here'

course_directory = os.path.join(os.path.dirname(__file__),
        'templates', 'content')
course_index_file = os.path.join(course_directory, 'index.json')

course = {}

if os.path.exists(course_index_file):
    with open(course_index_file) as fp:
        course = json.load(fp)

course_modules = {}

previous = None
current = None

for current in course['modules']:
    course_modules[current['file']] = current

    current['previous'] = previous and previous['file']

    if previous:
        previous['next'] = current['file']

    previous = current

if current:
    current['next'] = None

@app.route(uri_root_path + '/dashboard/')
def dashboard():
    return render_template("course/dashboard.html", course=course)

@app.route(uri_root_path + '/workshop/')
def modules_list():
    embedded = request.args.get('embedded')

    return render_template("course/modules-list.html", course=course,
            embedded=embedded)

@app.route(uri_root_path + '/workshop/<module>')
def module_file(module):
    if not course:
        abort(404)

    stub = os.path.splitext(module)[0]

    if stub not in course_modules:
        abort(404)

    filename = 'content/%s.md' % stub

    embedded = request.args.get('embedded')

    return render_template("course/module-file.html",
            module=course_modules[stub], filename=filename,
            embedded=embedded)

@app.route(uri_root_path + '/workshop/images/<image>')
def image_file(image):
    return send_from_directory(course_directory+'/images', image)

@app.route(uri_root_path + '/static/<path:filename>')
def static_file(filename):
    return send_from_directory(os.path.dirname(__file__)+'/static', filename)
