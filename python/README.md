# ProjectPrayoga Python

This directory contains the Python scripts used for dataset recording, machine-learning training, and live learning in ProjectPrayoga.

## Scripts

### `record_dataset.py`

Used to collect sensor recordings from the ESP32 and save them as CSV files.

The recording process collects data from:

* MPU6050 accelerometer
* MPU6050 gyroscope
* Piezoelectric sensor

The recordings are organized according to the target phrase being recorded.

### `train_model.py`

Used to train and evaluate the machine-learning models.

The script:

* Loads the recorded sensor dataset
* Extracts features from each recording
* Generates a 153-feature representation
* Evaluates the SVM and Random Forest models
* Performs grouped cross-validation
* Trains the final models
* Saves the trained model files and feature information

The Random Forest model is currently used for live prediction.

### `live_learning.py`

Used for live phrase prediction and human-in-the-loop learning.

The script:

* Connects to the ESP32
* Records a new sensor sample
* Extracts the same features used during training
* Uses the trained Random Forest model to predict the phrase
* Provides audible feedback using text-to-speech
* Allows the user to confirm or correct the prediction
* Saves the new labeled recording
* Retrains the model using the updated dataset

## Machine-Learning Pipeline

The Python workflow consists of three main stages:

**Data Collection**

`record_dataset.py` collects and stores sensor recordings from the ESP32.

**Model Training**

`train_model.py` processes the recordings, extracts features, and trains the classification models.

**Live Learning**

`live_learning.py` uses the trained Random Forest model for prediction and allows new labeled recordings to be added to the dataset.

## Requirements

The Python scripts require Python 3 and the project's required Python packages.

Install the dependencies with:

```bash
pip install numpy pandas scikit-learn joblib pyserial pyttsx3 matplotlib
```

## Usage

### Collect Dataset

```bash
python record_dataset.py
```

### Train Models

```bash
python train_model.py
```

### Run Live Learning

```bash
python live_learning.py
```

The ESP32 should be connected and running the corresponding Arduino firmware before starting the recording or live-learning scripts.

## Development Status

The Python pipeline is currently part of the ProjectPrayoga prototype and is being actively developed alongside the hardware and machine-learning components.
