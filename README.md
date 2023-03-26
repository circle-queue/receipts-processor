# Receipts processor

## What
A tool for scraping receipts (specifically from coop)

Results in a dataframe with 
    MultiIndex[receipt_number: int, receipt_index: int]
    Columns[item: str, price: float]

## Installation
git clone receipts-processor
cd receipts-processor
python -m venv venv
pip install -e .
venv/Scripts/activate.bat

## How
First, activate the venv
venv/Scripts/activate.bat

To scrape from coop (using selenium) and output to "src/receipts/data.parquet" 
    scrape-coop

Then, as an example, you can display the 25 most common items using
    common-example
