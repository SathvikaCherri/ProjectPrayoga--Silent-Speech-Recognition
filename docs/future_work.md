# ProjectPrayoga — Future Work

ProjectPrayoga is currently a proof-of-concept system. Future development will focus on improving recognition performance, portability, usability, and scalability.

## 1. Expand the Vocabulary

The current prototype recognizes five phrases.

Future versions can expand the vocabulary to include a larger set of commonly used words and phrases, allowing the system to support more communication scenarios.

## 2. Increase the Dataset

More recordings can be collected for each phrase to improve the robustness of the machine-learning models.

The dataset can also be expanded to include recordings from multiple users.

## 3. Personalization

Silent articulation patterns can vary between individuals.

A future version could use a short calibration process to adapt the model to a specific user.

## 4. Improve Recognition Performance

Future work can explore:

* Improved signal preprocessing
* Additional temporal features
* Alternative machine-learning models
* Deep-learning approaches
* Better handling of variations between recordings

The goal is to improve recognition reliability while keeping the system practical for wearable use.

## 5. Additional Sensors

The current prototype uses one MPU6050 and one piezoelectric sensor.

Future hardware versions could investigate additional sensing locations or additional vibration and motion sensors to determine whether they provide useful complementary information.

## 6. Standalone Operation

The current development workflow relies on a computer for Python-based processing and model inference.

A major future goal is to move the inference pipeline directly onto the ESP32 so that the wearable can operate without a connected computer.

## 7. Portable Audio Output

The current prototype provides audible prediction output through computer-based text-to-speech.

A standalone version could use a compact audio output system so that recognized phrases can be communicated without requiring a laptop.

## 8. Wearable Design

Future hardware iterations can focus on:

* Smaller electronics
* Better sensor placement
* Improved comfort
* Secure sensor attachment
* Reduced wiring
* Portable power

The goal is to move from a development prototype toward a more practical wearable form factor.

## 9. Real-Time Continuous Recognition

The current system processes recordings as individual samples.

Future versions could investigate continuous recognition, allowing the system to detect and classify silently articulated phrases in real time.

## 10. Long-Term Goal

The long-term goal of ProjectPrayoga is to develop a compact wearable interface capable of translating silent articulation into useful communication.

The current prototype provides an initial platform for exploring this concept through low-cost sensing and machine learning.
