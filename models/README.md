# ProjectPrayoga Models

This directory documents the machine-learning models used by ProjectPrayoga for silent-speech phrase classification.

## Models

ProjectPrayoga currently evaluates two machine-learning models:

* **Support Vector Machine (SVM)**
* **Random Forest**

Both models are trained using features extracted from the sensor recordings.

## Input Features

The current feature-extraction pipeline produces **153 features** from each recording.

The features are derived from:

* Piezoelectric sensor data
* Accelerometer data
* Gyroscope data
* Acceleration magnitude
* Gyroscope magnitude
* Temporal characteristics of selected signals

These features are used as the input to the classification models.

## Random Forest

The Random Forest model is currently used for live prediction in the ProjectPrayoga prototype.

It predicts one of the five target phrases:

* `HELLO`
* `YES`
* `NO`
* `I_NEED_WATER`
* `I_NEED_HELP`

The model also provides prediction probabilities that are used to estimate the confidence of a prediction.

## Support Vector Machine

An SVM model is also trained and evaluated as an alternative classification approach.

The current implementation uses an RBF kernel with feature standardization.

The SVM is primarily used for model comparison and experimentation.

## Model Training

The models are trained using the sensor dataset and the feature-extraction pipeline implemented in `train_model.py`.

The training process:

1. Loads the sensor recordings.
2. Extracts the 153 features.
3. Evaluates the classification models using grouped cross-validation.
4. Trains the final models using the available recordings.
5. Saves the trained model files and feature information.

## Model Files

The trained model files are generated locally during training.

They are currently not included in this public repository because the trained model files are excluded through `.gitignore`.

The main generated files are:

* `random_forest_model.pkl`
* `svm_model.pkl`
* `feature_names.json`

## Current Status

The models are part of an experimental prototype and are still being improved.

Model performance may vary depending on:

* User
* Sensor placement
* Recording conditions
* Amount of training data
* Silent articulation patterns

Future versions may explore additional models and more advanced approaches as the dataset grows.
