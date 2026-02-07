# Streamlit App for Buying and Selling Dashboard

This Streamlit app calculates the buying and selling prices based on the provided charges and discounts.

## Requirements
- Python 3.x
- Streamlit

## Installation
To install the required packages, run:
```bash
pip install streamlit
```

## Usage
To run the app, execute:
```bash
streamlit run app.py
```

## Code
```python
import streamlit as st

# Function to calculate buying price
def calculate_buying_price(buying_price):
    mandi_charge = 0.015 * buying_price
    tractor_rent = 15 * (buying_price / 100)  # Assuming buying price is in kg
    total_buying_price = buying_price + mandi_charge + tractor_rent
    return total_buying_price

# Function to calculate selling price
def calculate_selling_price(selling_price, buying_price):
    cash_discount = 0.04 * selling_price
    labour_charge = 60 * (selling_price / 100)  # Assuming selling price is in kg
    transport_charge = 280 * (selling_price / 100)  # Assuming selling price is in kg
    total_selling_price = selling_price - cash_discount - labour_charge - transport_charge
    return total_selling_price

# Streamlit UI
st.title('Buying and Selling Price Dashboard')

# Input fields
buying_price = st.number_input('Enter Buying Price:', min_value=0.0)

if st.button('Calculate Buying Price'):
    total_buying = calculate_buying_price(buying_price)
    st.write(f'Total Buying Price: {total_buying}')

selling_price = st.number_input('Enter Selling Price:', min_value=0.0)

if st.button('Calculate Selling Price'):
    total_selling = calculate_selling_price(selling_price, buying_price)
    st.write(f'Total Selling Price: {total_selling}')