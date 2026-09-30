"""Data loading, cleaning, and processing for the Airbnb Listings Explorer."""

import logging
import os

import pandas as pd

logger = logging.getLogger(__name__)


class DataHandler:
    """Load, clean, and query an Inside Airbnb listings CSV."""

    def __init__(self, file_path):
        """Store the file path, then load and clean the dataset."""
        self.file_path = file_path
        self.df = None
        self.raw_row_count = None
        self.load_data()

    def load_data(self):
        """Load and clean the Airbnb dataset."""
        try:
            self.df = pd.read_csv(self.file_path, low_memory=False)
            self.raw_row_count = len(self.df)
            logger.info(f"Loaded dataset with {len(self.df)} rows")
        except FileNotFoundError:
            logger.error(f"File {self.file_path} not found")
            raise
        self.clean_data()

    def clean_data(self):
        """Standardize the neighborhood column, convert price to numbers, drop bad rows."""
        df = self.df

        # 1. One consistent column name: "neighborhood"
        if "neighbourhood_cleansed" in df.columns:
            df = df.drop(columns=["neighbourhood"], errors="ignore")
            df = df.rename(columns={"neighbourhood_cleansed": "neighborhood"})
        elif "neighbourhood" in df.columns:
            df = df.rename(columns={"neighbourhood": "neighborhood"})

        # 2. Price: "$1,500.00" -> 1500.0 (unparseable values become NaN)
        df["price"] = pd.to_numeric(
            df["price"].astype(str).str.replace(r"[$,]", "", regex=True),
            errors="coerce",
        )

        # 3. Missing values: rows without a price or neighborhood can't be analyzed
        df = df.dropna(subset=["price", "neighborhood"])

        # 4. Extreme outliers (Tukey's rule): drop zero prices and anything above Q3 + 3*IQR
        q1, q3 = df["price"].quantile([0.25, 0.75])
        upper = q3 + 3 * (q3 - q1)
        df = df[(df["price"] > 0) & (df["price"] <= upper)]

        self.df = df.reset_index(drop=True)
        removed = self.raw_row_count - len(self.df)
        logger.info(f"Cleaning removed {removed} rows; {len(self.df)} remain (price cap {upper:,.0f})")

    def _resolve_column(self, name):
        """Return the real column name for user input, or raise ValueError."""
        name = name.strip().lower()
        if name == "neighbourhood":
            name = "neighborhood"
        if name not in self.df.columns:
            raise ValueError(f"Column '{name}' not found in dataset")
        return name

    def _filter(self, column, value):
        """Return rows matching value. Numeric columns accept a range like '1000-2000'."""
        col = self._resolve_column(column)
        series = self.df[col]
        if pd.api.types.is_numeric_dtype(series):
            if "-" in value:
                low, high = (float(v) for v in value.split("-", 1))
                mask = series.between(low, high)
            else:
                mask = series == float(value)
        else:
            mask = series.astype(str).str.contains(value, case=False, na=False, regex=False)
        return self.df[mask]

    def get_summary(self):
        """Return a dictionary with dataset summary statistics."""
        missing = self.df.isna().sum()
        return {
            "rows": len(self.df),
            "rows_before_cleaning": self.raw_row_count,
            "columns": list(self.df.columns),
            "missing_values": missing[missing > 0].to_dict(),
        }

    def search_entries(self, column, value):
        """Return a list of dictionaries for entries matching criteria."""
        return self._filter(column, value).to_dict(orient="records")

    def filter_and_export(self, output_file, columns, filter_column=None, filter_value=None):
        """Export (optionally filtered) data with selected columns to CSV. Returns (path, row_count)."""
        cols = [self._resolve_column(c) for c in columns] if columns else list(self.df.columns)
        data = self._filter(filter_column, filter_value) if filter_column else self.df

        # A bare file name goes into data/processed/
        if not os.path.dirname(output_file):
            output_file = os.path.join("data", "processed", output_file)
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        data[cols].to_csv(output_file, index=False)
        logger.info(f"Exported {len(data)} rows to {output_file}")
        return output_file, len(data)

    def get_aggregate(self, column):
        """Return a dictionary with price statistics (mean, median, count) grouped by column."""
        col = self._resolve_column(column)
        grouped = (
            self.df.groupby(col)["price"]
            .agg(["mean", "median", "count"])
            .round(2)
            .sort_values("mean", ascending=False)
        )
        return grouped.to_dict(orient="index")