import altair as alt
import pandas as pd

def bar(df):
    

    # Create 'Year' and 'Quarter' columns
    df["End Date"] = pd.to_datetime(df["End Date"])
    df["Year"] = df["End Date"].dt.year
    df["Quarter"] = df["End Date"].dt.to_period("Q").astype(str)  # Format like "2025Q1"

    # Optional: combine for a single x-axis label like "Q1 2025"
    df["Quarter_Label"] = df["End Date"].dt.to_period("Q").apply(lambda x: f"{x.quarter}Q {x.year}")

    # Plot using Quarter_Label on x-axis
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X("Quarter_Label:N", title="Quarter", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("Ending Value:Q", title="Ending Value"),
        color="Account Type:N",
        tooltip=["Account Type", "End Date", "Ending Value"]
    ).properties(
        title="Ending Value by Quarter and Account Type",
        width='container'
    )
    return chart

