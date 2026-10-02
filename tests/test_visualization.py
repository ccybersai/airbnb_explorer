"""Unit tests for Visualization."""

import os

import pandas as pd
import pytest

from src.visualization import Visualization


@pytest.fixture
def sample_df():
    """Small cleaned DataFrame like the one DataHandler produces."""
    return pd.DataFrame({
        "price": [800.0, 1000.0, 2500.0, 1200.0],
        "neighborhood": ["Khlong Toei", "Vadhana", "Khlong Toei", "Bang Rak"],
    })


def test_output_dir_created(tmp_path):
    out = tmp_path / "plots"
    Visualization(output_dir=str(out))
    assert out.is_dir()


def test_missing_price_column_returns_none(tmp_path):
    vis = Visualization(output_dir=str(tmp_path))
    assert vis.plot_price_distribution(pd.DataFrame({"x": [1, 2]})) is None


def test_price_distribution_saves_png(tmp_path, sample_df):
    vis = Visualization(output_dir=str(tmp_path))
    path = vis.plot_price_distribution(sample_df)
    assert path is not None and os.path.exists(path)


def test_neighborhood_plot_saves_jpg(tmp_path, sample_df):
    vis = Visualization(output_dir=str(tmp_path))
    path = vis.plot_neighborhood(sample_df, fmt="jpg")
    assert path is not None and path.endswith(".jpg") and os.path.exists(path)