import pandas as pd
import streamlit as st

from filters import get_filters_and_data
from streamlit_option_menu import option_menu as option_menu
from plots import leads_by_location, property_type_breakdown, property_units_breakdown, lot_area_treemap, \
    residential_units_pie_chart, commercial_units_pie_chart, lead_count_pie_chart, features_map, property_condition_map, \
    conversion_channels_dist, features_table
from utils import process_data, verify_password
from streamlit_gsheets import GSheetsConnection

pd.options.mode.chained_assignment = None

# -------------------------Page Config----------------------------------------
st.set_page_config(page_title="Stock Analysis", layout="wide")

# -------------------------CSS Styling----------------------------------------
with open("css/style.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden; height:0;}
    .block-container {
      margin-top: 0;
      padding-top: 0;
    }
    .stMetric {
       background-color: rgba(28, 131, 225, 0.1);
       border: 1px solid rgba(28, 131, 225, 0.1);
       padding: 5% 5% 5% 10%;
       border-radius: 5px;
       color: rgb(30, 103, 119);
       overflow-wrap: break-word;
       height: 100px;
    }
    .stPlotlyChart {
     outline: 5px solid white;
     border-radius: 10px;
     # border: 5px solid white;
     box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.20), 0 6px 20px 0 rgba(0, 0, 0, 0.30);
    }
    </style>
""", unsafe_allow_html=True)

# ------------------------------- Data Loading ---------------------------------
# users_df = pd.read_csv("data/users.csv")
#
# data = pd.read_csv("data/df.csv", delimiter=",", on_bad_lines='skip')

# ------------------------------- Data Loading ---------------------------------
conn = st.connection("gsheets", type=GSheetsConnection)
data = conn.read(worksheet='leads')
users_df = conn.read(worksheet='users')

data = process_data(data)

# ------------------------------- Authentication --------------------------------
with st.sidebar:
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_role = None

    if st.button("Login"):
        user = users_df[users_df['Email'] == email]
        if not user.empty:
            stored_hashed_password = user['Password'].values[0]
            if verify_password(password, stored_hashed_password):
                st.success(f"Logged in as {user['Name'].values[0]}")
                st.session_state.logged_in = True
                st.session_state.user_role = user['Role'].values[0]
            else:
                st.error("Incorrect password")
        else:
            st.error("User not found")

    menu_options = ['Login Required']
    if st.session_state.logged_in:
        role = st.session_state.user_role

        # Administrator menu
        if role == "Administrator/in":
            menu_options=["Quick Summary", "Leads Features", "Edit Leads"]
        # Mitarbeiter (Employee) menu
        elif role == "Mitarbeiter/in":
            menu_options=["Quick Summary", "Leads Features"]
        # Tracking Partner menu
        elif role == "Trackingpartner":
            menu_options=["Leads Features"]



# -------------------------------- App ------------------------------------------
menu = option_menu(menu_title=None,
                   options=menu_options,
                   orientation="horizontal")

if menu == "Quick Summary":
    df = get_filters_and_data(data)

    metrics = st.columns(5)
    metrics[0].metric(label="Total Leads", value=len(df))
    metrics[1].metric(label="Total Residential Units", value=round(df['Wohneinheiten'].sum()))
    metrics[2].metric(label="Total Commercial Units", value=round(df['Gewerbeeinheiten'].sum()))
    metrics[3].metric(label="Avg. Living Area (sq meters)", value=f"{df['Wohnflaeche'].mean():.2f}")
    metrics[4].metric(label="Avg. Lot Area (sq meters)", value=f"{df['Grundstueckflaeche'].mean():.2f}")

    row_2 = st.columns(3)
    row_2[0].plotly_chart(lead_count_pie_chart(df), use_container_width=True)
    row_2[1].plotly_chart(residential_units_pie_chart(df), use_container_width=True)
    row_2[2].plotly_chart(commercial_units_pie_chart(df), use_container_width=True)

    row_3 = st.columns((4,3))
    row_3[0].plotly_chart(property_type_breakdown(df), use_container_width=True)
    row_3[1].plotly_chart(property_units_breakdown(df), use_container_width=True)

    row_4 = st.columns((4, 3))
    row_4[0].plotly_chart(leads_by_location(df), use_container_width=True)
    row_4[1].plotly_chart(conversion_channels_dist(df), use_container_width=True)

    st.plotly_chart(lot_area_treemap(df), use_container_width=True)

if menu == "Leads Features":
    filters_row = st.columns((1,5))
    selected_email = filters_row[0].selectbox("Select Email", data['Email'].unique())
    filtered_data = data[(data['Email'] == selected_email)]

    if not filtered_data.empty:
        filtered_data = filtered_data.sort_values(by='Baujahr')
        for idx, row in filtered_data.iterrows():
            st.write(f"### Property Listing no. {idx}")

            residential_units = row['Wohneinheiten'] if not pd.isna(row['Wohneinheiten']) else 0
            commercial_units = row['Gewerbeeinheiten'] if not pd.isna(row['Gewerbeeinheiten']) else 0
            living_area = round(row['Wohnflaeche']) if not pd.isna(row['Wohnflaeche']) else 0
            lot_area = round(row['Grundstueckflaeche']) if not pd.isna(row['Grundstueckflaeche']) else 0

            metrics_row = st.columns(5)
            metrics_row[0].metric(label="Year of Construction", value=round(row['Baujahr']))
            metrics_row[1].metric(label="Residential Units", value=residential_units)
            metrics_row[2].metric(label="Commercial Units", value=commercial_units)
            metrics_row[3].metric(label="Living Area (sq meters)", value=living_area)
            metrics_row[4].metric(label="Lot Area (sq meters)", value=lot_area)

            row_2 = st.columns(2)
            row_2[0].plotly_chart(features_table(row), use_container_width=True)
            row_2[1].plotly_chart(property_condition_map(row), use_container_width=True)

    else:
        st.write("No properties found for the selected lead.")
