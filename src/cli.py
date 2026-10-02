"""Formats DataHandler results into user-friendly console output."""

import logging

logger = logging.getLogger(__name__)


class CLI:
    """Console interface that turns raw DataHandler results into readable output."""

    def __init__(self, data_handler, visualization):
        """Store the data handler and visualization objects."""
        self.dh = data_handler
        self.vis = visualization

    @staticmethod
    def _header(title):
        """Print a section header."""
        print(f"\n{'=' * 70}\n{title}\n{'=' * 70}")

    def display_summary(self):
        """Print row counts, column names, and missing-value counts."""
        s = self.dh.get_summary()
        self._header("DATASET SUMMARY")
        print(f"Rows before cleaning: {s['rows_before_cleaning']:,}")
        print(f"Rows after cleaning:  {s['rows']:,}")
        print(f"Columns ({len(s['columns'])}):")
        print("  " + ", ".join(s["columns"]))

        missing = s["missing_values"]
        if missing:
            print(f"\nColumns with missing values ({len(missing)}):")
            for col, count in sorted(missing.items(), key=lambda x: x[1], reverse=True):
                print(f"  {col:<45} {count:>8,}")
        else:
            print("\nNo missing values.")

    def search_entries(self, column, value, limit=20):
        """Print listings matching the search, showing up to `limit` rows."""
        results = self.dh.search_entries(column, value)
        self._header(f"SEARCH: {column} = '{value}'")
        if not results:
            print("No matching listings found.")
            return

        print(f"Found {len(results):,} matching listings. Showing first {min(limit, len(results))}:\n")
        print(f"{'ID':<20} {'Name':<35} {'Neighborhood':<20} {'Room type':<16} {'Price':>9}")
        print("-" * 104)
        for row in results[:limit]:
            print(
                f"{str(row.get('id', ''))[:20]:<20} "
                f"{str(row.get('name', ''))[:35]:<35} "
                f"{str(row.get('neighborhood', ''))[:20]:<20} "
                f"{str(row.get('room_type', ''))[:16]:<16} "
                f"{row['price']:>9,.0f}"
            )

    def export_data(self, output_file, columns, search=None):
        """Export data (optionally filtered by a search) and report where it was saved."""
        filter_column, filter_value = search if search else (None, None)
        path, count = self.dh.filter_and_export(output_file, columns, filter_column, filter_value)
        self._header("EXPORT COMPLETE")
        if search:
            print(f"Filter:  {filter_column} = '{filter_value}'")
        print(f"Columns: {', '.join(columns) if columns else 'all'}")
        print(f"Saved {count:,} rows to {path}")

    def display_aggregate(self, column):
        """Print mean, median, and count of prices grouped by column."""
        agg = self.dh.get_aggregate(column)
        self._header(f"PRICE STATISTICS BY {column.upper()} ({self.vis.currency})")
        print(f"{column.replace('_', ' ').title():<32} {'Mean':>10} {'Median':>10} {'Listings':>9}")
        print("-" * 64)
        for group, stats in agg.items():
            print(f"{str(group)[:32]:<32} {stats['mean']:>10,.0f} {stats['median']:>10,.0f} {int(stats['count']):>9,}")

    def export_plot(self, plot_type, fmt="png"):
        """Create the requested plot and report where it was saved."""
        self._header("EXPORT PLOT")
        if plot_type == "price_dist":
            path = self.vis.plot_price_distribution(self.dh.df, fmt)
        elif plot_type == "neighborhood":
            path = self.vis.plot_neighborhood(self.dh.df, fmt=fmt)
        else:
            raise ValueError(f"Unknown plot type: {plot_type}")

        if path:
            print(f"Plot saved to {path}")
        else:
            print("Plot could not be created. See the error message above.")