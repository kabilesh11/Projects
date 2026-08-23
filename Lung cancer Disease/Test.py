# Import necessary libraries
from tensorflow.keras.preprocessing import image
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model

# Define the image size used for training
IMAGE_SIZE = (350, 350)

# Function to load and preprocess an image for prediction
def load_and_preprocess_image(img_path, target_size):
    img = image.load_img(img_path, target_size=target_size)
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array /= 255.0  # Rescale the image like the training images
    return img_array

# Function to predict the class of an image
def predict_image_class(model, img_path, class_labels, target_size):
    img = load_and_preprocess_image(img_path, target_size)
    predictions = model.predict(img)
    predicted_class = np.argmax(predictions[0])
    predicted_label = class_labels[predicted_class]
    print(f"The image belongs to class: {predicted_label}")
    
    # Display the image with the predicted class
    plt.imshow(image.load_img(img_path, target_size=target_size))
    plt.title(f"Predicted: {predicted_label}")
    plt.axis('off')
    plt.show()

# Load the trained model
model = load_model('trained_lung_cancer_model.h5')

# Define the class labels (same as used in training)
class_labels = ['adenocarcinoma', 'large cell carcinoma', 'normal', 'squamous cell carcinoma']

# Test the model with different images
predict_image_class(model, 'dataset/train/normal/2.png', class_labels, IMAGE_SIZE)