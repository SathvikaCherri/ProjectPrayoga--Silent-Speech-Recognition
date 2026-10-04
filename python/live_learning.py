import os
print("LIVE LEARNING WORKING DIRECTORY:", os.getcwd())
import pyttsx3
import sys
import glob
import time
import json
import subprocess

import numpy as np
import pandas as pd
import serial
import serial.tools.list_ports
import joblib

# IMPORTANT:
# Use the EXACT feature extractor from your training program.
from train_model import extract_features


# ============================================================
# CONFIGURATION
# ============================================================

BAUD_RATE = 115200
RECORDING_TIME = 3

DATASET_DIR = "silent_speech_dataset"
MODEL_DIR = "trained_models"

PHRASES = [
    "HELLO",
    "YES",
    "NO",
    "I_NEED_WATER",
    "I_NEED_HELP",
]

MODEL_FILE = os.path.join(
    MODEL_DIR,
    "random_forest_model.pkl"
)

FEATURE_NAMES_FILE = os.path.join(
    MODEL_DIR,
    "feature_names.json"
)

def speak_prediction(prediction):
    phrase_text = {
        "HELLO": "Hello",
        "YES": "Yes",
        "NO": "No",
        "I_NEED_WATER": "I need water",
        "I_NEED_HELP": "I need help"
    }

    text = phrase_text.get(prediction, prediction)

    print(f"🔊 Voice output: {text}")

    engine = pyttsx3.init()
    engine.setProperty("rate", 150)
    engine.setProperty("volume", 1.0)

    engine.say(text)
    engine.runAndWait()

# ============================================================
# SERIAL PORT
# ============================================================

def find_esp32_port():

    ports = list(serial.tools.list_ports.comports())

    if not ports:
        return None

    print()
    print("Available serial ports:")

    for i, port in enumerate(ports):
        print(f"  [{i}] {port.device} - {port.description}")

    # Try to automatically find ESP32-looking port
    for port in ports:

        description = (
            (port.description or "") +
            " " +
            (port.manufacturer or "")
        ).lower()

        if (
            "usb" in description
            or "cp210" in description
            or "ch340" in description
            or "silicon labs" in description
            or "esp32" in description
        ):
            print()
            print(f"Automatically selected: {port.device}")
            return port.device

    # Otherwise ask user
    choice = input(
        "\nEnter the port number to use: "
    ).strip()

    try:
        return ports[int(choice)].device
    except Exception:
        print("Invalid port.")
        return None


# ============================================================
# LOAD MODEL
# ============================================================

def load_model():

    if not os.path.exists(MODEL_FILE):
        raise FileNotFoundError(
            f"Model not found:\n{MODEL_FILE}\n\n"
            "Run train_model.py first."
        )

    if not os.path.exists(FEATURE_NAMES_FILE):
        raise FileNotFoundError(
            f"Feature names not found:\n{FEATURE_NAMES_FILE}"
        )

    model = joblib.load(MODEL_FILE)

    with open(FEATURE_NAMES_FILE, "r") as f:
        feature_names = json.load(f)

    return model, feature_names


# ============================================================
# RECORD ONE SAMPLE
# ============================================================

def record_sample(ser):

    print()
    print("Get ready...")
    time.sleep(0.7)

    print("3")
    time.sleep(1)

    print("2")
    time.sleep(1)

    print("1")
    time.sleep(1)

    print()
    print(">>> PERFORM THE PHRASE NOW <<<")
    print()

    # Clear anything old in the serial buffer
    ser.reset_input_buffer()

    # Tell ESP32 to record
    ser.write(b"START\n")

    rows = []

    recording_started = False

    while True:

        line = ser.readline().decode(
            "utf-8",
            errors="ignore"
        ).strip()

        if not line:
            continue

        if line == "RECORDING_START":

            recording_started = True
            continue

        if line == "RECORDING_END":

            break

        if not recording_started:
            continue

        # Ignore CSV header
        if line.startswith("time,"):
            continue

        parts = line.split(",")

        if len(parts) != 8:
            continue

        try:

            row = [
                float(x)
                for x in parts
            ]

            rows.append(row)

        except ValueError:
            continue

    if len(rows) < 100:

        raise RuntimeError(
            f"Only received {len(rows)} samples."
        )

    columns = [
        "time",
        "ax",
        "ay",
        "az",
        "gx",
        "gy",
        "gz",
        "piezo",
    ]

    df = pd.DataFrame(
        rows,
        columns=columns
    )

    return df


# ============================================================
# PREDICT
# ============================================================

def predict_sample(df, model, feature_names):

    features = extract_features(df)

    feature_df = pd.DataFrame(
        [features]
    )

    # Make absolutely sure the live features
    # have the same order as training.
    feature_df = feature_df.reindex(
        columns=feature_names
    )

    if feature_df.shape[1] != len(feature_names):

        raise RuntimeError(
            "Feature count mismatch."
        )

    if hasattr(model, "n_features_in_"):

        if model.n_features_in_ != feature_df.shape[1]:

            raise RuntimeError(
                f"Model expects "
                f"{model.n_features_in_} features, "
                f"but live data produced "
                f"{feature_df.shape[1]}."
            )

    prediction = model.predict(
        feature_df
    )[0]

    #aufdisjkafd idk gnggg

    print(f"Prediction: {prediction}")

    speak_prediction(prediction)

    probabilities = model.predict_proba(
        feature_df
    )[0]

    classes = model.classes_

    probability_dict = {
        str(label): float(prob)
        for label, prob in zip(
            classes,
            probabilities
        )
    }

    confidence = probability_dict[
        str(prediction)
    ]

    return (
        prediction,
        confidence,
        probability_dict
    )


# ============================================================
# GET NEXT RECORDING NUMBER
# ============================================================

def get_next_recording_number(phrase):

    phrase_dir = os.path.join(
        DATASET_DIR,
        phrase
    )

    os.makedirs(
        phrase_dir,
        exist_ok=True
    )

    files = glob.glob(
        os.path.join(
            phrase_dir,
            "recording_*.csv"
        )
    )

    numbers = []

    for filepath in files:

        filename = os.path.basename(
            filepath
        )

        try:

            number = int(
                filename
                .replace("recording_", "")
                .replace(".csv", "")
            )

            numbers.append(number)

        except ValueError:
            pass

    if not numbers:
        return 1

    return max(numbers) + 1


# ============================================================
# SAVE LEARNING SAMPLE
# ============================================================

def save_learning_sample(df, phrase):

    number = get_next_recording_number(
        phrase
    )

    filepath = os.path.join(
        DATASET_DIR,
        phrase,
        f"recording_{number:02d}.csv"
    )

    # train_model.py expects a "phrase" column.
    output_df = df.copy()

    # Put phrase first, matching your existing dataset style.
    output_df.insert(
        0,
        "phrase",
        phrase
    )

    output_df.to_csv(
        filepath,
        index=False
    )

    print()
    print("✓ New training example saved:")
    print(filepath)

    return filepath


# ============================================================
# RETRAIN
# ============================================================

def retrain_model():
    print("\nRunning train_model.py...")

    project_dir = os.path.dirname(os.path.abspath(__file__))
    train_script = os.path.join(project_dir, "train_model.py")

    result = subprocess.run(
        [sys.executable, train_script],
        cwd=project_dir,
        capture_output=False
    )

    if result.returncode != 0:
        print("\nERROR: Model retraining failed.")
        return False

    print("\nModel retraining completed successfully.")
    return True


# ============================================================
# DISPLAY PROBABILITIES
# ============================================================

def show_probabilities(probabilities):

    print()
    print("Model probabilities:")

    sorted_probs = sorted(
        probabilities.items(),
        key=lambda x: x[1],
        reverse=True
    )

    for phrase, probability in sorted_probs:

        print(
            f"  {phrase:16s} "
            f"{probability * 100:6.2f}%"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 60)
    print(" SILENT SPEECH - HUMAN IN THE LOOP")
    print("=" * 60)

    print()
    print("Loading model...")

    model, feature_names = load_model()

    print(
        f"Model loaded successfully."
    )

    print(
        f"Model features: {len(feature_names)}"
    )

    if len(feature_names) != 153:

        print(
            "WARNING: Expected 153 features "
            f"but found {len(feature_names)}."
        )

    port = find_esp32_port()

    if port is None:

        print("No serial port selected.")
        return

    print()
    print(
        f"Connecting to ESP32 on {port}..."
    )

    ser = serial.Serial(
        port,
        BAUD_RATE,
        timeout=1
    )

    # Give ESP32 time to reset
    time.sleep(2)

    ser.reset_input_buffer()

    print("✓ ESP32 connected.")

    print()
    print("=" * 60)
    print("HOW THIS WORKS")
    print("=" * 60)
    print()
    print("1. Press ENTER.")
    print("2. Countdown: 3, 2, 1.")
    print("3. Perform any phrase.")
    print("4. Model predicts it.")
    print("5. Tell the system whether it was correct.")
    print("6. The sample is added to the dataset.")
    print("7. The model retrains automatically.")
    print()
    print("Press CTRL+C to stop.")
    print()

    try:

        while True:

            input(
                "Press ENTER when you are ready..."
            )

            # ------------------------------------------------
            # RECORD
            # ------------------------------------------------

            try:

                df = record_sample(
                    ser
                )

            except Exception as e:

                print()
                print(
                    "Recording error:",
                    e
                )

                continue

            print(
                f"Received {len(df)} samples."
            )

            # ------------------------------------------------
            # PREDICT
            # ------------------------------------------------

            try:

                prediction, confidence, probabilities = (
                    predict_sample(
                        df,
                        model,
                        feature_names
                    )
                )

            except Exception as e:

                print()
                print(
                    "Prediction error:",
                    e
                )

                continue

            print()
            print("=" * 60)
            print("MODEL PREDICTION")
            print("=" * 60)

            print()
            print(
                f"Prediction: {prediction}"
            )

            print(
                f"Confidence: {confidence * 100:.1f}%"
            )

            show_probabilities(
                probabilities
            )

            # ------------------------------------------------
            # ASK USER
            # ------------------------------------------------

            print()
            print(
                "Was the prediction correct?"
            )

            print(
                "[Y] Yes"
            )

            print(
                "[N] No"
            )

            while True:

                answer = input(
                    "\nYour answer: "
                ).strip().upper()

                if answer in ["Y", "N"]:
                    break

                print(
                    "Please enter Y or N."
                )

            # ------------------------------------------------
            # CORRECT
            # ------------------------------------------------

            if answer == "Y":

                actual_phrase = prediction

                print()
                print(
                    f"✓ Confirmed: {actual_phrase}"
                )

            # ------------------------------------------------
            # INCORRECT
            # ------------------------------------------------

            else:

                print()
                print(
                    "What were you actually saying?"
                )

                for i, phrase in enumerate(
                    PHRASES,
                    start=1
                ):

                    print(
                        f"[{i}] {phrase}"
                    )

                while True:

                    choice = input(
                        "\nEnter 1-5: "
                    ).strip()

                    try:

                        choice = int(choice)

                        if 1 <= choice <= 5:
                            break

                    except ValueError:
                        pass

                    print(
                        "Please enter a number "
                        "from 1 to 5."
                    )

                actual_phrase = PHRASES[
                    choice - 1
                ]

                print()
                print(
                    f"✓ Correct label: "
                    f"{actual_phrase}"
                )

            # ------------------------------------------------
            # SAVE SAMPLE
            # ------------------------------------------------

            save_learning_sample(
                df,
                actual_phrase
            )

            # ------------------------------------------------
            # RETRAIN
            # ------------------------------------------------

            success = retrain_model()

            if success:

                # Load the newly trained model
                model, feature_names = (
                    load_model()
                )

                print()
                print(
                    "✓ New model loaded."
                )

            print()
            print("=" * 60)
            print("READY FOR NEXT ATTEMPT")
            print("=" * 60)
            print()

    except KeyboardInterrupt:

        print()
        print()
        print(
            "Stopping..."
        )

    finally:

        ser.close()

        print(
            "Serial connection closed."
        )


if __name__ == "__main__":
    main()