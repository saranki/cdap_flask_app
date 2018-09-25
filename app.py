from flask import Flask, request, render_template, json
from flask_cors import CORS, cross_origin
from flaskext.mysql import MySQL

from component.mysql.dbconnect import get_all_journey
from component.cdap_detection_model import split_video_to_image, extract_location, predict_road_signs, \
    display_prediction_details,remove_duplicates

app = Flask(__name__)
CORS(app)
mysql = MySQL()

# def connection():
app.config['MYSQL_DATABASE_USER'] = 'admin_018'
app.config['MYSQL_DATABASE_PASSWORD'] = 'admin_018'
app.config['MYSQL_DATABASE_DB'] = 'drive_assist_central_db'
app.config['MYSQL_DATABASE_HOST'] = 'drive-assist-central-db-mysql-instance.cf43lhxr9ub8.ap-south-1.rds.amazonaws.com'
mysql.init_app(app)

_conn = mysql.connect()


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
        cursor = _conn.cursor()
        cursor.execute("SELECT * from journey")
        data = cursor.fetchall()
        if data is None:
            return "No data"
        else:
            return render_template('summary.html', data=data)
    else:
        return json.dumps({'html': '<span>Enter the required fields</span>'})


def insert_journey(route_id, routeName):
    route = 'Malabe'
    cursor = _conn.cursor()
    # if route_name is None:
    #     route_name='New route'
    # value = cursor.execute("INSERT INTO journey (journey_id, route_name) VALUES('{}','{}')".format('j4','new route'))
    sql = 'INSERT INTO journey(journey_id, route_name) VALUES(%s, %s)'
    value = cursor.execute(sql, (route_id, routeName))
    _conn.commit()
    print('value', value)
    print('inserted')
    # mysql.close()
    return value


@app.route('/video-split', methods=['GET', 'POST'])
@cross_origin()
def split():
    if request.method == 'GET':
        return render_template('split.html')

    if request.method == 'POST':
        route = request.form['routeName']
        video = split_video_to_image()
        print(video)
        extract_location()
        predict_road_signs()
        remove_duplicates(video)

        cursor = _conn.cursor()
        cursor.execute("SELECT COUNT(journey_id) from journey")
        data = cursor.fetchone()

        count = data[0]
        route_id = 'j' + str(count + 1)
        print('route id', route_id)
        print('route name', route)
        res = insert_journey(route_id, route)

        if res == 1:
            print("Successfully added to Database")
        else:
            print("Unable to add details to the database")

        return 'OK'


@app.route('/check/<image_name>', methods=['POST'])
@cross_origin()
def check_individual(image_name):
    if request.method == 'POST':
        values = display_prediction_details(image_name)
        lat = values['lat']
        long = values['long']
        sign_name = values['sign_name']
        accuracy = values['accuracy']
        return json.dumps(values)


@app.route('/check')
@cross_origin()
def check():
    return render_template('check.html', amount="this is to check the value")


@app.route('/split_crossing', methods=['GET', 'POST'])
@cross_origin()
def split_crossing():
    if request.method == 'GET':
        return render_template('split_crossing.html')

    if request.method == 'POST':
        route = request.form['routeName']
        video = split_video_to_image()
        print(video)
        extract_location()
        predict_road_signs()
        remove_duplicates(video)

        cursor = _conn.cursor()
        cursor.execute("SELECT COUNT(journey_id) from journey")
        data = cursor.fetchone()

        count = data[0]
        route_id = 'j' + str(count + 1)
        print('route id', route_id)
        print('route name', route)
        res = insert_journey(route_id, route)

        if res == 1:
            print("Successfully added to Database")
        else:
            print("Unable to add details to the database")

        return 'OK'


@app.route('/summary')
@cross_origin()
def summary():
    return render_template('summary.html')


@app.route('/summary_crossing')
@cross_origin()
def summary_crossing():
    return render_template('summary_crossing.html')


# @app.route('/journey')
# @cross_origin()
# def get_journey_details():
#     cursor = _conn.cursor()
#     cursor.execute("SELECT * from journey")
#     data = cursor.fetchall()
#     if data is None:
#         return "No data"
#     else:
#         return render_template('summary.html', data=data)


if __name__ == '__main__':
    app.run(debug=True)
