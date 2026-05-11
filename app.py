import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime

st.title("新加坡HDB万岁！😘")
st.write("Following are some font styles.")
st.header("header")
st.subheader("subheader")
st.caption("caption")
st.markdown("markdown")

# Sets the page configuration
# You can set the page title and layout here
st.set_page_config(page_title="HDB Resale Dashboard", layout="wide")

st.title("Singapore HDB Resale Dashboard - Updated Commit 2")
st.caption("Code-along: building a usable dashboard from real resale transactions.")

st.header("Dashboard Overview")
st.subheader("What this app will show")
st.markdown("""
- Transaction volume after filtering
- Average resale price
- Median floor area
- Town and flat type trends
""")



DATA_PATH = "./data/resale_data.csv"

@st.cache_data
def load_data(path):
    #WHERE'S THIS?
    print(f"😭 Rerun at: {datetime.now()}") #caching data means each time filtered, CSV file not need to be reread.
    df = pd.read_csv(path)
    df["month"] = pd.to_datetime(df["month"])
    return df

df = load_data(DATA_PATH)

df = pd.read_csv(DATA_PATH)
# Lesson assumption:
# this dataset has already gone through EDA and basic cleaning.
# Here we focus on dashboard building, not data cleaning.
# We still set the datetime dtype explicitly for reliable filtering and charting.
df["month"] = pd.to_datetime(df["month"])

#All data before filtering.
st.header("All data before filtering.")
st.write(f"Rows loaded: {len(df):,} | Columns: {len(df.columns)}")
st.dataframe(df.head(20), width="stretch")

#sidebar frontend only, no filtering logic yet.
st.sidebar.header("Filters")

#unique, load only but not displayed yet.
unique_towns = sorted(df["town"].dropna().unique())
unique_flat_types = sorted(df["flat_type"].dropna().unique())

#load the list of unique
selected_towns = st.sidebar.multiselect("Town", unique_towns, default=[])
selected_flat_types = st.sidebar.multiselect("Flat Type", unique_flat_types, default=[])

#slide for price range. Determine min and max.
min_price = int(df["resale_price"].min())
max_price = int(df["resale_price"].max())

#slider widget code
price_range = st.sidebar.slider(
    "Resale Price Range",
    min_value=min_price,
    max_value=max_price,
    value=(min_price, max_price),
    step=10000,
)

#slider for date. only able after converting to datetime.
date_min = df["month"].min().date()
date_max = df["month"].max().date()

#input widget in sidebar
date_range = st.sidebar.date_input("Month Range", value=(date_min, date_max))


#----- FILTER - make a copy of the original dataframe to apply filters on.
filtered_df = df.copy()

#boolean mask: if selected, return to filtered df data frame.
if selected_towns:
    filtered_df = filtered_df[filtered_df["town"].isin(selected_towns)]

if selected_flat_types:
    filtered_df = filtered_df[filtered_df["flat_type"].isin(selected_flat_types)]

filtered_df = filtered_df[
    filtered_df["resale_price"].between(price_range[0], price_range[1])
]
#if both dates selected, duple created. 
if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = filtered_df[filtered_df["month"].between(
        pd.to_datetime(start_date), pd.to_datetime(end_date)
    )]

#--- KPI of filtered data - Top metrics: Before displaying of table is ok.
st.header("Key Metrics")
# Create four columns(streamlit element) for the metrics(streamlit element) and unpack them
# We can then use each column to place a metric
col1, col2, col3, col4 = st.columns(4)

# Each col provides a .metric() method that takes a label and a value
col1.metric("Transactions", f"{len(filtered_df):,}")
col2.metric("Average Price", f"${filtered_df['resale_price'].mean():,.0f}")
col3.metric("Median Price", f"${filtered_df['resale_price'].median():,.0f}")
col4.metric("Median Floor Area", f"{filtered_df['floor_area_sqm'].median():.1f} sqm")

    #MAIN CONTENT after filter - to use filtered data in the UI.
st.header("Filtered Results")
st.write(f"Matching rows: {len(filtered_df):,} | Columns: {len(filtered_df.columns)}")
st.dataframe(filtered_df.head(20), width="stretch")

#context mgr - all elements in same column: with col_left ...
# added with this on top: import plotly.express as px

import plotly.express as px

st.header("Visual Analysis")

col_left, col_right = st.columns(2) #only if want side by side in 2 columns.

# Tells Streamlit to put the following content in the left column
with col_left:
    st.subheader("Average Resale Price by Town")
    avg_price_by_town = (
        filtered_df.groupby("town", as_index=False)["resale_price"] #like sql groupby. don't use index.
        .mean()
        .sort_values("resale_price", ascending=False)
        .head(10) # Top 10 towns only for clarity
    )
    # Create a Plotly bar chart with towns on x-axis and average resale price on y-axis
    fig_town = px.bar(avg_price_by_town, x="town", y="resale_price")
    # Display the Plotly chart in Streamlit
    st.plotly_chart(fig_town, width="stretch") #width = to max.

# Tells Streamlit to put the following content in the right column
with col_right:
    st.subheader("Transactions by Flat Type")
    tx_by_flat = (
        filtered_df.groupby("flat_type", as_index=False)
        .size()
        .rename(columns={"size": "transactions"})
        .sort_values("transactions", ascending=False)
    )
    # Create a Plotly bar chart with flat types on x-axis and transaction counts on y-axis
    fig_flat = px.bar(tx_by_flat, x="flat_type", y="transactions")
    # Display the Plotly chart in Streamlit
    st.plotly_chart(fig_flat, width="stretch")

#Monthly trend
st.subheader("Monthly Median Resale Price")
trend = (
    filtered_df.groupby("month", as_index=False)["resale_price"]
    .median()
    .sort_values("month")
)
# Create a Plotly line chart with month on x-axis and median resale price on y-axis
fig_trend = px.line(trend, x="month", y="resale_price", markers=True)
# Display the Plotly chart in Streamlit
st.plotly_chart(fig_trend, width="stretch")

#Detailed table and download function
with st.expander("View Filtered Transactions"):
    st.dataframe(filtered_df, width="stretch", height=350)
    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download filtered CSV",
        data=csv,
        file_name="filtered_resale_data.csv",
        mime="text/csv",
    )