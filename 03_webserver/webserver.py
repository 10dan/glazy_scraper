from flask import Flask, request, jsonify, send_file
from tensorflow.keras.models import load_model
import numpy as np
import PIL.Image
import os

app = Flask(__name__)
script_dir = os.path.dirname(os.path.abspath(__file__))


# Load your trained model
model = load_model('trained_model.keras')

@app.route('/')
def index():
    index_path = os.path.join(script_dir, 'index.html')
    return open(index_path).read()

@app.route('/predict', methods=['POST'])
def predict():
    recipe_vector = np.array([request.json['recipe']])
    print(recipe_vector)
    predicted_image = model.predict(recipe_vector)[0]
    
    # Convert to PIL image and save
    predicted_image = (predicted_image * 255).astype('uint8')
    img = PIL.Image.fromarray(predicted_image, 'RGB')
    img.save("/tmp/predicted_image.jpg")
    
    return send_file("/tmp/predicted_image.jpg", mimetype='image/jpg')

if __name__ == '__main__':
    app.run(debug=True)
    print(script_dir)

# acab (not all)