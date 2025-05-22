import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Set page config
st.set_page_config(page_title="Bradford Crime Analysis Dashboard", layout="wide")

# Load data
@st.cache_data
def load_data():
    df= pd.read_excel("Complete- crime rate- Bradford-1.xlsx", sheet_name=0)
    crime_map = {
        1: 'Anti-social behaviour', 2: 'Bicycle theft', 3: 'Burglary',
        4: 'Criminal damage and arson', 5: 'Drugs', 6: 'Other crime',
        7: 'Other theft', 8: 'Possession of weapons', 9: 'Public order',
        10: 'Robbery', 11: 'Shoplifting', 12: 'Theft from person',
        13: 'Vehicle crime', 14: 'Violence and Sexual offenses'
    }
    outcome_map = {
        0: 'Unable to prosecute suspect', 1: 'Action by another org.',
        2: 'Awaiting court outcome', 3: 'Court results unavailable',
        4: 'Action not in public interest (formal)', 5: 'Action not in public interest (further)',
        6: 'Further investigation not in public interest', 7: 'No suspect identified',
        8: 'Local resolution', 9: 'Offender given a caution',
        10: 'Penalty notice', 11: 'Status update unavailable',
        12: 'Charged in another case', 13: 'Under investigation'
    }
    df['Crime type label'] = df['Crime type'].map(crime_map)
    df['Last outcome label'] =df['Last outcome category'].map(outcome_map)
    df['Date'] = pd.to_datetime(df['Year'].astype(str) + '-' + df['Month'], format='%Y-%b')
    return df

CRB_clean = load_data()

# Sidebar filters
st.sidebar.header("Filters")
selected_crime = st.sidebar.multiselect("Select Crime Types", CRB_clean['Crime type label'].unique(), default=None)
top_n = st.sidebar.radio("Show Top N Crime Types", [3, 5, 10], index=1)

if selected_crime:
    CRB_clean = CRB_clean[CRB_clean['Crime type label'].isin(selected_crime)]

st.title("📊 Bradford Crime Analysis Dashboard")
st.markdown("This dashboard provides an interactive exploration of crime data across Bradford, UK. Use the filters to adjust the insights.")

# 1. Monthly Trend for Top 5 Crimes
st.subheader("1. Monthly Trend for Top Crime Types")
top5_crimes = CRB_clean['Crime type label'].value_counts().nlargest(5).index
CRB_top5 = CRB_clean[CRB_clean['Crime type label'].isin(top5_crimes)]
trend_data = CRB_top5.groupby([CRB_top5['Date'].dt.to_period('M'), 'Crime type label']).size().unstack().fillna(0)
trend_data.index = trend_data.index.to_timestamp()
fig1, ax1 = plt.subplots(figsize=(12, 5))
trend_data.plot(marker='o', ax=ax1)
ax1.set_title("Monthly Trend for Top 5 Crime Types")
ax1.set_ylabel("Number of Crimes")
ax1.set_xlabel("Month")
ax1.grid(True)
st.pyplot(fig1)

# 2. Stacked Bar Chart of Crime Outcomes
st.subheader("2. Outcome Distribution by Crime Type")
outcome_counts = pd.crosstab(CRB_clean['Crime type label'], CRB_clean['Last outcome label'])
fig2, ax2 = plt.subplots(figsize=(12, 6))
outcome_counts.plot(kind='bar', stacked=True, colormap='tab20', ax=ax2)
ax2.set_title("Crime Type vs Outcome")
ax2.set_ylabel("Count")
ax2.set_xlabel("Crime Type")
ax2.legend(loc='upper right', bbox_to_anchor=(1.2, 1))
st.pyplot(fig2)

# 3. Bar Chart of Top N Crime Types
st.subheader(f"3. Bar Chart of Top {top_n} Crime Types")
top_counts = CRB_clean['Crime type label'].value_counts().nlargest(top_n)
fig_bar, ax_bar = plt.subplots(figsize=(10, 4))
sns.barplot(x=top_counts.values, y=top_counts.index, ax=ax_bar)
ax_bar.set_title(f"Top {top_n} Crime Types")
ax_bar.set_xlabel("Number of Crimes")
ax_bar.set_ylabel("Crime Type")
st.pyplot(fig_bar)


# 4. Spatial KDE Heatmap
st.subheader("3. Crime Location Density (KDE)")
kde_data = CRB_clean.dropna(subset=['Latitude', 'Longitude'])
fig3, ax3 = plt.subplots(figsize=(10, 6))
sns.kdeplot(data=kde_data, x='Longitude', y='Latitude', fill=True, cmap='Reds', thresh=0.05, ax=ax3)
ax3.set_title("KDE Heatmap of Crime Locations")
st.pyplot(fig3)

# 5. Pair Plot
st.subheader("4. Feature Relationships (Pair Plot)")
CRB_pair = CRB_clean.copy()
CRB_pair['Crime Type Code'] = CRB_pair['Crime type label'].astype('category').cat.codes
CRB_pair['Outcome Code'] = CRB_pair['Last outcome label'].astype('category').cat.codes
CRB_pair['Month Code'] = CRB_pair['Date'].dt.month
pair_data = CRB_pair[['Crime Type Code', 'Outcome Code', 'Month Code']].astype(int)
fig4 = sns.pairplot(pair_data, diag_kind='hist')
st.pyplot(fig4)

# 6. Plotly Interactive Map (fallback)
st.subheader("5. Interactive Crime Map with Plotly")
plot_sample = CRB_clean.dropna(subset=['Latitude', 'Longitude']).sample(n=1000, random_state=42)
fig_map = px.scatter_mapbox(
    plot_sample,
    lat='Latitude',
    lon='Longitude',
    color='Crime type label',
    hover_data=['Last outcome label'],
    zoom=10,
    height=500
)
fig_map.update_layout(mapbox_style='open-street-map')
fig_map.update_layout(margin={'r':0,'t':0,'l':0,'b':0})
st.plotly_chart(fig_map)

st.markdown("---")
st.markdown("📍 Built with Streamlit | 📊 Data: West Yorkshire Police")


