from flask import Flask, render_template, request
from PIL import Image, ImageFilter, ImageEnhance, ImageOps, ImageDraw
import io
import base64

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')  # Render the index.html template when accessing the root route

# Function to apply grayscale filter to an image
def apply_grayscale(image):
    return image.convert('L')

# Function to apply cropping to an image
def apply_crop(image, left, top, right, bottom):
    width, height = image.size
    return image.crop((left, top, right, bottom))

# Function to apply rotation to an image
def apply_rotate(image, angle):
    return image.rotate(angle, expand=True)

# Function to apply Gaussian blur to an image
def apply_blur(image, radius):
    return image.filter(ImageFilter.GaussianBlur(radius=radius))

# Function to apply contrast enhancement to an image
def apply_contrast(image, factor):
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(factor)

# Function to apply vignette effect to an image
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

# Route to apply image filter
@app.route('/apply_filter', methods=['POST'])
def apply_filter():
    # Get the base64-encoded image data from the form
    image_data = request.form['image'].split(',')[1]
    # Decode the base64 data into bytes
    image_bytes = base64.b64decode(image_data.encode())
    # Open the image using PIL
    image = Image.open(io.BytesIO(image_bytes))
    # Get the type of filter to apply
    filter_type = request.form['filter']

    # Apply the selected filter based on the filter type
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

    # Convert the processed image back to base64-encoded string
    image_buffer = io.BytesIO()
    image.save(image_buffer, format='PNG')
    image_bytes = image_buffer.getvalue()
    encoded_image = base64.b64encode(image_bytes).decode('utf-8')
    # Return the base64-encoded image string as the response
    return encoded_image, 200, {'Content-Type': 'text/plain'}

if __name__ == '__main__':
    app.run(debug=True)  # Run the Flask application in debug mode if executed as main script
