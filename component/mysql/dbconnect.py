
def get_all_journey(mysql):
    cursor = mysql.connect().cursor()
    cursor.execute("SELECT * from journey")
    data = cursor.fetchall()