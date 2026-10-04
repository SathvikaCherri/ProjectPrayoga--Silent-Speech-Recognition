# ProjectPrayoga — Methodology

## 1. Hardware and Data Acquisition

ProjectPrayoga uses an ESP32 to collect data from two sensing modalities:

* MPU6050 IMU
* Piezoelectric sensor

The MPU6050 provides accelerometer and gyroscope measurements.

The piezoelectric sensor is used to capture mechanical vibrations associated with silent articulation.

## 2. Sensor Configuration

The MPU6050 communicates with the ESP32 using I2C.

The current connections are:

* SDA → GPIO 21
* SCL → GPIO 22
* VCC → 3.3V
* GND → GND

The conditioned piezoelectric signal is connected to an ESP32 analog input.

The current prototype uses GPIO 34 for the piezoelectric analog signal.

## 3. Data Collection

Each recording is approximately **3 seconds** long.

Sensor samples are collected at approximately **10 ms intervals**.

The dataset currently contains recordings corresponding to five target phrases:

* `HELLO`
* `YES`
* `NO`
* `I_NEED_WATER`
* `I_NEED_HELP`

The recording process is designed to maintain consistent sensor placement and recording conditions.

## 4. Recorded Signals

The collected data includes:

* Piezoelectric signal
* X, Y, and Z accelerometer measurements
* X, Y, and Z gyroscope measurements

Additional magnitude signals are calculated during feature extraction.

## 5. Feature Extraction

The Python training pipeline converts each recording into a fixed-length feature vector.

Statistical features include:

* Mean
* Standard deviation
* Minimum
* Maximum
* Range
* Root mean square
* Energy
* Difference-based statistics
* Percentiles

Additional features are calculated from:

* Individual accelerometer channels
* Individual gyroscope channels
* Piezoelectric signal
* Acceleration magnitude
* Gyroscope magnitude

Temporal features are also calculated by dividing selected signals into sections and calculating statistics for each section.

The current feature extraction pipeline produces **153 features per recording**.

## 6. Machine-Learning Models

Two classification approaches are currently evaluated.

### Support Vector Machine

The SVM implementation uses feature standardization followed by an RBF-kernel classifier.

### Random Forest

The Random Forest classifier is trained using the extracted sensor features.

The current implementation uses multiple decision trees and class balancing.

The Random Forest model is currently used by the live-learning application for phrase prediction.

## 7. Model Evaluation

The training pipeline uses grouped cross-validation based on recording groups.

This helps evaluate how consistently the extracted features distinguish between the target phrases while keeping recordings from the same group together during validation.

The evaluation results are used during development to compare the SVM and Random Forest approaches.

## 8. Live Prediction

During live operation, the ESP32 records a new sensor sample.

The Python application processes the recording using the same feature-extraction pipeline used during training.

The resulting 153-feature vector is passed to the trained Random Forest model.

The predicted class is then converted into the corresponding phrase.

## 9. Human-in-the-Loop Learning

After a prediction is produced, the user can confirm whether it is correct.

If the prediction is incorrect, the user selects the intended phrase.

The new recording is saved with the corrected label and added to the training dataset.

The training pipeline can then be executed again to update the model using the expanded dataset.

## 10. Current Methodology

The current methodology is intended as a proof-of-concept approach.

The system focuses on demonstrating that motion and vibration signals can provide useful information for distinguishing a small set of silently articulated phrases.

Further experimentation is required to determine how well the approach generalizes across different users, sensor placements, and articulation patterns.
