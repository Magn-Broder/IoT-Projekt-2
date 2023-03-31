#!/home/magn3442/Project/IoT2 python
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io

from flask import Flask, render_template, send_file, make_response, request
app = Flask(__name__)

import sqlite3
conn=sqlite3.connect('../sensor_data.db', check_same_thread=False)
curs=conn.cursor()

# Modtag den nyeste data fra databasen 
def get_last_data():
	for row in curs.execute("SELECT * FROM MQ135_data ORDER BY timestamp DESC LIMIT 1"):
		time = row[0]
		ppm = row[1]
		print(time)
	#conn.close()
	return time, ppm

def get_hist_data (num_samples):
	curs.execute("SELECT * FROM MQ135_data ORDER BY timestamp DESC LIMIT "+str(num_samples))
	data = curs.fetchall()
	dates = []
	ppm = []

	for row in reversed(data):
		dates.append(row[0])
		ppm.append(row[1])
	
	return dates, ppm

def max_rows_table():
	for row in curs.execute("select COUNT(ppm) from  MQ135_data"):
		max_number_rows=row[0]
	return max_number_rows

# define and initialize global variables
global num_samples
num_samples = max_rows_table()
if (num_samples > 101):
	num_samples = 100

# main route
@app.route("/")
def index():
	time, ppm = get_last_data()
	templateData = {
	  	'time'  : time,
		'ppm'   : ppm,		
      	'num_samples'	: num_samples
	}
	return render_template('index.html', **templateData)

@app.route('/', methods=['POST'])
def my_form_post():
    global num_samples
    num_samples = int (request.form['num_samples'])
    num_max_samples = max_rows_table()
    if (num_samples > num_max_samples):
        num_samples = (num_max_samples-1)
    time, ppm = get_last_data()
    templateData = {
	  	'time'  : time,
      	'ppm'   : ppm,
      	'num_samples'	: num_samples
	}
    return render_template('index.html', **templateData)

@app.route('/plot/ppm')
def plot_ppm():
	time, ppms = get_hist_data(num_samples)
	ys = ppms
	fig = Figure()
	axis = fig.add_subplot(1, 1, 1)
	axis.set_title("CO2 [PPM]")
	axis.set_xlabel("Samples")
	axis.grid(True)
	xs = range(num_samples)
	axis.plot(xs, ys)
	canvas = FigureCanvas(fig)
	output = io.BytesIO()
	canvas.print_png(output)
	response = make_response(output.getvalue())
	response.mimetype = 'image/png'
	return response

if __name__ == "__main__":
   app.run(host='0.0.0.0', port=80, debug=False)
