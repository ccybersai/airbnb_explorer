"""Plot generation and export for the Airbnb Listings Explorer."""

import logging
import os

import plotly.express as px

logger = logging.getLogger(__name__)


class Visualization:
    """Create Plotly charts from listings data and save them as image files."""

    def __init__(self, output_dir="data/plots", currency="THB"):
        """Set the output folder (created if missing) and the currency label for prices."""
        self.output_dir = output_dir
        self.currency = currency
        os.makedirs(self.output_dir, exist_ok=True)

    def _save(self, fig, filename, fmt="png"):
        """Write a figure to the output folder and return its file path."""
        output_file = os.path.join(self.output_dir, f"{filename}.{fmt}")
        fig.write_image(output_file, format=fmt, width=1000, height=600)
        logger.info(f"Saved plot to {output_file}")
        return output_file

    def plot_price_distribution(self, df, fmt="png"):
        """Save a histogram of nightly prices. Returns the file path, or None on failure."""
        try:
            if "price" not in df.columns:
                raise ValueError("Price column not found")
            plot_df = df.dropna(subset=["price"])
            plot_df = plot_df[plot_df["price"] > 0]
            if plot_df.empty:
                raise ValueError("No valid prices to plot")

            fig = px.histogram(
                plot_df, x="price", nbins=50, title="Price Distribution",
                labels={"price": f"Price per night ({self.currency})"},
            )
            fig.update_layout(yaxis_title="Number of listings")
            return self._save(fig, "price_distribution", fmt)
        except Exception as e:
            logger.error(f"Plot error: {e}")
            return None

    def plot_neighborhood(self, df, top_n=15, fmt="png"):
        """Save a bar chart of listing counts for the busiest neighborhoods. Returns path or None."""
        try:
            if "neighborhood" not in df.columns:
                raise ValueError("Neighborhood column not found")
            counts = df["neighborhood"].value_counts().head(top_n).reset_index()
            counts.columns = ["neighborhood", "listings"]
            if counts.empty:
                raise ValueError("No neighborhood data to plot")

            fig = px.bar(
                counts, x="neighborhood", y="listings",
                title=f"Top {len(counts)} Neighborhoods by Number of Listings",
                labels={"neighborhood": "Neighborhood", "listings": "Number of listings"},
            )
            fig.update_layout(xaxis_tickangle=-45)
            return self._save(fig, "neighborhood_listings", fmt)
        except Exception as e:
            logger.error(f"Plot error: {e}")
            return None