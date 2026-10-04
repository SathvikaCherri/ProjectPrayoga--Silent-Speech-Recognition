# ProjectPrayoga — Project Overview

## Introduction

ProjectPrayoga is a wearable silent-speech recognition prototype that explores the use of low-cost sensors and machine learning to recognize intended phrases without requiring audible speech.

The system captures subtle physical signals produced during silent articulation and uses those signals to identify the user's intended phrase.

## Problem

Conventional speech-based communication depends on audible vocalization. ProjectPrayoga explores an alternative approach in which subtle movements and mechanical vibrations associated with silent articulation can be sensed and translated into recognizable phrases.

The project aims to investigate whether a combination of motion and vibration sensing can provide a practical foundation for silent communication.

## Current Prototype

The current prototype uses:

* ESP32 as the main microcontroller
* MPU6050 IMU for motion sensing
* Piezoelectric sensor for mechanical vibration sensing
* Machine-learning models for phrase classification

The prototype currently recognizes five phrases:

* `HELLO`
* `YES`
* `NO`
* `I_NEED_WATER`
* `I_NEED_HELP`

## System Concept

The MPU6050 captures acceleration and angular motion, while the piezoelectric sensor captures mechanical vibrations associated with articulation.

The ESP32 collects these sensor signals. The recorded data is then processed using a Python-based machine-learning pipeline.

Statistical and temporal characteristics are extracted from the sensor signals and used as input features for classification.

## Machine Learning

The current feature extraction pipeline produces **153 features** from each recording.

Two machine-learning approaches are evaluated:

* Support Vector Machine (SVM)
* Random Forest

The Random Forest model is currently used for live prediction.

## Dataset

The dataset consists of approximately three-second recordings collected for each target phrase.

Recordings contain data from the MPU6050 accelerometer, MPU6050 gyroscope, and piezoelectric sensor.

The dataset is currently intended for prototype development and experimentation rather than large-scale or multi-user deployment.

## Live Learning

ProjectPrayoga also includes a human-in-the-loop learning workflow.

A new sensor recording is classified by the trained model. The user can confirm the prediction or provide the correct phrase. The new labeled recording is then added to the dataset and the model can be retrained.

This provides a way to incrementally collect user-specific data during development.

## Current Stage

ProjectPrayoga is currently an experimental proof-of-concept prototype.

The project demonstrates the feasibility of combining wearable motion and vibration sensing with machine learning for a limited silent-speech vocabulary.
