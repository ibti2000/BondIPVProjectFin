import streamlit as st
from bondcode import bond_price
import pandas as pd
import altair as alt

st.sidebar.markdown("[View Source Code](https://github.com/ibti2000/BondIPVProjectFin)")

st.title("Independent Price Verification Tool - Bond Pricer")

face_value = st.number_input("Face Value", value=1000.0, step=100.0)
coupon_rate = st.number_input("Coupon Rate (decimal)", value=0.05, step=0.01)
periods = st.number_input("Years to Maturity", value=5.0, step=1.0)
market_rate = st.number_input("Market Rate / Yield (decimal)", value=0.05, step=0.01)
m = st.number_input("Payments per Year (m)", value=1, step=1)
        
#Calculate now

if st.button("Calculate Bond Value"):
    price, duration, convexity = bond_price(face_value, coupon_rate, periods, market_rate, m)
    st.success(f"Bond Price: {price:.2f}")
    st.write(f"**Duration:** {duration:.4f}")
    st.write(f"**Convexity:** {convexity:.4f}")

uploaded_file = st.file_uploader("Upload Trader Bond Data (CSV)", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df[["ModelPrice", "Duration", "Convexity"]] = df.apply(
        lambda row: pd.Series(
            bond_price(row["FaceValue"], row["CouponRate"], row["Periods"], row["MarketRate"], row["PaymentsPerYear"])
        ),
        axis=1
    )
    df["Difference"] = df["TraderPrice"] - df["ModelPrice"]

    st.subheader("Uploaded Data with Model Results")
    st.dataframe(df)


    st.subheader("Mispricing Summary")
    max_diff = df["Difference"].max()
    min_diff = df["Difference"].min()
    avg_diff = df["Difference"].mean()
    overpriced_count = (df["Difference"] > 0).sum()
    underpriced_count = (df["Difference"] < 0).sum()
    
    summary_df = pd.DataFrame({
        "Metric": ["Max Mispricing", "Min Mispricing", "Avg Mispricing", "Number Overpriced", "Number Underpriced"],
        "Value": [max_diff, min_diff, avg_diff, overpriced_count, underpriced_count]
    })
    st.table(summary_df)

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Max Mispricing", f"{max_diff:.2f}")
    col2.metric("Min Mispricing", f"{min_diff:.2f}")
    col3.metric("Avg Mispricing", f"{avg_diff:.2f}")
    col4.metric("Overpriced Count", overpriced_count)
    col5.metric("Underpriced Count", underpriced_count)

    st.subheader("Trader vs Model Price Differences")
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X("Periods:O", title="Years to Maturity"),
        y=alt.Y("Difference:Q", title="Trader - Model Price"),
        color=alt.condition(
            alt.datum.Difference > 0,
            alt.value("green"),
            alt.value("red")
        ),
        tooltip=["FaceValue", "CouponRate", "Periods", "MarketRate", "TraderPrice", "ModelPrice", "Difference"]
    ).properties(width=600, height=400)
    st.altair_chart(chart)

    st.subheader("Top 5 Overpriced / Underpriced Bonds")
    st.dataframe(df.nlargest(5, "Difference")[["FaceValue", "CouponRate", "Periods", "TraderPrice", "ModelPrice", "Difference"]])
    st.dataframe(df.nsmallest(5, "Difference")[["FaceValue", "CouponRate", "Periods", "TraderPrice", "ModelPrice", "Difference"]])

    # Histogram
    st.subheader("Mispricing Distribution")
    hist_chart = alt.Chart(df).mark_bar().encode(
        x=alt.X("Difference:Q", bin=alt.Bin(maxbins=30), title="Mispricing"),
        y="count()",
        tooltip=["count()"]
    ).properties(width=600, height=400)
    st.altair_chart(hist_chart)

    st.download_button(
        "Download Processed Data",
        df.to_csv(index=False).encode("utf-8"),
        "bond_results.csv",
        "text/csv"
    )



