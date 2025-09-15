#bondwalkthrough - refer to bsm code walkthrough for a better guidance
#this above code is the function - for streamlit that is below

import numpy as np
from scipy.stats import norm

def bond_price(face_value, coupon_rate, periods, market_rate, m=1): #set parameters for our function


    if not float(periods * m).is_integer(): #just to tell that like # of years aka the periods * m should be integer
        raise ValueError("periods * m must be an integer (whole number of coupon dates).") #if not
    n = int(periods * m) #this is our n
    payment = face_value * coupon_rate / m #pmt - we are adjusting for compounding periods
    I_Y = market_rate / m
    bps = 0.01 / 100 #for duration and convexity
    mbps = bps / m

    #PresentValue of coupons
    discounted_coupons = sum([payment / (1 + I_Y) ** t for t in range(1, n+1)]) 
    #we defined in the for loop thats its incl. 1 and excl n + 1 so n mentioned
    discounted_face = face_value / (1 + I_Y) ** n # bcz only maturity
    price = discounted_coupons + discounted_face
    PVPluscoupon =  sum([payment / (1 + (I_Y + mbps)) ** t for t in range(1, n+1)])
    discounted_PVPlusface = face_value / (1 + (I_Y + mbps)) ** n # bcz only maturity
    PVPlus = PVPluscoupon + discounted_PVPlusface
    PVMinuscoupon = sum([payment / (1 + (I_Y - mbps)) ** t for t in range(1, n+1)]) 
    discounted_PVMinusface = face_value / (1 + (I_Y - mbps)) ** n # bcz only maturity 
    PVMinus = PVMinuscoupon + discounted_PVMinusface
    duration = (PVMinus - PVPlus) / (2 * price * bps)
    convexity = (PVMinus + PVPlus - (2 * price)) / (price * (bps ** 2))                          
    return price, duration, convexity

# Test 1
#price, duration, convexity = bond_price(face_value=1000, coupon_rate=0.05, periods=1, market_rate=0.05)
#print(f"Test 1 Price: {price:.2f}, Duration: {duration:.2f}, Convexity: {convexity:.2f}")

# Test 2
#price, duration, convexity = bond_price(face_value=1000, coupon_rate=0.06, periods=2, market_rate=0.05, m=2)
#print(f"Test 2 Price: {price:.2f}, Duration: {duration:.2f}, Convexity: {convexity:.2f}")

#streamlit code - PLEASE REFER TO BSM WALKTRHOUGH FOR BETTER GUIDE

import streamlit as st
from bondcode import bond_price
import pandas as pd
import altair as alt


st.title("Independent Price Verification Tool - Bond Pricer")

face_value = st.number_input("Face Value", value=1000.0, step=100.0) #step tells theres a plus sign and change in value
coupon_rate = st.number_input("Coupon Rate (decimal)", value=0.05, step=0.01)
periods = st.number_input("Years to Maturity", value=5.0, step=1.0)
market_rate = st.number_input("Market Rate / Yield (decimal)", value=0.05, step=0.01)
m = st.number_input("Payments per Year (m)", value=1, step=1) #all these require you to input a number 
        
#Calculate now

if st.button("Calculate Bond Value"): #if we press the button
    price, duration, convexity = bond_price(face_value, coupon_rate, periods, market_rate, m) #we are given these 3 values and function takes the parameter from values in the variable defined above
    st.success(f"Bond Price: {price:.2f}") #will be shown in green
    st.write(f"**Duration:** {duration:.4f}")
    st.write(f"**Convexity:** {convexity:.4f}")

uploaded_file = st.file_uploader("Upload Trader Bond Data (CSV)", type="csv") #gives a upload button to upload a csv file 

if uploaded_file: #now from now on, all stuff will happen on the ploaded file
    df = pd.read_csv(uploaded_file) #we give the uploaded file the name df
    df[["ModelPrice", "Duration", "Convexity"]] = df.apply( #the answers from this function will be assigned into 3 new columns [[]] for multiple
        lambda row: pd.Series( #pd.series splits the answers in 3 columns
            bond_price(row["FaceValue"], row["CouponRate"], row["Periods"], row["MarketRate"], row["PaymentsPerYear"])
        ),
        axis=1
    )
    #axis = 1 apply per row, and function is given and lamba makes it apply the function on current row from the mentioned column matching the function parameter  
    df["Difference"] = df["TraderPrice"] - df["ModelPrice"] #to get differences

    #^^ we applied 


    st.subheader("Uploaded Data with Model Results")
    st.dataframe(df) #put the df into a dataframe


    st.subheader("Mispricing Summary") #to create a summary heading
    max_diff = df["Difference"].max()
    min_diff = df["Difference"].min()
    avg_diff = df["Difference"].mean()
    overpriced_count = (df["Difference"] > 0).sum()
    underpriced_count = (df["Difference"] < 0).sum()
    
    #we are applying max min and mean on difference column from df table; also summing the difference overpriced/underpriced
    #BELOW --- pd.dataframe - keys and values so the key is basically the title of column in new dataframe and what values it will take
    #these values were calculated above ^^

    summary_df = pd.DataFrame({
        "Metric": ["Max Mispricing", "Min Mispricing", "Avg Mispricing", "Number Overpriced", "Number Underpriced"],
        "Value": [max_diff, min_diff, avg_diff, overpriced_count, underpriced_count]
    })
    st.table(summary_df) #table

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Max Mispricing", f"{max_diff:.2f}")
    col2.metric("Min Mispricing", f"{min_diff:.2f}")
    col3.metric("Avg Mispricing", f"{avg_diff:.2f}")
    col4.metric("Overpriced Count", overpriced_count)
    col5.metric("Underpriced Count", underpriced_count)

    #col1, col2 etc. are just column name variables - st.columns(5) tell create 5 columns
    #the metric thing helps display in a more designed fashion with name of column, the value inside adjusted using f"{}


    #here we create a chart using altair for the df dataframe, .mark_chartname helps decide what chart to use and then encode is just to code the chart
    #alt.X and alt.Y methods to work on the x and y axis; first parameter is to tell whichcolumn:whattype ; the type column and numerical, and then what is axis title
    #alt.condition parameters are (condition, value if true, value if false) and alt.datum lets you go over each row and check what u want like here values in diff col > 0

    st.subheader("Trader vs Model Price Differences")
    chart = alt.Chart(df).mark_bar().encode( #altair helps make charts, mark_chartname we decide the chart and encode tells us what to code in it
        x=alt.X("Periods:O", title="Years to Maturity"), #O is ordinal - categorical, discrete
        y=alt.Y("Difference:Q", title="Trader - Model Price"), #Q is quantative
        color=alt.condition(
            alt.datum.Difference > 0,
            alt.value("green"),
            alt.value("red")
        ),
        tooltip=["FaceValue", "CouponRate", "Periods", "MarketRate", "TraderPrice", "ModelPrice", "Difference"] #when u hover each bar what column values u see
    ).properties(width=600, height=400)
    st.altair_chart(chart) #chart is also the variable name for our chart code
    #set the size of chart and display it


    #Top Over/under table, .nlargest(how many, value from what column); so u put the results in a dataframe and this data is again out of the df

    st.subheader("Top 5 Overpriced / Underpriced Bonds")
    st.dataframe(df.nlargest(5, "Difference")[["FaceValue", "CouponRate", "Periods", "TraderPrice", "ModelPrice", "Difference"]]) #top differences, and what columns to choose and display in df
    st.dataframe(df.nsmallest(5, "Difference")[["FaceValue", "CouponRate", "Periods", "TraderPrice", "ModelPrice", "Difference"]])
    
    #st.dataframe means results get displayed in table form, double bracket picks multiple columns

    # Histogram
    st.subheader("Mispricing Distribution")
    hist_chart = alt.Chart(df).mark_bar().encode(
        x=alt.X("Difference:Q", bin=alt.Bin(maxbins=30), title="Mispricing"), #how many ranges of dist u want so we want 30 interval to be made within the min max value
        y="count()", #histogram shows frequency of the difference values so u can see the distributon
        tooltip=["count()"] #put the count function in the tooltip
    ).properties(width=600, height=400)
    st.altair_chart(hist_chart)

    st.download_button(
        "Download Processed Data",
        df.to_csv(index=False).encode("utf-8"),
        "bond_results.csv",
        "text/csv"
    )

    #encode utf-8 is general for conversion browser friendly
    #text/csv to tell its a csv file 
    #download_button - a st feature

