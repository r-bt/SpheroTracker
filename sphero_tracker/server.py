from C920 import C920
from flask import Flask, render_template, Response, request
import json
import cv2

app = Flask(__name__)

c920_control = C920("/dev/video0")

callback = None

def video_stream():
    global callback
    while True:
        if callback is None:
            raise RuntimeError("Callback not set. Please run set_callback(cb) before running video_stream()")
        frame = callback()

        cv2.imwrite("images/frame.jpg", frame)

        if frame is None:
            print("Frame is none!")
            continue
        
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(frame) + b'\r\n')
   
@app.route('/')
def siteTest():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(video_stream(), mimetype= 'multipart/x-mixed-replace; boundary=frame')

@app.route('/change_c920_param', methods=["POST"])
def change_c920_param():
    param = request.json['param']
    value = int(request.json['value'])
    if param == 'auto_focus':
        print("value is")
        print(value)
        if value:
            c920_control.enable_auto_focus()
        else:
            print("disabling autofocus")
            c920_control.disable_auto_focus()
    elif param == "focus":
        c920_control.set_focus(value)
    elif param == "gain":
        c920_control.set_gain(value)
    elif param == 'brightness':
        c920_control.set_brightness(value)
    elif param == 'zoom_absolute':
        c920_control.set_zoom(value)
    elif param == 'contrast':
        c920_control.set_contrast(value)
    elif param == 'saturation':
        c920_control.set_saturation(value)
    elif param == 'sharpness':
        c920_control.set_sharpness(value)
    return json.dumps({"status": True})

@app.route('/get_controls')
def get_controls():
    controls = c920_control.get_controls()
    return json.dumps(controls)

def set_callback(cb):
    global callback
    callback = cb

def start_server():
    app.run(host ='0.0.0.0', port= '5000', debug=True, use_reloader=False)