# Airbnb Listings Explorer

A Python command-line application for exploring Inside Airbnb listings data. It summarizes the dataset, searches listings, exports filtered subsets to CSV, calculates price aggregates, and saves Plotly charts as images.

This project uses the Bangkok, Thailand dataset from Inside Airbnb. Prices are in Thai baht (THB).

## Setup

1. Run the setup script to create the folders and virtual environment and install dependencies:
```bash
   bash setup.sh
```
2. Activate the virtual environment:
   - Mac/Linux: `source venv/bin/activate`
   - Windows: `venv\Scripts\activate`
3. Download the detailed `listings.csv.gz` for Bangkok from [Inside Airbnb](https://insideairbnb.com/get-the-data/), unzip it, and place `listings.csv` in `data/raw/`.

Plot export uses Kaleido, which needs Google Chrome. If plots fail to save, run `plotly_get_chrome` inside the virtual environment.

## Usage

```bash
python main.py --help
python main.py --summary
python main.py --search neighborhood "khlong toei"
python main.py --search price 1000-2000
python main.py --aggregate neighborhood
python main.py --aggregate room_type
python main.py --plot price_dist
python main.py --plot neighborhood --format jpg
python main.py --export budget.csv --search price 500-1500 --columns id name neighborhood room_type price
```

Exports given as a bare file name are saved to `data/processed/`. Plots are saved to `data/plots/`.

## Data Cleaning

On load, `DataHandler` automatically:
- renames `neighbourhood_cleansed` to `neighborhood`
- converts `price` from text like `"$1,500.00"` to a number
- drops rows missing a price or neighborhood
- removes zero prices and extreme outliers above Q3 + 3×IQR (Tukey's rule)

## Project Structure

```
airbnb_explorer/
├── src/
│   ├── data_handler.py
│   ├── visualization.py
│   └── cli.py
├── data/
│   ├── raw/
│   ├── processed/
│   └── plots/
├── tests/
├── main.py
├── setup.sh
└── requirements.txt
```

## Running Tests

```bash
python -m pytest -v
```