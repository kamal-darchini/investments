import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import math

st.set_page_config(layout="wide")
st.title("Mortgage Payments Calculator")

st.write("### Input Data")
col1, col2 = st.columns(2)
home_value = col1.number_input("Home Value", min_value=0, value=1550000)
deposit = col1.number_input("Down Payment", min_value=0, value=330000)
interest_rate = col2.number_input("Interest Rate (in %)", min_value=0.0, value=6.125)
loan_term = col2.number_input("Loan Term (in years)", min_value=1, value=30)

# Calculate the repayments.
loan_amount = home_value - deposit
monthly_interest_rate = (interest_rate / 100) / 12
number_of_payments = loan_term * 12
monthly_payment = (
    loan_amount
    * (monthly_interest_rate * (1 + monthly_interest_rate) ** number_of_payments)
    / ((1 + monthly_interest_rate) ** number_of_payments - 1)
)

# Display the repayments.
total_payments = monthly_payment * number_of_payments
total_interest = total_payments - loan_amount

st.write("### Payments")
col1, col2, col3 = st.columns(3)
col1.metric(label="Monthly Repayments", value=f"${monthly_payment:,.2f}")
col2.metric(label="Total Repayments", value=f"${total_payments:,.0f}")
col3.metric(label="Total Interest", value=f"${total_interest:,.0f}")


# Create a data-frame with the payment schedule.
schedule = []
remaining_balance = loan_amount

for i in range(1, number_of_payments + 1):
    interest_payment = remaining_balance * monthly_interest_rate
    principal_payment = monthly_payment - interest_payment
    remaining_balance -= principal_payment
    year = math.ceil(i / 12)  # Calculate the year into the loan
    schedule.append(
        [
            i,
            monthly_payment,
            principal_payment,
            interest_payment,
            remaining_balance,
            year,
        ]
    )

df = pd.DataFrame(
    schedule,
    columns=["Month", "Payment", "Principal", "Interest", "Remaining Balance", "Year"],
)

# Create two columns for chart and table
col1, col2 = st.columns(2)

# Display the data-frame as a chart with unique key
payments_df = df[["Year", "Remaining Balance"]].groupby("Year").min().reset_index()
fig = px.line(payments_df, x="Year", y="Remaining Balance",
              title="Remaining Balance Over Time")
fig.update_layout(
    xaxis_title="Year",
    yaxis_title="Remaining Balance ($)",
    showlegend=False
)
col1.plotly_chart(fig, use_container_width=True, key="balance_chart")

# Calculate and display annual interest paid
col2.write("### Annual Interest Paid and Tax Deductions")
annual_interest = df.groupby("Year")[["Interest", "Remaining Balance"]].agg({
    "Interest": "sum",
    "Remaining Balance": "min"
}).reset_index()
annual_interest.rename(columns={"Interest": "Total Interest Paid"}, inplace=True)
annual_interest["Deductible Ratio"] = annual_interest["Remaining Balance"].apply(
    lambda x: min(750000 / x, 1) if x > 0 else 1
)
annual_interest["Deductible Interest"] = annual_interest["Total Interest Paid"] * annual_interest[
    "Deductible Ratio"]
annual_interest["Tax Deduction (34%)"] = annual_interest["Deductible Interest"] * 0.34

# Format the numbers for display
annual_interest["Annual Interest Paid"] = annual_interest["Total Interest Paid"].apply(lambda x: f"${x:,.2f}")
annual_interest["Deductible Interest"] = annual_interest["Deductible Interest"].apply(lambda x: f"${x:,.2f}")
annual_interest["Tax Deduction (34%)"] = annual_interest["Tax Deduction (34%)"].apply(lambda x: f"${x:,.2f}")
annual_interest["Deductible Ratio"] = annual_interest["Deductible Ratio"].apply(lambda x: f"{x:.1%}")
annual_interest["Remaining Balance"] = annual_interest["Remaining Balance"].apply(lambda x: f"${x:,.2f}")

annual_interest = annual_interest[
    ["Year", "Remaining Balance", "Annual Interest Paid", "Deductible Interest", "Tax Deduction (34%)",
     "Deductible Ratio"]]
annual_interest.set_index("Year", inplace=True)
col2.dataframe(annual_interest, height=300, key="interest_table")  # Adjusted height for side-by-side display
