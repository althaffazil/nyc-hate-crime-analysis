import pandas as pd
import streamlit as st
import plotly.express as px 

st.set_page_config(page_title="NYC Hate Crime Analytics",
                   layout="wide"
                   )

st.header("New York City Hate Crime Analytics", divider=True)
st.markdown("---")

def load_data():
    return pd.read_csv("nypd_data_cleaned.csv")

df = load_data()

# Convert Borough to Title Case

df["Patrol Borough"] = df["Patrol Borough"].str.title()


# Sidebar
st.sidebar.header("Filters")

selected_year = st.sidebar.selectbox("Select Year",sorted(df["Year"].unique()))
selected_borough = st.sidebar.selectbox("Select Patrol Borough",["All"]+sorted(df["Patrol Borough"].unique()))


# Filter Data Based on Selections

filtered_df = df[df["Year"]==selected_year]

if selected_borough != "All":
    filtered_df = filtered_df[filtered_df["Patrol Borough"] == selected_borough]



# KPI Metrics

total_crimes = len(filtered_df)
most_common_offense_cat = filtered_df["Offense Category"].mode()[0] if not filtered_df.empty else "N/A"

if selected_borough == "All":
    most_affected_borough = filtered_df["Patrol Borough"].mode()[0] if not filtered_df.empty else "N/A"
    kpi_1, kpi_2, kpi_3 = st.columns(3)
    kpi_1.metric("Total Crime Count", f"{total_crimes:,}")
    kpi_2.metric("Most Common Offense Category", most_common_offense_cat.title()) 
    kpi_3.metric("Most Affected Borough", most_affected_borough.title())
else:
    most_affected_precinct = filtered_df["Precinct Code"].mode()[0] if not filtered_df.empty else "N/A"
    kpi_1, kpi_2, kpi_3 = st.columns(3)
    kpi_1.metric("Total Crime Count", f"{total_crimes:,}")
    kpi_2.metric("Most Common Offense Category", most_common_offense_cat.title())  # Title case
    kpi_3.metric("Most Affected Precinct", most_affected_precinct)


st.markdown("---")


# Monthly Trend Analysis

st.subheader("Monthly Hate Crime Trends")
# Ensure all months are included, even if crime count is 0
month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# Convert Month column to categorical with the correct order
filtered_df["Month"] = pd.Categorical(filtered_df["Month"], categories=month_order, ordered=True)

# Count crimes per month and fill missing months with 0
monthly_trend = filtered_df["Month"].value_counts().reindex(month_order, fill_value=0).reset_index()
monthly_trend.columns = ["Month", "Count"]

# Plot the continuous line chart
fig_trend = px.line(monthly_trend, x="Month", y="Count", markers=True, 
                    color_discrete_sequence=["red"])

# Show chart
st.plotly_chart(fig_trend, use_container_width=True)



# Row: Bias Motive & Offense Category
st.subheader("Bias Motive & Offense Category Distribution")
col6, col7 = st.columns(2)

# Pie Chart: Bias Motive Distribution
bias_counts = filtered_df["Bias Motive"].value_counts().reset_index()
bias_counts.columns = ["Bias Motive", "Count"]
bias_counts["Bias Motive"] = bias_counts["Bias Motive"].str.title()  # Title case
fig_bias = px.pie(bias_counts, names="Bias Motive", values="Count", title="Bias Motive Distribution", hole=0.4)
col6.plotly_chart(fig_bias, use_container_width=True)

# Bar Chart: Offense Category
offense_counts = filtered_df["Offense Category"].value_counts().reset_index()
offense_counts.columns = ["Offense Category", "Count"]
offense_counts["Offense Category"] = offense_counts["Offense Category"].str.title()  # Title case
fig_offense = px.bar(offense_counts, x="Count", y="Offense Category", orientation="h", title="Offense Category Distribution", color="Count", color_continuous_scale="Blues")
col7.plotly_chart(fig_offense, use_container_width=True)

st.markdown("---")



# Treemap for Precincts
st.subheader("Precinct-Level Crime Distribution")

if not filtered_df.empty:
    precinct_counts = filtered_df["Precinct Code"].value_counts().reset_index()
    precinct_counts.columns = ["Precinct", "Count"]
    
    fig_treemap = px.treemap(precinct_counts, 
                              path=["Precinct"], 
                              values="Count",
                              color="Count",
                              color_continuous_scale="Reds")

    st.plotly_chart(fig_treemap, use_container_width=True)
else:
    st.warning("No data available for the selected filters.")




st.subheader("Crime Incidents by County")
import json
with open('nyc_counties_geojson.json', 'r') as f:
    geojson_data = json.load(f)

# Define county center coordinates (approximate)
county_centers = {
    "New York": {"lat": 40.7831, "lon": -73.9712},
    "Kings": {"lat": 40.6782, "lon": -73.9442},
    "Queens": {"lat": 40.7282, "lon": -73.7949},
    "Bronx": {"lat": 40.8448, "lon": -73.8648},
    "Richmond": {"lat": 40.5795, "lon": -74.1502}
}

filtered_df["County"] = filtered_df["County"].str.title()

county_data = filtered_df["County"].value_counts().reset_index()
county_data.columns = ["County", "Count"]

# Add latitude and longitude for each county
county_data["Latitude"] = county_data["County"].map(lambda x: county_centers[x]["lat"])
county_data["Longitude"] = county_data["County"].map(lambda x: county_centers[x]["lon"])

# Create Bubble Map
fig = px.scatter_mapbox(
    county_data,
    lat="Latitude",
    lon="Longitude",
    size="Count",
    hover_name="County",
    hover_data={"Count": True, "Latitude": False, "Longitude": False},
    color="Count",
    color_continuous_scale="Sunsetdark",
    size_max=100,
    zoom=9,
    mapbox_style="carto-positron"
    # title="Hate Crime Incidents by County (Bubble Map)"
)

# Update layout for better visuals
fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0})

# Display in Streamlit
st.plotly_chart(fig, use_container_width=True)


