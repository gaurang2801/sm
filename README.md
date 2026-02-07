# Buying & Selling Dashboard

A professional Streamlit application for managing buying and selling transactions with comprehensive error handling, input validation, and edge case management.

## Features

- 📊 **Dashboard** - Monitor business performance at a glance with key metrics and charts
- 📥 **Record Buying** - Add purchase transactions with automatic cost calculations
- 📤 **Record Selling** - Record sales and link them to inventory
- 📋 **View Transactions** - Filter, search, and manage all transactions
- 📦 **Pending Inventory** - Track items bought but not yet sold
- 💼 **Buyer/Seller Ledger** - Manage payment balances and track dues
- ⚙️ **Settings** - View configuration and application logs

## Project Structure

```
v1/
├── app.py                 # Main application entry point
├── config.py              # Configuration and constants
├── database.py            # Database operations and CRUD functions
├── validators.py          # Input validation functions
├── calculations.py        # Price calculation functions
├── transactions.py        # Transaction CRUD operations
├── utils.py               # Utility functions and UI helpers
├── styles.py              # Custom CSS styling
├── logger_setup.py        # Logging configuration
├── pages/                 # Page modules
│   ├── __init__.py
│   ├── dashboard.py
│   ├── record_buying.py
│   ├── record_selling.py
│   ├── view_transactions.py
│   ├── pending_inventory.py
│   ├── ledger.py
│   └── settings.py
├── logs/                  # Application logs
└── transactions.db        # SQLite database
```

## Requirements

- Python 3.8+
- Streamlit
- Pandas
- SQLite3 (included with Python)

## Installation

```bash
pip install streamlit pandas
```

## Usage

```bash
streamlit run app.py
```

## Configuration

Transaction rates and limits can be modified in `config.py`:

| Setting | Default Value |
|---------|---------------|
| Mandi Charge Rate | 1.5% |
| Muddat Rate | 1.5% |
| Cash Discount Rate | 4% |
| Tractor Rent | ₹15/Quintal |
| Labour Charge | ₹60/Quintal |
| Transport Charge | ₹280/Quintal |

## License

MIT License