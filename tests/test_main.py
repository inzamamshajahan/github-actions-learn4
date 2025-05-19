# tests/test_main.py
import os
import tempfile

import main as main_module  # Import the module itself.
import pandas as pd
import pytest
from main import (  # PROJECT_ROOT is no longer directly imported here
    create_sample_dataframe,
    process_data,
)


@pytest.fixture()
def sample_df_for_test() -> pd.DataFrame:
    data = {
        "id": [1, 2, 3, 4, 5],
        "category": ["X", "Y", "X", "Z", "Y"],
        "value1": [15, 25, 35, 45, 10],
        "value2": [10.0, 20.0, 30.0, 40.0, 50.0],
    }
    return pd.DataFrame(data)


@pytest.fixture()
def temp_data_dir(monkeypatch):  # Pytest's built-in monkeypatch fixture
    """Creates a temporary directory for data files during tests and cleans up."""
    with tempfile.TemporaryDirectory() as tmpdir_path:
        monkeypatch.setattr(main_module, "PROJECT_ROOT", tmpdir_path)
        # Also patch the log file path if it's defined globally in main_module
        # and you want test logs to go to a temp location or be suppressed.
        # For simplicity now, we'll let it use the patched PROJECT_ROOT
        # which means test logs would go into temp_data_dir/data/data_processing.log
        # Alternatively, you could disable file logging during tests.
        yield tmpdir_path


def test_create_sample_dataframe():
    df = create_sample_dataframe()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert list(df.columns) == ["id", "category", "value1", "value2"]
    assert len(df) == 5


def test_process_data_with_input_file(sample_df_for_test: pd.DataFrame, temp_data_dir: str):
    # Setup logging for the test context if not already configured by main execution
    # This is only needed if tests run main.py as a script vs importing functions.
    # Our current setup imports functions, and logging is configured when main.py runs.
    # However, to ensure logging is active during test of process_data:
    if not main_module.logger.hasHandlers():  # Check if handlers are already set
        main_module.setup_logging()  # Call setup if not configured

    test_input_csv_path = os.path.join(temp_data_dir, "data", "test_input.csv")
    os.makedirs(os.path.dirname(test_input_csv_path), exist_ok=True)
    sample_df_for_test.to_csv(test_input_csv_path, index=False)

    processed_df = process_data(test_input_csv_path)

    assert not processed_df.empty
    assert "value1_plus_10" in processed_df.columns
    expected_ids_after_filter = [2, 3, 4]
    assert processed_df["id"].tolist() == expected_ids_after_filter
    expected_types = ["Medium", "Medium", "High"]
    assert processed_df["value1_type"].tolist() == expected_types


def test_process_data_generates_sample_if_no_input(temp_data_dir: str):
    if not main_module.logger.hasHandlers():
        main_module.setup_logging()

    processed_df = process_data("non_existent_file.csv")
    assert not processed_df.empty
    assert "value1_plus_10" in processed_df.columns
    generated_input_path = os.path.join(temp_data_dir, "data", "sample_input.csv")
    assert os.path.exists(generated_input_path)


def test_process_data_handles_empty_input_file(temp_data_dir: str):
    if not main_module.logger.hasHandlers():
        main_module.setup_logging()

    empty_csv_path = os.path.join(temp_data_dir, "data", "empty_input.csv")
    os.makedirs(os.path.dirname(empty_csv_path), exist_ok=True)
    with open(empty_csv_path, "w") as f:
        f.write("")  # Create an empty file, or just headers
        # For true EmptyDataError: f.write("col1,col2\n") # just headers

    processed_df = process_data(empty_csv_path)
    assert processed_df.empty  # Expect an empty DataFrame due to EmptyDataError handling
