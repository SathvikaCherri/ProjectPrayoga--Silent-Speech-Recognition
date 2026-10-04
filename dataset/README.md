# ProjectPrayoga Dataset

The ProjectPrayoga dataset contains sensor recordings collected from the wearable prototype during silent articulation.

## Target Phrases

The current dataset contains five target phrases:

* `HELLO`
* `YES`
* `NO`
* `I_NEED_WATER`
* `I_NEED_HELP`

## Sensors

Each recording contains data collected using:

* **MPU6050 accelerometer**
* **MPU6050 gyroscope**
* **Piezoelectric sensor**

The sensor signals are collected through an **ESP32**.

## Recording Details

* Recording duration: approximately **3 seconds**
* Sampling interval: approximately **10 ms**
* Multiple recordings were collected for each target phrase.
* Each recording is labeled according to the intended phrase.

## Dataset Usage

The dataset is used for:

* Feature extraction
* Machine-learning model training
* Model evaluation
* Live-learning experiments

The current dataset supports the five-phrase proof-of-concept system.

## Data Availability

The raw sensor recordings are currently stored locally and are not included in this public repository.

The dataset is intended for prototype development and experimentation and is not yet a large-scale or multi-user dataset.
