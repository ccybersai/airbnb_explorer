"""Entry point: parses arguments and coordinates the CLI, DataHandler, and Visualization."""

import argparse
import logging
import sys

from src.data_handler import DataHandler
from src.visualization import Visualization
from src.cli import CLI

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

for noisy in ("kaleido", "choreographer", "logistro"):
    logging.getLogger(noisy).setLevel(logging.WARNING)


def main():
    """Parse command-line arguments and run the requested action."""
    parser = argparse.ArgumentParser(description="Airbnb Listings Explorer")
    parser.add_argument("--file", type=str, default="data/raw/listings.csv", help="Path to Airbnb CSV file")
    parser.add_argument("--summary", action="store_true", help="Display data summary")
    parser.add_argument("--search", nargs=2, metavar=("COLUMN", "VALUE"),
                        help="Search entries by column and value (price accepts a range, e.g. 1000-2000)")
    parser.add_argument("--export", type=str, help="Export filtered data to CSV (specify output file)")
    parser.add_argument("--columns", nargs="*", help="Columns to include in export")
    parser.add_argument("--aggregate", type=str, choices=["neighborhood", "room_type"],
                        help="Display aggregate data by column")
    parser.add_argument("--plot", type=str, choices=["price_dist", "neighborhood"], help="Export plot as JPG/PNG")
    parser.add_argument("--format", type=str, choices=["png", "jpg"], default="png",
                        help="Image format for --plot (default: png)")
    args = parser.parse_args()

    # No action requested: show help without loading the dataset
    if not (args.summary or args.search or args.export or args.aggregate or args.plot):
        parser.print_help()
        return

    try:
        dh = DataHandler(args.file)
        vis = Visualization()
        cli = CLI(dh, vis)

        if args.summary:
            cli.display_summary()
        elif args.export:
            cli.export_data(args.export, args.columns, args.search)
        elif args.search:
            cli.search_entries(args.search[0], args.search[1])
        elif args.aggregate:
            cli.display_aggregate(args.aggregate)
        elif args.plot:
            cli.export_plot(args.plot, args.format)
    except (ValueError, FileNotFoundError) as e:
        # Expected user mistakes: show a clear message, no traceback
        logger.error(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise


if __name__ == "__main__":
    main()
