# src/main.py
import logging  # 1. Import the logging module.
import os
from typing import Optional

import numpy as np
import pandas as pd

# --- Determine Project Root (same as before) ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- Define Default Paths (same as before) ---
DEFAULT_INPUT_CSV_PATH = os.path.join(PROJECT_ROOT, "data", "sample_input.csv")
DEFAULT_OUTPUT_CSV_PATH = os.path.join(PROJECT_ROOT, "data", "processed_output.csv")
DEFAULT_LOG_FILE_PATH = os.path.join(PROJECT_ROOT, "data", "data_processing.log")  # 2. Define log file path

# --- Configure Logging ---
# 3. Get a logger instance. Using __name__ is a common practice,
#    it gives the logger the name of the current module (e.g., 'main').
logger = logging.getLogger(__name__)


# 4. This function sets up the logging configuration.
#    It's called once, typically at the start of the script's execution.
def setup_logging():
    """Configures the logging for the application."""
    # Ensure the directory for the log file exists
    log_dir = os.path.dirname(DEFAULT_LOG_FILE_PATH)
    os.makedirs(log_dir, exist_ok=True)

    # Create a formatter: defines how log messages will look.
    # Example: 2023-10-27 10:00:00,123 - main - INFO - This is a log message.
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Create a file handler: writes log messages to a file.
    file_handler = logging.FileHandler(DEFAULT_LOG_FILE_PATH)
    file_handler.setLevel(logging.DEBUG)  # Log DEBUG and higher messages to the file.
    file_handler.setFormatter(formatter)

    # Create a console handler: writes log messages to the console (stdout/stderr).
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)  # Log INFO and higher messages to the console.
    console_handler.setFormatter(formatter)

    # Add the handlers to our logger.
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Set the overall minimum logging level for the logger.
    # If this is INFO, even if a handler is set to DEBUG, only INFO and above will pass through the logger.
    # So, set this to the lowest level you want any handler to process.
    logger.setLevel(logging.DEBUG)

    # Prevent log messages from being propagated to the root logger if it has handlers,
    # to avoid duplicate console output if the root logger is also configured.
    logger.propagate = False


# --- create_sample_dataframe (same as before, but could add logging if complex) ---
def create_sample_dataframe() -> pd.DataFrame:
    """Generates a sample Pandas DataFrame for demonstration."""
    logger.debug("Creating sample DataFrame.")  # 5. Example of a debug log
    data = {
        "id": range(1, 6),
        "category": ["A", "B", "A", "C", "B"],
        "value1": np.random.randint(10, 50, size=5),
        "value2": np.random.rand(5) * 100,
    }
    df = pd.DataFrame(data)
    logger.debug(f"Sample DataFrame created with {len(df)} rows.")
    return df


# --- process_data (modified to use logger) ---
def process_data(input_csv_path: Optional[str] = None) -> pd.DataFrame:
    """
    Reads data from a CSV or generates sample data if not found,
    performs transformations, and returns the processed DataFrame.
    """
    data_dir = os.path.join(PROJECT_ROOT, "data")
    os.makedirs(data_dir, exist_ok=True)

    effective_input_path = input_csv_path if input_csv_path else DEFAULT_INPUT_CSV_PATH

    try:
        if os.path.exists(effective_input_path):
            logger.info(f"Reading data from: {effective_input_path}")  # 6. Replaced print with logger.info
            df = pd.read_csv(effective_input_path)
        else:
            logger.warning(f"Input file '{effective_input_path}' not found. Generating sample data.")  # 7. logger.warning
            df = create_sample_dataframe()
            df.to_csv(DEFAULT_INPUT_CSV_PATH, index=False)
            logger.info(f"Sample data generated and saved to: {DEFAULT_INPUT_CSV_PATH}")
    except pd.errors.EmptyDataError:
        logger.error(f"Input file '{effective_input_path}' is empty. Cannot process.")
        return pd.DataFrame()  # Return an empty DataFrame
    except Exception as e:
        logger.error(
            f"Error reading or generating input data from '{effective_input_path}': {e}",
            exc_info=True,
        )
        # exc_info=True will include traceback information in the log for unexpected errors.
        return pd.DataFrame()  # Return an empty DataFrame

    logger.info("Original DataFrame head:")  # 8. Info log for DataFrame head
    logger.info(f"\n{df.head().to_string()}")  # Using to_string() for better multi-line log output

    # Perform transformations:
    logger.debug("Starting transformations.")
    df["value1_plus_10"] = df["value1"] + 10
    logger.debug("Added 'value1_plus_10' column.")

    df["value2_div_value1"] = df["value2"] / (df["value1"] + 1e-6)
    logger.debug("Added 'value2_div_value1' column.")

    df_filtered = df[df["value1"] > 20].copy()
    logger.debug(f"Filtered DataFrame, {len(df_filtered)} rows remaining.")

    df_filtered["value1_type"] = np.where(df_filtered["value1"] > 35, "High", "Medium")
    logger.debug("Added 'value1_type' column.")

    logger.info("Processed DataFrame head (after filtering and adding 'value1_type'):")
    logger.info(f"\n{df_filtered.head().to_string()}")

    return df_filtered


# --- Main execution block (modified to use logger) ---
if __name__ == "__main__":
    setup_logging()  # 9. Call the logging setup function once.
    logger.info("Script execution started.")  # 10. Log script start

    # Output directory creation is already handled by setup_logging for the log file
    # and by process_data for data files. This explicit one might be redundant
    # but harmless if paths are consistent.
    # os.makedirs(os.path.dirname(DEFAULT_OUTPUT_CSV_PATH), exist_ok=True)

    try:
        processed_df = process_data(DEFAULT_INPUT_CSV_PATH)

        if not processed_df.empty:
            processed_df.to_csv(DEFAULT_OUTPUT_CSV_PATH, index=False)
            logger.info(f"Processed data successfully saved to: {DEFAULT_OUTPUT_CSV_PATH}")
        else:
            logger.info("No data to save after processing (DataFrame was empty or error occurred).")
    except Exception as e:
        logger.critical(f"An unhandled error occurred during script execution: {e}", exc_info=True)  # 11. Log critical errors
        # In a real scenario, you might exit with a non-zero status code here
        # import sys
        # sys.exit(1)

    logger.info("Script execution finished.")  # 12. Log script end
