# src/main.py
import logging
import os
from typing import Optional

import numpy as np
import pandas as pd

# --- Determine Project Root ---
# This is defined once at the module level.
# When testing, your test fixture (temp_data_dir) will monkeypatch THIS variable
# in the 'main_module' object.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# --- Helper functions to dynamically get default paths ---
# These functions will use the CURRENT value of PROJECT_ROOT when called.
# This is key for testing, as PROJECT_ROOT will be patched by the test fixture.
def get_default_input_path() -> str:
    return os.path.join(PROJECT_ROOT, "data", "sample_input.csv")


def get_default_output_path() -> str:
    return os.path.join(PROJECT_ROOT, "data", "processed_output.csv")


def get_default_log_path() -> str:
    return os.path.join(PROJECT_ROOT, "data", "data_processing.log")


# --- Configure Logging ---
logger = logging.getLogger(__name__)  # Get logger instance for this module


def setup_logging():
    """Configures the logging for the application."""
    log_file_path = get_default_log_path()  # Use helper to get current log path
    log_dir = os.path.dirname(log_file_path)
    os.makedirs(log_dir, exist_ok=True)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # File Handler
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Add handlers to the logger if they haven't been added already
    # This prevents duplicate handlers if setup_logging is called multiple times (e.g., in tests)
    if not logger.hasHandlers():
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    logger.setLevel(logging.DEBUG)  # Set overall logger level
    logger.propagate = False  # Avoid duplicate logs from root logger


# --- create_sample_dataframe (no changes needed other than using the existing logger) ---
def create_sample_dataframe() -> pd.DataFrame:
    """Generates a sample Pandas DataFrame for demonstration."""
    logger.debug("Creating sample DataFrame.")
    data = {
        "id": range(1, 6),
        "category": ["A", "B", "A", "C", "B"],
        "value1": np.random.randint(10, 50, size=5),
        "value2": np.random.rand(5) * 100,
    }
    df = pd.DataFrame(data)
    logger.debug(f"Sample DataFrame created with {len(df)} rows.")
    return df


# --- process_data (modified to use dynamic default paths) ---
def process_data(input_csv_path: Optional[str] = None) -> pd.DataFrame:
    """
    Reads data from a CSV or generates sample data if not found,
    performs transformations, and returns the processed DataFrame.
    """
    # Dynamically get the default input path using the current (possibly patched) PROJECT_ROOT
    current_default_input_path = get_default_input_path()

    # Ensure data directory exists (uses current PROJECT_ROOT)
    data_dir = os.path.join(PROJECT_ROOT, "data")
    os.makedirs(data_dir, exist_ok=True)

    effective_input_path = input_csv_path if input_csv_path else current_default_input_path

    try:
        if os.path.exists(effective_input_path):
            logger.info(f"Reading data from: {effective_input_path}")
            df = pd.read_csv(effective_input_path)
        else:
            logger.warning(f"Input file '{effective_input_path}' not found. Generating sample data.")
            df = create_sample_dataframe()
            # Save to the current_default_input_path, which reflects patched PROJECT_ROOT in tests
            df.to_csv(current_default_input_path, index=False)
            logger.info(f"Sample data generated and saved to: {current_default_input_path}")
    except pd.errors.EmptyDataError:
        logger.error(f"Input file '{effective_input_path}' is empty. Cannot process.")
        return pd.DataFrame()
    except Exception as e:
        logger.error(
            f"Error reading or generating input data from '{effective_input_path}': {e}",
            exc_info=True,
        )
        return pd.DataFrame()

    if df.empty:  # Handle case where df might be empty after read/generation before transformations
        logger.info("Input DataFrame is empty. No transformations will be applied.")
        return df

    logger.info("Original DataFrame head:")
    logger.info(f"\n{df.head().to_string()}")

    # Perform transformations:
    logger.debug("Starting transformations.")
    df["value1_plus_10"] = df["value1"] + 10
    logger.debug("Added 'value1_plus_10' column.")

    df["value2_div_value1"] = df["value2"] / (df["value1"] + 1e-6)
    logger.debug("Added 'value2_div_value1' column.")

    df_filtered = df[df["value1"] > 20].copy()
    logger.debug(f"Filtered DataFrame, {len(df_filtered)} rows remaining.")

    if not df_filtered.empty:  # Only add 'value1_type' if df_filtered is not empty
        df_filtered["value1_type"] = np.where(df_filtered["value1"] > 35, "High", "Medium")
        logger.debug("Added 'value1_type' column.")
    else:
        logger.debug("DataFrame became empty after filtering; 'value1_type' column not added.")

    logger.info("Processed DataFrame head (after filtering and adding 'value1_type'):")
    logger.info(f"\n{df_filtered.head().to_string()}")

    return df_filtered


# --- Main execution block ---
if __name__ == "__main__":  # pragma: no cover
    setup_logging()  # Call the logging setup function once.
    logger.info("Script execution started.")

    # Get default paths dynamically for the main script execution
    default_input_for_script = get_default_input_path()
    default_output_for_script = get_default_output_path()

    # Ensure output directory exists (process_data also does this for its needs)
    os.makedirs(os.path.dirname(default_output_for_script), exist_ok=True)

    try:
        processed_df = process_data(default_input_for_script)

        if not processed_df.empty:
            processed_df.to_csv(default_output_for_script, index=False)
            logger.info(f"Processed data successfully saved to: {default_output_for_script}")
        else:
            logger.info("No data to save after processing (DataFrame was empty or error occurred).")
    except Exception as e:
        logger.critical(f"An unhandled error occurred during script execution: {e}", exc_info=True)
        # import sys
        # sys.exit(1) # Consider exiting with an error code for critical failures

    logger.info("Script execution finished.")
