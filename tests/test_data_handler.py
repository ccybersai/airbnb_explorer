"""Unit tests for DataHandler, using a small sample CSV."""

import pandas as pd
import pytest

from src.data_handler import DataHandler


@pytest.fixture
def sample_csv(tmp_path):
    """Write a tiny Inside Airbnb-style CSV with messy prices and missing values."""
    df = pd.DataFrame({
        "id": [1, 2, 3, 4, 5],
        "name": ["Loft", "Condo", "Room", "Studio", "House"],
        "neighbourhood_cleansed": ["Khlong Toei", "Vadhana", "Khlong Toei", None, "Vadhana"],
        "room_type": ["Entire home/apt", "Private room", "Private room", "Entire home/apt", "Entire home/apt"],
        "price": ["$1,000.00", "$2,500.00", "$800.00", "$900.00", None],
    })
    path = tmp_path / "listings.csv"
    df.to_csv(path, index=False)
    return str(path)


def test_price_converted_to_numeric(sample_csv):
    dh = DataHandler(sample_csv)
    assert pd.api.types.is_numeric_dtype(dh.df["price"])
    assert 1000.0 in dh.df["price"].values


def test_rows_with_missing_values_dropped(sample_csv):
    dh = DataHandler(sample_csv)
    assert len(dh.df) == 3  # missing-neighborhood and missing-price rows removed


def test_neighborhood_column_renamed(sample_csv):
    dh = DataHandler(sample_csv)
    assert "neighborhood" in dh.df.columns


def test_search_is_case_insensitive(sample_csv):
    dh = DataHandler(sample_csv)
    assert len(dh.search_entries("neighborhood", "khlong")) == 2


def test_search_price_range(sample_csv):
    dh = DataHandler(sample_csv)
    results = dh.search_entries("price", "900-1500")
    assert [r["price"] for r in results] == [1000.0]


def test_aggregate_mean_price(sample_csv):
    dh = DataHandler(sample_csv)
    agg = dh.get_aggregate("neighborhood")
    assert agg["Khlong Toei"]["mean"] == 900.0
    assert agg["Khlong Toei"]["count"] == 2


def test_export_selected_columns(sample_csv, tmp_path):
    dh = DataHandler(sample_csv)
    path, count = dh.filter_and_export(str(tmp_path / "out.csv"), ["name", "price"])
    exported = pd.read_csv(path)
    assert list(exported.columns) == ["name", "price"]
    assert count == 3


def test_invalid_column_raises(sample_csv):
    dh = DataHandler(sample_csv)
    with pytest.raises(ValueError):
        dh.get_aggregate("not_a_column")


def test_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        DataHandler("does/not/exist.csv")