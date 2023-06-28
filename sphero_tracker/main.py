import cv2
# import numpy
from flask import Flask, render_template, Response, stream_with_context, Request, request

from tracker_filters import ColorFilter
from trackable_object import TrackableObject
from tracker import Tracker
from C920 import C920
import pdb
import json

app = Flask(__name__)

c920_control = C920("/dev/video0")

def video_stream():
    tracker = Tracker()

    sphero_test = TrackableObject("Sphero1")
    sphero_test.filter = ColorFilter((0,255,0))

    sphero_test1 = TrackableObject("Sphero2")
    sphero_test1.filter = ColorFilter((0,0,255))

    # sphero_test2 = TrackableObject("Sphero3")
    # sphero_test2.filter = ColorFilter((255,0,0))

    sphero_test3 = TrackableObject("Sphero3")
    sphero_test3.filter = ColorFilter((255,0,255))

    sphero_test4 = TrackableObject("Sphero4")
    sphero_test4.filter = ColorFilter((0,255,255))

    trackable_objects = [sphero_test, sphero_test1, sphero_test3, sphero_test4]

    while True:
        tracker.clear_masks()
        img = tracker.track_objects(trackable_objects)
        _, buffer = cv2.imencode('.jpeg',img)
        frame = buffer.tobytes()
        yield (b'--frame\r\n' b'Content-type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def siteTest():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(video_stream(), mimetype= 'multipart/x-mixed-replace; boundary = frame')

@app.route('/change_c920_param', methods=["POST"])
def change_c920_param():
    param = request.form['param']
    value = request.form['value']
    if param == 'auto_focus':
        if value == 0:
            c920_control.disable_auto_focus()
        else:
            c920_control.enable_auto_focus()
    elif param == "focus":
        c920_control.set_focus(int(value))
    elif param == "gain":
        c920_control.set_gain(int(value))
    return json.dumps({"status": True})

@app.route('/get_controls')
def get_controls():
    controls = c920_control.get_controls()
    return json.dumps(controls)


## EXAMPLE CODE
if __name__ == "__main__":
    app.run(host ='0.0.0.0', port= '5000', debug=True)

    