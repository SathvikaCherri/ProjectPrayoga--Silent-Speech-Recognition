# ProjectPrayoga--Silent-Speech-Recognition
# SilentSpeak

### Wearable Silent Speech Recognition Using IMU and Piezoelectric Sensing

SilentSpeak is a wearable silent-speech recognition prototype designed to recognize a small set of intended phrases from subtle jaw and facial movements and mechanical vibrations produced during silent articulation.

The current prototype uses an **ESP32**, **MPU6050 IMU**, and **piezoelectric sensor** to capture motion and vibration signals. These signals are processed using machine-learning techniques to classify the user's intended phrase.

> **Current prototype phrases:**
> `HELLO` · `YES` · `NO` · `I NEED WATER` · `I NEED HELP`

---

## Prototype

<p align="center">
  <img src="hardware/images/hardware_setup.jpg" width="700">
</p>

*Current SilentSpeak hardware prototype.*

The prototype consists of an ESP32 connected to an MPU6050 motion sensor and a piezoelectric sensor positioned near the jaw/face region.

---

## Motivation

People who cannot rely on conventional speech may benefit from alternative communication interfaces that do not require audible vocalization.

SilentSpeak explores whether subtle physical signals generated during silent articulation can be captured using wearable sensors and translated into recognizable commands.

The goal of the project is to investigate a compact, low-cost sensing system that could eventually support silent communication through wearable hardware.

---

## How It Works

SilentSpeak captures subtle motion and mechanical vibrations produced during silent articulation using an **MPU6050 IMU** and a **piezoelectric sensor**.

The ESP32 collects the sensor signals, which are then processed into statistical and temporal features. These features are passed to a machine-learning classifier to identify the intended phrase.

The current system focuses on a limited vocabulary of five phrases as a proof-of-concept.

---

## Hardware

| Component                     | Purpose                                                     |
| ----------------------------- | ----------------------------------------------------------- |
| ESP32                         | Main microcontroller and sensor interface                   |
| MPU6050                       | Measures acceleration and angular motion                    |
| Piezoelectric sensor          | Captures mechanical vibrations associated with articulation |
| Piezo bias/protection circuit | Conditions the piezo signal for analog measurement          |
| Power source                  | Provides portable power for future standalone operation     |

### Current Sensor Connections

#### MPU6050

| MPU6050 | ESP32   |
| ------- | ------- |
| VCC     | 3.3V    |
| GND     | GND     |
| SDA     | GPIO 21 |
| SCL     | GPIO 22 |

#### Piezoelectric Sensor

| Piezo circuit | ESP32   |
| ------------- | ------- |
| Analog output | GPIO 34 |
| Ground        | GND     |

GPIO 34 is used as the analog input for the piezoelectric sensor.

---

## Sensors

### MPU6050

The MPU6050 provides:

* Accelerometer readings: `Ax`, `Ay`, `Az`
* Gyroscope readings: `Gx`, `Gy`, `Gz`

These measurements capture small changes in head and jaw-related movement during silent articulation.

### Piezoelectric Sensor

The piezoelectric sensor captures mechanical vibrations generated around the jaw/face region.

The sensor signal is biased and conditioned before being connected to the ESP32 analog input.

Using both motion and vibration information provides complementary sensing modalities for the recognition task.

---

## Machine Learning

The current Python pipeline extracts **153 features** from each recorded sensor sample.

The feature set includes statistical and temporal characteristics derived from:

* Piezoelectric signal
* Accelerometer channels
* Gyroscope channels
* Acceleration magnitude
* Gyroscope magnitude
* Temporal sections of selected signals

Two classifiers are currently evaluated:

* Support Vector Machine (SVM)
* Random Forest

The Random Forest model is currently used for live prediction.

---

## Dataset

The dataset contains recordings for five target phrases:

| Phrase       | Label          |
| ------------ | -------------- |
| Hello        | `HELLO`        |
| Yes          | `YES`          |
| No           | `NO`           |
| I need water | `I_NEED_WATER` |
| I need help  | `I_NEED_HELP`  |

Each recording contains approximately **3 seconds of sensor data** sampled at approximately **10 ms intervals**.

The dataset is organized by phrase:

```text
silent_speech_dataset/
├── HELLO/
├── YES/
├── NO/
├── I_NEED_WATER/
└── I_NEED_HELP/
```

The dataset is currently being used for experimentation and model development rather than as a final benchmark dataset.

---

## Live Learning

SilentSpeak includes a human-in-the-loop learning workflow.

During live operation:

1. The system records a new sensor sample.
2. The trained model predicts the intended phrase.
3. The predicted phrase is displayed and spoken through the computer.
4. The user confirms whether the prediction is correct.
5. If the prediction is incorrect, the user selects the correct phrase.
6. The new labeled recording is added to the dataset.
7. The model is retrained using the updated dataset.
8. The updated model is loaded for subsequent predictions.

This allows the prototype to gradually incorporate additional user-specific recordings.

---

## Live Prediction

The current live-learning application provides audible feedback using text-to-speech.

For example, when the model predicts:

> `I NEED WATER`

the system produces the corresponding spoken output:

> **"I need water."**

This allows the prototype to demonstrate the complete sensing → classification → output pipeline.

---

## Project Structure

```text
SilentSpeak/
│
├── README.md
│
├── arduino/
│   ├── sensor_test/
│   ├── dataset_recording/
│   └── live_inference/
│
├── python/
│   ├── train_model.py
│   ├── live_learning.py
│   ├── record_dataset.py
│   └── README.md
│
├── hardware/
│   ├── README.md
│   ├── wiring.md
│   └── images/
│
├── dataset/
│   └── README.md
│
├── models/
│   └── README.md
│
├── results/
│   └── README.md
│
└── docs/
    ├── project_overview.md
    ├── methodology.md
    └── future_work.md
```

---

## Software Setup

### Requirements

* Python 3.x
* Arduino IDE
* ESP32 board support
* ESP32 USB drivers
* Required Python packages

Install the Python dependencies with:

```bash
pip install numpy pandas scikit-learn joblib pyserial pyttsx3 matplotlib
```

---

## Training the Model

Place the dataset in the configured dataset directory and run:

```bash
python train_model.py
```

The training pipeline:

* Loads the sensor recordings
* Extracts features
* Performs grouped cross-validation
* Evaluates the SVM and Random Forest models
* Trains the final models
* Saves the trained model and feature information

The trained models are stored in the configured model directory.

---

## Running Live Learning

Connect the ESP32 to the computer and make sure the required Arduino firmware is running.

Then run:

```bash
python live_learning.py
```

The application will:

* Detect the ESP32 serial connection
* Record a sensor sample
* Extract the required features
* Predict the phrase
* Report the confidence
* Provide audible output
* Ask the user to confirm the prediction
* Save confirmed/corrected recordings
* Retrain the model

---

## Current Prototype Status

The current prototype demonstrates:

* ESP32-based sensor acquisition
* MPU6050 motion sensing
* Piezoelectric vibration sensing
* Automated dataset recording
* Feature extraction
* Machine-learning classification
* Live phrase prediction
* Human-in-the-loop dataset expansion
* Automatic model retraining
* Audible prediction output

The system is currently a **proof-of-concept research prototype** and is not yet intended as a production communication device.

---

## Current Limitations

The current prototype has several limitations:

* The vocabulary is limited to five phrases.
* The system requires calibration and consistent sensor placement.
* Sensor signals vary between recordings and users.
* The current implementation relies on a computer for Python-based inference and speech output.
* The dataset is still relatively small for a general-purpose silent-speech system.
* Recognition performance may vary with sensor placement, movement, and articulation style.

---

## Future Development

Future versions of SilentSpeak could explore:

* Larger phrase vocabularies
* More training data and additional users
* Personalized calibration
* Improved signal processing
* More advanced machine-learning models
* Multiple piezoelectric sensing locations
* Additional IMU or vibration sensors
* Fully standalone ESP32 inference
* Portable audio output
* Smaller and more ergonomic wearable hardware
* Real-time continuous recognition
* Integration with assistive communication interfaces

---

## Project Vision

The long-term goal of SilentSpeak is to explore a wearable interface capable of converting silent articulation into useful communication without requiring audible speech.

The current prototype is an early step toward that goal, focusing on the feasibility of combining low-cost motion and vibration sensing with machine learning.

---

## Status

**Prototype Stage — Active Development**

The current system is functional as a research and demonstration prototype. Hardware, sensing methods, dataset quality, and machine-learning performance are still being improved.

---

## Author

**Sathvika**

Developed as a wearable silent-speech recognition prototype for hackathon and research exploration.

---

## Disclaimer

SilentSpeak is an experimental prototype developed for research, demonstration, and educational purposes. It should not be considered a medical device or a replacement for established assistive communication technologies.
