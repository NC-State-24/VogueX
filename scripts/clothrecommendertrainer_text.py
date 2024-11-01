# VogueX
# Copyright (c) 2024 Group 84: Gokul Prakash Ramesh, Haricharan Bharathi, Raghunandan Ganesh Mante
# This project is licensed under the MIT License.
# #
# Governance Model:
# This project follows an open governance model, which includes a leadership team,
# contribution guidelines, a code of conduct, and a clear decision-making process.
# Contributions are welcome, and please see CONTRIBUTING.md for details.

# -*- coding: utf-8 -*-
"""ClothRecommenderTrainer.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1eJhmlkEFEwwN3cq8ufpvheKyhmiroIta
"""

import kagglehub
import os
import shutil

# Create a directory in the Colab runtime
preferred_path = "/content/fashion-product-images-dataset"
os.makedirs(preferred_path, exist_ok=True)

# Download the dataset from Kaggle
path = kagglehub.dataset_download("paramaggarwal/fashion-product-images-dataset")

# Move the downloaded dataset to your preferred path
shutil.move(path, preferred_path)

print("Dataset saved to:", preferred_path)

import os
import pathlib
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# Define the path to the dataset
path = "/content/fashion-product-images-dataset/1/fashion-dataset"
dataset_path = pathlib.Path(path)

# List all files in the dataset directory
images = os.listdir(dataset_path / "images")

# Display the list of image files (first 10 for verification)
print(images[:10])

# Plot the images
plt.figure(figsize=(20, 20))
for i in range(10, 20):
    # Make sure to use the correct path for the image files
    cloth_img_path = dataset_path / "images" / images[i]  # Change this line
    cloth_img = mpimg.imread(cloth_img_path)
    plt.subplot(6, 10, i - 10 + 1)
    plt.imshow(cloth_img)
    plt.axis("off")
plt.subplots_adjust(wspace=-0.5, hspace=1)
plt.show()

import pandas as pd

# Define the path to the CSV file
csv_path = "/content/fashion-product-images-dataset/1/fashion-dataset/styles.csv"  # Update the path

# Read the CSV file, skipping bad lines
df = pd.read_csv(csv_path, nrows=6000, on_bad_lines="skip")

# Add a column for the image filenames
df["image"] = df.apply(lambda x: str(x["id"]) + ".jpg", axis=1)

# Drop the 'year' column if it exists
if "year" in df.columns:
    df = df.drop(columns=["year"])

# Reset the index
df = df.reset_index(drop=True)

# Print the shape of the dataframe
print(df.shape)

# Display the first 5 rows of the dataframe
df.head(5)

from sklearn.preprocessing import LabelEncoder

embedding_dim = 8

# Keep only relevant columns for encoding
features_to_encode = [
    "gender",
    "masterCategory",
    "subCategory",
    "articleType",
    "baseColour",
    "season",
    "usage",
]

# Label Encoding
label_encoders = {}
encoded_data = {}
for col in features_to_encode:
    le = LabelEncoder()
    encoded_data[col] = le.fit_transform(df[col])
    label_encoders[col] = le


class FeatureExtractor(tf.keras.Model):
    def __init__(self, feature_vocab_sizes, embedding_dim):
        super(FeatureExtractor, self).__init__()
        self.embeddings = {
            feature: tf.keras.layers.Embedding(
                input_dim=vocab_size, output_dim=embedding_dim
            )
            for feature, vocab_size in feature_vocab_sizes.items()
        }

    def call(self, inputs):
        embedded = [
            self.embeddings[feature](tf.convert_to_tensor(inputs[feature]))
            for feature in inputs
        ]
        concatenated = tf.concat(embedded, axis=1)
        return concatenated


feature_vocab_sizes = {col: len(label_encoders[col].classes_) for col in label_encoders}

model = FeatureExtractor(feature_vocab_sizes, embedding_dim)
model.build(input_shape={feature: (None,) for feature in feature_vocab_sizes})

encoded_inputs = {col: tf.constant(encoded_data[col]) for col in label_encoders}
dataset_features = model(encoded_inputs).numpy()

import pandas as pd
import numpy as np


def find_similar_items(input_values, top_n=5):
    # Encode input values
    encoded_input = {
        col: tf.constant([label_encoders[col].transform([input_values[col]])[0]])
        for col in input_values
    }
    input_features = model(encoded_input).numpy()

    # Compute cosine similarity
    similarities = cosine_similarity(input_features, dataset_features)
    indices = np.argsort(similarities[0])[::-1][:top_n]
    return df.iloc[indices]


import joblib
import os

# Define a directory to save the model and encoders
model_save_dir = "model_directory"
os.makedirs(model_save_dir, exist_ok=True)

# Save the model architecture and weights as a .h5 file
model.save(os.path.join(model_save_dir, "text_feature_extractor.h5"))

# Save the model as a .pkl file using joblib
joblib.dump(model, os.path.join(model_save_dir, "text_feature_extractor.pkl"))

# Save the label encoders
for col, le in label_encoders.items():
    joblib.dump(le, os.path.join(model_save_dir, f"{col}_label_encoder.pkl"))

from sklearn.metrics.pairwise import cosine_similarity

input_values = {
    "gender": "Men",
    "masterCategory": "Apparel",
    "subCategory": "Topwear",
    "articleType": "Shirts",
    "baseColour": "Navy Blue",
    "season": "Fall",
    "usage": "Casual",
}

# Find and display similar items
similar_items = find_similar_items(input_values, top_n=5)
print(similar_items[["productDisplayName", "image"]])
