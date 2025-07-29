import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math

st.set_page_config(layout="wide")
st.title("Net Worth and Cash Flow Calculator")

# Input parameters
st.write("### Input Parameters")
col1, col2 = st.columns(2)

house_value_1 = col1.number_input("House 1 Value", min_value=0, value=1500000, key="house_value_1")
down_payment_1 = col1.number_input("Down Payment 1", min_value=0, value=300000, key="down_payment_1")
house_growth_1 = col1.number_input("Annual House Price Growth (%)", min_value=0.0, value=5.0, key="house_growth_1")
interest_rate_1 = col1.number_input("Annual Interest Rate (%)", min_value=0.0, value=6.125, key="interest_rate_1")
monthly_expenses_1 = col1.number_input("Monthly Other Expenses", min_value=0, value=7000, key="monthly_expenses_1")

house_value_2 = col2.number_input("House 2 Value", min_value=0, value=1500000, key="house_value_2")
down_payment_2 = col2.number_input("Down Payment 2", min_value=0, value=300000, key="down_payment_2")
house_growth_2 = col2.number_input("Annual House Price Growth (%)", min_value=0.0, value=5.0, key="house_growth_2")
interest_rate_2 = col2.number_input("Annual Interest Rate (%)", min_value=0.0, value=6.125, key="interest_rate_2")
monthly_expenses_2 = col2.number_input("Monthly Other Expenses", min_value=0, value=7000, key="monthly_expenses_2")

# Create new row for income parameters
col_income_1, col_income_2, col_income_3 = st.columns(3)
monthly_income = col_income_2.number_input("Monthly Income", min_value=0, value=20000, key="monthly_income")
stock_return = col_income_2.number_input("Annual Stock Return (%)", min_value=0.0, value=7.0, key="stock_return")


def get_wealth(house_value, down_payment, monthly_income,
               monthly_expenses, stock_return, house_growth,
               interest_rate):
    # Calculate monthly mortgage payment
    loan_amount = house_value - down_payment
    monthly_interest_rate = interest_rate / 12 / 100
    number_of_payments = 30 * 12
    monthly_payment = (
            loan_amount
            * (monthly_interest_rate * (1 + monthly_interest_rate) ** number_of_payments)
            / ((1 + monthly_interest_rate) ** number_of_payments - 1)
    )

    # Calculate monthly progression
    months = 30 * 12
    data = []
    house_value_current = house_value
    stock_portfolio = 0
    monthly_surplus = monthly_income - monthly_payment - monthly_expenses

    # Calculate initial loan amount and remaining balance
    loan_amount = house_value - down_payment
    monthly_interest_rate = interest_rate / 12 / 100

    for month in range(1, months + 1):
        # Calculate monthly values
        stock_portfolio = stock_portfolio * (1 + stock_return / 100 / 12) + monthly_surplus
        house_value_current *= (1 + house_growth / 100 / 12)

        remaining_balance = (loan_amount * (1 + monthly_interest_rate) ** month -
                             (monthly_payment * ((1 + monthly_interest_rate) ** month - 1) / monthly_interest_rate))
        remaining_balance = max(remaining_balance, 0)
        house_appreciation = house_value_current - house_value
        total_paid = monthly_payment * month
        monthly_interest = monthly_payment * month - (loan_amount - remaining_balance)
        house_equity = house_appreciation + down_payment + total_paid - monthly_interest

        net_worth = house_equity + stock_portfolio

        data.append({
            'Month': month,
            'Year': math.ceil(month / 12),
            # 'House Value': house_value_current,
            'House Equity': house_equity,
            # 'remaining_balance': remaining_balance,
            # 'Paid Interest': yearly_interest,
            # 'Total Paid': total_paid,
            'Stock Portfolio': stock_portfolio,
            'Net Worth': net_worth,
            # 'Yearly Cash Surplus': yearly_surplus,
        })

    # Create DataFrame
    df = pd.DataFrame(data)

    return df


def get_payments(house_vale, down_payment, interest_rate):
    # Create a data-frame with the payment schedule.
    loan_amount = house_vale - down_payment


    number_of_payments = 30 * 12
    monthly_interest_rate = (interest_rate / 100) / 12
    monthly_payment = (
            loan_amount
            * (monthly_interest_rate * (1 + monthly_interest_rate) ** number_of_payments)
            / ((1 + monthly_interest_rate) ** number_of_payments - 1)
    )
    return monthly_payment


df1 = get_wealth(house_value_1, down_payment_1, monthly_income,
               monthly_expenses_1, stock_return, house_growth_1,
               interest_rate_1)
df2 = get_wealth(house_value_2, down_payment_2, monthly_income,
               monthly_expenses_2, stock_return, house_growth_2,
               interest_rate_2)

# monthly payments
st.write("### Payments")
col1, col2 = st.columns(2)
col1.metric(label="House 1 Monthly Repayments", value=f"${get_payments(house_value_1, down_payment_1, interest_rate_1):,.2f}")
col2.metric(label="House 2 Monthly Repayments", value=f"${get_payments(house_value_2, down_payment_2, interest_rate_2):,.2f}")

# Visualizations
col1, col2 = st.columns(2)
col1.write("### Net Worth For House 1")
col2.write("### Net Worth For House 2")

col1, col2 = st.columns(2)
# Net Worth Components
fig1, ax1 = plt.subplots()
x = df1['Month']
width = 0.35
ax1.bar(x - width / 2, df1['House Equity'], width, label='House Equity')
ax1.bar(x + width / 2, df1['Stock Portfolio'], width, label='Stock Portfolio')
ax1.plot(x, df1['Net Worth'], 'r-', label='Net Worth', linewidth=2)
ax1.legend(loc='upper left')
ax1.set_xlabel('Month')
ax1.set_ylabel('Value ($)')
ax1.set_title(f'Net Worth Components - ${house_value_1:,} House')
col1.pyplot(fig1)

# Net Worth Components
fig1, ax1 = plt.subplots()
x = df2['Month']
width = 0.35
ax1.bar(x - width / 2, df2['House Equity'], width, label='House Equity')
ax1.bar(x + width / 2, df2['Stock Portfolio'], width, label='Stock Portfolio')
ax1.plot(x, df2['Net Worth'], 'r-', label='Net Worth', linewidth=2)
ax1.legend(loc='upper left')
ax1.set_xlabel('Month')
ax1.set_ylabel('Value ($)')
ax1.set_title(f'Net Worth Components - ${house_value_2:,} House')
col2.pyplot(fig1)


# Display detailed data
col1, col2 = st.columns(2)

col1.write("### Detailed Yearly Data For House 1")
df1['Month'] = df1['Month'].apply(lambda x: ((x - 1) % 12) + 1)
col1.dataframe(df1.groupby(['Year', 'Month']).last().round(0).astype(int))

col2.write("### Detailed Yearly Data For House 2")
df2['Month'] = df2['Month'].apply(lambda x: ((x - 1) % 12) + 1)
col2.dataframe(df2.groupby(['Year', 'Month']).last().round(0).astype(int))


# Plot net worth difference
st.write("### Net Worth Difference (House 1 - House 2)")
col1, col2 = st.columns(2)
fig3, ax3 = plt.subplots(figsize=(8, 4))
x = (df1['Year'] - 1) * 12 + df1['Month']
ax3.bar(x, df1['Net Worth'] - df2['Net Worth'], color='b')
ax3.axhline(y=0, color='r', linestyle='--')
ax3.legend(loc='upper left')
ax3.set_xlabel('Month of Year')
ax3.set_ylabel('Value ($)')
ax3.set_title('Net Worth Difference Between Houses')
col1.pyplot(fig3)


