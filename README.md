# Raceyard SBG Status Decoder

A simple web application built with Streamlit to decode decimal status codes from SBG Systems' inertial navigation systems into human-readable flags.

This tool is designed for the Raceyard Formula Student team to quickly diagnose sensor states during testing and development.

## Features

-   **Web-Based UI:** Accessible from any browser on the local network.
-   **Dynamic Definitions:** Status bit definitions are loaded from an external `status_codes.yaml` file, making them easy to update without changing the code.
-   **Comprehensive Decoding:** Supports both simple bitmasks and multi-bit enum values.

## File Structure

-   `streamlit_app.py`: The main Streamlit application script.
-   `status_codes.yaml`: Contains all status code definitions based on the SBG firmware manual.
-   `requirements.txt`: Lists the required Python packages.
-   `README.md`: This file.

## How to Run Locally

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd <your-repo-folder>
    ```

2.  **Install the dependencies:**
    Make sure you have Python 3.8+ installed.
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Streamlit app:**
    ```bash
    streamlit run streamlit_app.py
    ```

4.  **Open your browser:** Navigate to the local URL provided by Streamlit (usually `http://localhost:8501`).
