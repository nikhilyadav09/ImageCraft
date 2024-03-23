from flask import Flask, render_template, request
import cv2
import numpy as np
from base64 import b64decode, b64encode

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/apply_filter', methods=['POST'])
def apply_filter():
    image_data = request.form['image'].split(',')[1]
    image_bytes = b64decode(image_data.encode())
    image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
    filter_type = request.form['filter']

    if filter_type == 'grayscale':
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    elif filter_type == 'cropping':
        left = int(request.form['left'])
        top = int(request.form['top'])
        right = int(request.form['right'])
        bottom = int(request.form['bottom'])
        image = image[top:bottom, left:right]
    elif filter_type == 'rotating':
        angle = int(request.form['angle'])
        rows, cols = image.shape[:2]
        M = cv2.getRotationMatrix2D((cols / 2, rows / 2), angle, 1)
        image = cv2.warpAffine(image, M, (cols, rows))
    elif filter_type == 'blur':
        blur_radius = int(request.form['blur'])
        if blur_radius > 0:
            image = cv2.GaussianBlur(image, (blur_radius, blur_radius), 0)
    elif filter_type == 'contrast':
        contrast_value = float(request.form['contrast'])
        if contrast_value > 0:
            image = cv2.convertScaleAbs(image, alpha=contrast_value, beta=0)
    elif filter_type == 'sharpen':
        sharpen_value = float(request.form['sharpen'])
        if sharpen_value > 1:
            kernel = np.array([[0, -1, 0], [-1, sharpen_value, -1], [0, -1, 0]])
            image = cv2.filter2D(image, -1, kernel)
    else:
        return "Invalid filter type", 400

    success, image_buffer = cv2.imencode('.png', image)
    image_bytes = image_buffer.tobytes()
    encoded_image = b64encode(image_bytes).decode('utf-8')

    return encoded_image, 200, {'Content-Type': 'text/plain'}

if __name__ == '__main__':
    app.run(debug=True)