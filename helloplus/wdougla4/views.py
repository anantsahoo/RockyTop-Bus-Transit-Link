from flask import Blueprint, render_template, request, jsonify, redirect, url_for, render_template_string

views = Blueprint(__name__, "views")

@views.route("/")
def home():
    return render_template("index.html", name="Tim")

# this allows for ?= queries 
# formatted as such: localhost/views/profile/?name=bob
@views.route("/profile/")
def profile():
    args = request.args
    name = args.get('name')
    return render_template("index.html", name=name)

#redirects back to the home page with the use of a button.
@views.route("/go_to_home")
def go_to_home():
    return render_template("redirectHome.html")

#
# The following functions underneath have no functionality right now, 
# but may serve a purpose in the future.
#

# returns json
@views.route("/json")
def get_json():
    return jsonify({'name': 'tim', 'coolness': '10'})

# how to access json from a root
@views.route("/data")
def get_data():
    data = request.json
    return jsonify(data)
