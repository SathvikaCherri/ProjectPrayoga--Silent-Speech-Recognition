import os
import time
import serial
import serial.tools.list_ports


# ============================================================
# CONFIGURATION
# ============================================================

BAUD_RATE = 115200

OUTPUT_FOLDER = "silent_speech_dataset"

PHRASES = [
    "HELLO",
    "YES",
    "NO",
    "I NEED WATER",
    "I NEED HELP"
]


# ============================================================
# FIND ESP32 AUTOMATICALLY
# ============================================================

def find_esp32_port():

    ports = list(
        serial.tools.list_ports.comports()
    )

    if not ports:

        print("ERROR: No serial devices found.")
        print()
        print("Make sure the ESP32 is connected by USB.")
        return None


    # Try to identify common ESP32 USB chips
    keywords = [
        "CP210",
        "CH340",
        "CH341",
        "USB Serial",
        "Silicon Labs",
        "Espressif"
    ]


    for port in ports:

        description = (
            str(port.description)
            + " "
            + str(port.manufacturer)
        )

        for keyword in keywords:

            if keyword.lower() in description.lower():

                print(
                    f"ESP32 found: "
                    f"{port.device} "
                    f"({port.description})"
                )

                return port.device


    # If only one device exists,
    # use it automatically

    if len(ports) == 1:

        print(
            f"Using serial device: "
            f"{ports[0].device}"
        )

        return ports[0].device


    # Multiple unknown devices
    print()
    print("Multiple serial devices found:")

    for i, port in enumerate(ports):

        print(
            f"{i + 1}. "
            f"{port.device} - "
            f"{port.description}"
        )

    print()

    choice = int(
        input("Select the ESP32 number: ")
    )

    return ports[choice - 1].device


# ============================================================
# FIND NEXT RECORDING NUMBER
# ============================================================

def get_next_recording_number():

    highest_number = 0


    if not os.path.exists(OUTPUT_FOLDER):

        return 1


    for phrase in PHRASES:

        phrase_folder = os.path.join(
            OUTPUT_FOLDER,
            phrase.replace(" ", "_")
        )

        if not os.path.exists(phrase_folder):
            continue


        for filename in os.listdir(
            phrase_folder
        ):

            if (
                filename.startswith(
                    "recording_"
                )
                and filename.endswith(".csv")
            ):

                number_text = (
                    filename
                    .replace("recording_", "")
                    .replace(".csv", "")
                )

                try:

                    number = int(
                        number_text
                    )

                    highest_number = max(
                        highest_number,
                        number
                    )

                except ValueError:
                    pass


    return highest_number + 1


# ============================================================
# CREATE PHRASE FOLDERS
# ============================================================

def create_folders():

    os.makedirs(
        OUTPUT_FOLDER,
        exist_ok=True
    )


    for phrase in PHRASES:

        folder_name = phrase.replace(
            " ",
            "_"
        )

        folder = os.path.join(
            OUTPUT_FOLDER,
            folder_name
        )

        os.makedirs(
            folder,
            exist_ok=True
        )


# ============================================================
# OPEN CSV FILES
# ============================================================

def create_csv_files(recording_number):

    files = {}

    for phrase in PHRASES:

        folder_name = phrase.replace(
            " ",
            "_"
        )

        filename = (
            f"recording_"
            f"{recording_number:02d}"
            f".csv"
        )

        filepath = os.path.join(
            OUTPUT_FOLDER,
            folder_name,
            filename
        )


        files[phrase] = open(
            filepath,
            "w",
            encoding="utf-8",
            newline=""
        )


        # Write header
        files[phrase].write(
            "phrase,time,ax,ay,az,gx,gy,gz,piezo\n"
        )


    return files


# ============================================================
# CLOSE CSV FILES
# ============================================================

def close_csv_files(files):

    for file in files.values():

        file.close()


# ============================================================
# DISPLAY COUNTDOWN
# ============================================================

def display_countdown(message):

    if message == "COUNTDOWN_3":

        print("   3...")

    elif message == "COUNTDOWN_2":

        print("   2...")

    elif message == "COUNTDOWN_1":

        print("   1...")

    elif message == "RECORDING_START":

        print()
        print("   >>> RECORDING NOW <<<")
        print()


# ============================================================
# RECORD ONE COMPLETE SESSION
# ============================================================

def record_session(
    esp32,
    recording_number
):

    print()
    print("=" * 65)
    print(
        f"STARTING RECORDING "
        f"{recording_number:02d}"
    )
    print("=" * 65)
    print()


    # Create five CSV files
    files = create_csv_files(
        recording_number
    )


    current_phrase = None

    recording_active = False

    sample_counts = {
        phrase: 0
        for phrase in PHRASES
    }


    # --------------------------------------------------------
    # Start session
    # --------------------------------------------------------

    esp32.write(
        b"START\n"
    )


    while True:

        raw_line = (
            esp32.readline()
            .decode(
                "utf-8",
                errors="ignore"
            )
            .strip()
        )


        if not raw_line:

            continue


        # ----------------------------------------------------
        # ESP32 status messages
        # ----------------------------------------------------

        if raw_line == "ESP32_READY":

            continue


        if raw_line == "MPU6050_OK":

            continue


        if raw_line == "SYSTEM_READY":

            continue


        if raw_line == "SESSION_START":

            print(
                "Session started."
            )

            continue


        # ----------------------------------------------------
        # New phrase
        # ----------------------------------------------------

        if raw_line.startswith(
            "PREPARE:"
        ):

            phrase = raw_line.split(
                ":",
                1
            )[1]

            print()
            print(
                f"Next phrase: "
                f"*** {phrase} ***"
            )

            print(
                "Prepare to silently mouth "
                "the phrase."
            )

            continue


        # ----------------------------------------------------
        # Phrase actually starts
        # ----------------------------------------------------

        if raw_line.startswith(
            "PHRASE_START:"
        ):

            current_phrase = (
                raw_line
                .split(":", 1)[1]
            )

            continue


        # ----------------------------------------------------
        # Countdown
        # ----------------------------------------------------

        if raw_line.startswith(
            "COUNTDOWN_"
        ):

            display_countdown(
                raw_line
            )

            continue


        # ----------------------------------------------------
        # Recording started
        # ----------------------------------------------------

        if raw_line == "RECORDING_START":

            recording_active = True

            continue


        # ----------------------------------------------------
        # CSV header from ESP32
        # ----------------------------------------------------

        if raw_line == "DATA_HEADER":

            continue


        if raw_line == (
            "phrase,time,ax,ay,az,"
            "gx,gy,gz,piezo"
        ):

            continue


        # ----------------------------------------------------
        # Recording ended
        # ----------------------------------------------------

        if raw_line == "RECORDING_END":

            recording_active = False

            print(
                f"Finished: "
                f"{current_phrase}"
            )

            print(
                f"Samples: "
                f"{sample_counts[current_phrase]}"
            )

            continue


        # ----------------------------------------------------
        # Entire session ended
        # ----------------------------------------------------

        if raw_line == "SESSION_END":

            break


        # ----------------------------------------------------
        # Sensor data
        # ----------------------------------------------------

        if recording_active:

            parts = raw_line.split(",")


            # Expected:
            # phrase,time,ax,ay,az,gx,gy,gz,piezo

            if len(parts) != 9:

                continue


            try:

                int(parts[0])
                int(parts[1])

                for value in parts[2:]:

                    float(value)


            except ValueError:

                continue


            if current_phrase is None:

                continue


            # Write directly to the correct CSV
            files[
                current_phrase
            ].write(
                raw_line + "\n"
            )


            sample_counts[
                current_phrase
            ] += 1


    # --------------------------------------------------------
    # Close all files
    # --------------------------------------------------------

    close_csv_files(files)


    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print()
    print("=" * 65)
    print(
        f"RECORDING "
        f"{recording_number:02d} COMPLETE"
    )
    print("=" * 65)

    print()

    for phrase in PHRASES:

        print(
            f"{phrase:<20}"
            f"{sample_counts[phrase]:>6} samples"
        )

    print()


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    print()
    print("=" * 65)
    print(" SILENT SPEECH DATASET RECORDER")
    print("=" * 65)
    print()


    # --------------------------------------------------------
    # Create folders
    # --------------------------------------------------------

    create_folders()


    # --------------------------------------------------------
    # Find ESP32
    # --------------------------------------------------------

    port = find_esp32_port()


    if port is None:

        return


    # --------------------------------------------------------
    # Determine recording number
    # --------------------------------------------------------

    recording_number = (
        get_next_recording_number()
    )


    print()
    print(
        f"Next recording number: "
        f"{recording_number:02d}"
    )


    # --------------------------------------------------------
    # Connect to ESP32
    # --------------------------------------------------------

    print()
    print(
        f"Connecting to "
        f"{port}..."
    )


    try:

        esp32 = serial.Serial(
            port,
            BAUD_RATE,
            timeout=1
        )

    except Exception as error:

        print()
        print(
            "Could not connect to ESP32."
        )

        print(error)

        return


    # ESP32 resets when serial connection opens
    time.sleep(2)


    # Clear old serial data
    esp32.reset_input_buffer()


    print()
    print(
        "ESP32 connected successfully."
    )

    print()


    # --------------------------------------------------------
    # Record
    # --------------------------------------------------------

    try:

        record_session(
            esp32,
            recording_number
        )

    except KeyboardInterrupt:

        print()
        print()
        print(
            "Recording stopped by user."
        )

    finally:

        esp32.close()


    # --------------------------------------------------------
    # Final message
    # --------------------------------------------------------

    print()
    print("=" * 65)
    print(" DATA SAVED")
    print("=" * 65)

    print()
    print(
        f"Recording {recording_number:02d} "
        "has been saved automatically."
    )

    print()

    print(
        "Location:"
    )

    print(
        f"    {OUTPUT_FOLDER}/"
    )

    print()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()