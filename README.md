# Receipts processor

## What
A tool for scraping receipts (specifically from coop)

Results in a dataframe
```
DataFrame[
    MultiIndex[receipt_number: int, receipt_index: int],
    Columns[item: str, price: float]
]
```

## Installation
```
git clone https://github.com/circle-queue/receipts-processor.git
cd receipts-processor
python -m venv venv
pip install -e .
venv/Scripts/activate.bat
```
Then create a .env file in your home directory [```pathlib.Path.home()```] containing
```
RECEIPTS_SECRET_USERNAME = "YOUR_USERNAME"
RECEIPTS_SECRET_PASSWORD = "YOUR_PASSWORD"
```
Or hard code this in ```src/receipts/scrape_coop.py```

## How
First, activate the venv
```venv/Scripts/activate.bat```

To scrape from coop (using selenium) and output to "src/receipts/data.parquet" 
    ```scrape-coop```

Then, as an example, you can display the 25 most common items using
    ```common-example```
