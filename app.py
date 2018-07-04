import os

from flask import Flask, request, render_template, json, redirect, url_for
from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin

from component.signboard import split_video_to_image, extract_location, predict_road_signs, display_prediction_details

app = Flask(__name__)
CORS(app)


@app.route('/')
@app.route('/login')
@cross_origin()
def login():
    return render_template('login.html')


@app.route('/home', methods=['POST'])
@cross_origin()
def signup():
    username = request.form['username']
    password = request.form['pass']

    if username == 'admin' and password == 'admin':
        return render_template('home.html')
        # return render_template('home.html')
    else:
        return json.dumps({'html': '<span>Enter the required fields</span>'})


@app.route('/video-split', methods=['GET', 'POST'])
@cross_origin()
def split():
    if request.method == 'GET':
        return render_template('split.html')

    if request.method == 'POST':
        split_video_to_image()
        extract_location()
        predict_road_signs()
        # TODO: eliminate_duplicates()
        # TODO: save_to_database()
        return 'OK'


@app.route('/check/<image_name>', methods=['POST'])
@cross_origin()
def check_individual(image_name):
    if request.method == 'POST':
        # print("CALLED !!!!!!!!!!!!!!!!!!!!!!")
        values = display_prediction_details(image_name)
        # print("predicted !!!!!!!!!!!!!!!!!!!!!!", values)
        # values = json.dumps(values)
        # print("lat", values[0])
        # print("long", values[1])
        # print("sign_name", values[2])
        # print("accuracy", values[3])
        # res = '12312312312312312'
        lat = values['lat']
        long = values['long']
        sign_name = values['sign_name']
        accuracy = values['accuracy']
        return json.dumps(values)
        # return render_template('check.html', lat=lat, long=long, sign_name=sign_name, accuracy=accuracy)


@app.route('/check')
@cross_origin()
def check():
    return render_template('check.html', amount="this is to check the value")


@app.route('/summary')
@cross_origin()
def summary():
    return render_template('summary.html')


if __name__ == '__main__':
    app.run(debug=True)
