# Selenium UI Tests

This directory contains automated UI tests using Selenium and Python.

## Prerequisites

1. Python 3.9+
2. Google Chrome installed
3. ChromeDriver (managed automatically by `webdriver-manager`)

## Installation

```bash
pip install -r requirements.txt
```

## Running the Tests

Ensure your application is running at `http://localhost` (or set `TEST_URL` environment variable).

```bash
python3 test_category_management.py
```

## Test Coverage

### `test_category_management.py`
- **Login**: Authenticates as admin.
- **Create Parent Category**: Adds a new root category.
- **Create Child Category**: Adds a sub-category and selects the parent.
- **Verification**: Checks if categories appear in the list and if the parent relationship is correctly displayed in the table.
