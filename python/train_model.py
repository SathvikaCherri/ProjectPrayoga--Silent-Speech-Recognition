import os
import glob
import json

import numpy as np
import pandas as pd
import joblib
import matplotlib.pyplot as plt

from sklearn.model_selection import GroupKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    classification_report,
    ConfusionMatrixDisplay,
)


# ============================================================
# CONFIGURATION
# ============================================================

DATASET_DIR = r"C:\Users\cheri\AppData\Local\Programs\Microsoft VS Code\silent_speech_dataset"
MODEL_DIR = r"C:\Users\cheri\AppData\Local\Programs\Microsoft VS Code\trained_models"

PHRASES = [
    "HELLO",
    "YES",
    "NO",
    "I_NEED_WATER",
    "I_NEED_HELP",
]


# ============================================================
# FEATURE EXTRACTION
# ============================================================

def add_signal_features(features, signal, prefix):
    """
    Extract statistical features from one sensor signal.
    """

    signal = np.asarray(signal, dtype=float)

    if len(signal) == 0:
        return

    diff = np.diff(signal)

    features[f"{prefix}_mean"] = np.mean(signal)
    features[f"{prefix}_std"] = np.std(signal)
    features[f"{prefix}_min"] = np.min(signal)
    features[f"{prefix}_max"] = np.max(signal)
    features[f"{prefix}_range"] = np.ptp(signal)

    # RMS
    features[f"{prefix}_rms"] = np.sqrt(
        np.mean(signal ** 2)
    )

    # Energy
    features[f"{prefix}_energy"] = np.mean(signal ** 2)

    # Signal change
    if len(diff) > 0:
        features[f"{prefix}_diff_std"] = np.std(diff)
        features[f"{prefix}_diff_abs_mean"] = np.mean(
            np.abs(diff)
        )
    else:
        features[f"{prefix}_diff_std"] = 0
        features[f"{prefix}_diff_abs_mean"] = 0

    # Percentiles
    percentiles = [10, 25, 50, 75, 90]

    values = np.percentile(signal, percentiles)

    for p, value in zip(percentiles, values):
        features[f"{prefix}_q{p}"] = value


def extract_features(df):
    """
    Extract features from one complete recording.
    """

    features = {}

    # --------------------------------------------------------
    # Derived MPU6050 signals
    # --------------------------------------------------------

    acceleration_magnitude = np.sqrt(
        df["ax"] ** 2 +
        df["ay"] ** 2 +
        df["az"] ** 2
    ).to_numpy()

    gyro_magnitude = np.sqrt(
        df["gx"] ** 2 +
        df["gy"] ** 2 +
        df["gz"] ** 2
    ).to_numpy()

    # --------------------------------------------------------
    # Individual sensor channels
    # --------------------------------------------------------

    sensor_columns = [
        "piezo",
        "ax",
        "ay",
        "az",
        "gx",
        "gy",
        "gz",
    ]

    for column in sensor_columns:

        add_signal_features(
            features,
            df[column].to_numpy(),
            column
        )

    # --------------------------------------------------------
    # Magnitudes
    # --------------------------------------------------------

    add_signal_features(
        features,
        acceleration_magnitude,
        "acc_mag"
    )

    add_signal_features(
        features,
        gyro_magnitude,
        "gyro_mag"
    )

    # --------------------------------------------------------
    # Temporal features
    #
    # Divide each recording into 3 sections:
    #
    # beginning | middle | end
    # --------------------------------------------------------

    temporal_signals = {
        "piezo": df["piezo"].to_numpy(),
        "acc_mag": acceleration_magnitude,
        "gyro_mag": gyro_magnitude,
    }

    for name, signal in temporal_signals.items():

        n = len(signal)

        for section in range(3):

            start = section * n // 3
            end = (section + 1) * n // 3

            segment = signal[start:end]

            features[
                f"{name}_seg{section + 1}_mean"
            ] = np.mean(segment)

            features[
                f"{name}_seg{section + 1}_std"
            ] = np.std(segment)

            features[
                f"{name}_seg{section + 1}_range"
            ] = np.ptp(segment)

    return features


# ============================================================
# LOAD DATASET
# ============================================================

def load_dataset():

    feature_rows = []

    print()
    print("=" * 60)
    print("LOADING DATASET")
    print("=" * 60)

    for phrase in PHRASES:

        phrase_dir = os.path.join(
            DATASET_DIR,
            phrase
        )

        files = sorted(
            glob.glob(
                os.path.join(
                    phrase_dir,
                    "recording_*.csv"
                )
            )
        )

        print(
            f"{phrase:20s}: {len(files)} recordings"
        )

        for filepath in files:

            filename = os.path.basename(filepath)

            # Example:
            # recording_01.csv
            recording_number = int(
                filename
                .replace("recording_", "")
                .replace(".csv", "")
            )

            df = pd.read_csv(filepath)

            # Basic validation
            required_columns = [
                "phrase",
                "time",
                "ax",
                "ay",
                "az",
                "gx",
                "gy",
                "gz",
                "piezo",
            ]

            missing_columns = [
                column
                for column in required_columns
                if column not in df.columns
            ]

            if missing_columns:

                print(
                    f"WARNING: {filepath}"
                )

                print(
                    "Missing:",
                    missing_columns
                )

                continue

            if len(df) == 0:

                print(
                    f"WARNING: Empty file: {filepath}"
                )

                continue

            # Remove rows containing NaN
            df = df.dropna()

            features = extract_features(df)

            features["phrase"] = phrase

            # Important:
            # recording number is used as the group
            # during validation.
            features["recording"] = recording_number

            feature_rows.append(features)

    dataset = pd.DataFrame(feature_rows)

    return dataset


# ============================================================
# TRAINING
# ============================================================

def main():

    os.makedirs(
        MODEL_DIR,
        exist_ok=True
    )

    dataset = load_dataset()

    print()
    print("=" * 60)
    print("DATASET SUMMARY")
    print("=" * 60)

    print(
        f"Total recordings loaded: {len(dataset)}"
    )

    print()

    print(
        dataset["phrase"].value_counts()
        .sort_index()
    )

    # --------------------------------------------------------
    # Separate features and labels
    # --------------------------------------------------------

    X = dataset.drop(
        columns=[
            "phrase",
            "recording"
        ]
    )

    y = dataset["phrase"]

    groups = dataset["recording"]

    feature_names = list(X.columns)

    # Save feature names
    with open(
        os.path.join(
            MODEL_DIR,
            "feature_names.json"
        ),
        "w"
    ) as f:

        json.dump(
            feature_names,
            f,
            indent=2
        )

    print()
    print(
        f"Number of features: {len(feature_names)}"
    )

    # --------------------------------------------------------
    # Grouped cross-validation
    # --------------------------------------------------------
    #
    # IMPORTANT:
    #
    # Recording 01 from every phrase belongs to group 1.
    # Recording 02 from every phrase belongs to group 2.
    #
    # This prevents the model from seeing the same recording
    # session during both training and validation.
    #
    # --------------------------------------------------------

    cv = GroupKFold(
        n_splits=5
    )

    # ========================================================
    # MODEL 1: SVM
    # ========================================================

    svm_model = Pipeline([
        (
            "scaler",
            StandardScaler()
        ),

        (
            "classifier",
            SVC(
                kernel="rbf",
                C=2.0,
                gamma="scale"
            )
        )
    ])

    print()
    print("=" * 60)
    print("TRAINING SVM")
    print("=" * 60)

    svm_predictions = cross_val_predict(
        svm_model,
        X,
        y,
        cv=cv,
        groups=groups
    )

    svm_accuracy = accuracy_score(
        y,
        svm_predictions
    )

    print(
        f"SVM accuracy: {svm_accuracy * 100:.2f}%"
    )

    print()
    print("SVM classification report:")
    print(
        classification_report(
            y,
            svm_predictions,
            labels=PHRASES,
            zero_division=0
        )
    )

    svm_cm = confusion_matrix(
        y,
        svm_predictions,
        labels=PHRASES
    )

    # Train SVM on ALL recordings
    svm_model.fit(
        X,
        y
    )

    joblib.dump(
        svm_model,
        os.path.join(
            MODEL_DIR,
            "svm_model.pkl"
        )
    )

    # ========================================================
    # MODEL 2: RANDOM FOREST
    # ========================================================

    rf_model = RandomForestClassifier(
        n_estimators=400,
        random_state=42,
        class_weight="balanced"
    )

    print()
    print("=" * 60)
    print("TRAINING RANDOM FOREST")
    print("=" * 60)

    rf_predictions = cross_val_predict(
        rf_model,
        X,
        y,
        cv=cv,
        groups=groups
    )

    rf_accuracy = accuracy_score(
        y,
        rf_predictions
    )

    print(
        f"Random Forest accuracy: "
        f"{rf_accuracy * 100:.2f}%"
    )

    print()
    print("Random Forest classification report:")
    print(
        classification_report(
            y,
            rf_predictions,
            labels=PHRASES,
            zero_division=0
        )
    )

    rf_cm = confusion_matrix(
        y,
        rf_predictions,
        labels=PHRASES
    )

    # Train Random Forest on ALL recordings
    rf_model.fit(
        X,
        y
    )

    joblib.dump(
        rf_model,
        os.path.join(
            MODEL_DIR,
            "random_forest_model.pkl"
        )
    )

    # ========================================================
    # SAVE CONFUSION MATRICES
    # ========================================================

    svm_cm_df = pd.DataFrame(
        svm_cm,
        index=PHRASES,
        columns=PHRASES
    )

    rf_cm_df = pd.DataFrame(
        rf_cm,
        index=PHRASES,
        columns=PHRASES
    )

    svm_cm_df.to_csv(
        os.path.join(
            MODEL_DIR,
            "svm_confusion_matrix.csv"
        )
    )

    rf_cm_df.to_csv(
        os.path.join(
            MODEL_DIR,
            "random_forest_confusion_matrix.csv"
        )
    )

    # ========================================================
    # PLOT CONFUSION MATRICES
    # ========================================================

    def save_confusion_matrix(
        matrix,
        title,
        filename
    ):

        fig, ax = plt.subplots(
            figsize=(8, 7)
        )

        im = ax.imshow(
            matrix
        )

        ax.set_xticks(
            range(len(PHRASES))
        )

        ax.set_yticks(
            range(len(PHRASES))
        )

        ax.set_xticklabels(
            PHRASES,
            rotation=30,
            ha="right"
        )

        ax.set_yticklabels(
            PHRASES
        )

        ax.set_xlabel(
            "Predicted"
        )

        ax.set_ylabel(
            "Actual"
        )

        ax.set_title(
            title
        )

        for i in range(len(PHRASES)):

            for j in range(len(PHRASES)):

                ax.text(
                    j,
                    i,
                    str(matrix[i, j]),
                    ha="center",
                    va="center"
                )

        fig.colorbar(
            im,
            ax=ax
        )

        fig.tight_layout()

        fig.savefig(
            os.path.join(
                MODEL_DIR,
                filename
            ),
            dpi=180
        )

        plt.close(fig)

    save_confusion_matrix(
        svm_cm,
        f"SVM — Accuracy {svm_accuracy * 100:.1f}%",
        "svm_confusion_matrix.png"
    )

    save_confusion_matrix(
        rf_cm,
        f"Random Forest — Accuracy {rf_accuracy * 100:.1f}%",
        "random_forest_confusion_matrix.png"
    )

    # ========================================================
    # SAVE RESULTS
    # ========================================================

    results = pd.DataFrame({
        "model": [
            "SVM",
            "Random Forest"
        ],

        "accuracy": [
            svm_accuracy,
            rf_accuracy
        ]
    })

    results.to_csv(
        os.path.join(
            MODEL_DIR,
            "model_results.csv"
        ),
        index=False
    )

    # ========================================================
    # FINAL OUTPUT
    # ========================================================

    print()
    print("=" * 60)
    print("TRAINING COMPLETE")
    print("=" * 60)

    print()
    print(
        f"SVM accuracy:          "
        f"{svm_accuracy * 100:.2f}%"
    )

    print(
        f"Random Forest accuracy:"
        f" {rf_accuracy * 100:.2f}%"
    )

    print()
    print("Models saved in:")
    print(
        os.path.abspath(
            MODEL_DIR
        )
    )

    print()
    print("Files created:")

    for filename in sorted(
        os.listdir(MODEL_DIR)
    ):

        print(
            "  ",
            filename
        )

    print()
    print(
        "IMPORTANT:"
    )

    print(
        "The accuracy above is grouped "
        "5-fold cross-validation accuracy."
    )

    print(
        "The saved models are then trained "
        "on all available recordings."
    )


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()