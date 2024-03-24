from flask import Flask, render_template, request
from PIL import Image, ImageFilter, ImageEnhance, ImageOps, ImageDraw
import io
import base64

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def apply_grayscale(image):
    return image.convert('L')

def apply_crop(image, left, top, right, bottom):
    width, height = image.size
    return image.crop((left, top, right, bottom))

def apply_rotate(image, angle):
    return image.rotate(angle, expand=True)

def apply_blur(image, radius):
    return image.filter(ImageFilter.GaussianBlur(radius=radius))

def apply_contrast(image, factor):
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(factor)

def apply_vignette(image, strength, start_color='black'):
    width, height = image.size
    center_x, center_y = width // 2, height // 2
    radius = min(center_x, center_y)

    # Create a circular mask
    vignette_mask = Image.new('L', (width, height), 0)
    draw = ImageDraw.Draw(vignette_mask)
    draw.ellipse((center_x - radius, center_y - radius, center_x + radius, center_y + radius), fill=255)

    # Invert the mask to create a ring
    vignette_mask = ImageOps.invert(vignette_mask)

    # Apply the vignette effect to the ring
    vignette_mask = ImageEnhance.Brightness(vignette_mask).enhance(strength / 255)

    # Create a new image with the starting color as the background
    if start_color == 'black':
        vignette_image = Image.new('RGB', image.size, 'black')
        end_color = 'white'
    else:
        vignette_image = Image.new('RGB', image.size, 'white')
        end_color = 'black'

    # Paste the original image inside the circle
    vignette_image.paste(image, (0, 0), mask=ImageOps.invert(vignette_mask))

    # Paste the vignette effect outside the circle
    vignette_image.paste(Image.new('RGB', image.size, end_color), (0, 0), mask=vignette_mask)

    return vignette_image

@app.route('/apply_filter', methods=['POST'])
def apply_filter():
    image_data = request.form['image'].split(',')[1]
    image_bytes = base64.b64decode(image_data.encode())
    image = Image.open(io.BytesIO(image_bytes))
    filter_type = request.form['filter']

    if filter_type == 'grayscale':
        image = apply_grayscale(image)
    elif filter_type == 'cropping':
        left = int(request.form['left'])
        top = int(request.form['top'])
        right = int(request.form['right'])
        bottom = int(request.form['bottom'])
        image = apply_crop(image, left, top, right, bottom)
    elif filter_type == 'rotating':
        angle = int(request.form['angle'])
        image = apply_rotate(image, angle)
    elif filter_type == 'blur':
        radius = float(request.form['blur'])
        image = apply_blur(image, radius)
    elif filter_type == 'contrast':
        factor = float(request.form['contrast'])
        image = apply_contrast(image, factor)
    elif filter_type == 'vignette':
        strength = int(request.form['vignette'])
        image = apply_vignette(image, strength)
    else:
        return "Invalid filter type", 400

    image_buffer = io.BytesIO()
    image.save(image_buffer, format='PNG')
    image_bytes = image_buffer.getvalue()
    encoded_image = base64.b64encode(image_bytes).decode('utf-8')
    return encoded_image, 200, {'Content-Type': 'text/plain'}

if __name__ == '__main__':
    app.run(debug=True)