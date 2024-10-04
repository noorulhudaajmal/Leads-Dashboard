import pandas as pd
import streamlit as st
from filters import get_filters_and_data
from streamlit_folium import folium_static
from streamlit_option_menu import option_menu as option_menu
from plots import leads_by_location, property_type_breakdown, property_units_breakdown, lot_area_treemap, \
    residential_units_pie_chart, commercial_units_pie_chart, lead_count_pie_chart, features_map, property_condition_map, \
    conversion_channels_dist, features_table, leads_registration_overtime, geographic_listing_analytics, \
    leads_cluster_map
from utils import process_data, verify_password
from streamlit_gsheets import GSheetsConnection
from auth import authenticate_user, handle_authentication_status
from css.streamlit_ui import main_styles, inner_styles
pd.options.mode.chained_assignment = None

# -------------------------Page Config----------------------------------------
st.set_page_config(page_title="Stock Analysis", layout="wide")

# -------------------------CSS Styling----------------------------------------
with open("css/style.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

st.markdown(main_styles, unsafe_allow_html=True)

# ------------------------------- Data -----------------------------------------
# data = pd.read_csv("data/df.csv")
# users_df = pd.read_csv("data/users2.csv")

# ------------------------------- Data Loading ---------------------------------
conn = st.connection("gsheets", type=GSheetsConnection)
data = conn.read(worksheet='leads')
users_df = conn.read(worksheet='users')

data = process_data(data)

# ------------------------------- Authentication --------------------------------
authenticator, authentication_status, name, username = authenticate_user(users_df)
handle_authentication_status(authenticator, authentication_status, name)

role=None

if authentication_status:
    st.markdown(inner_styles, unsafe_allow_html=True)
    menu_options = ['Login Required']
    role = users_df[users_df['Email'] == username]['Role'].values[0] if authentication_status else None
    if role == "Administrator/in":
        menu_options = ['Overview', 'Marketing Attribution', 'Property Breakdown', 'Geographic Analytics', 'Leads Features']
    elif role == "Mitarbeiter/in":
        menu_options = ['Overview', 'Property Breakdown', 'Leads Features']
    elif role == "Trackingpartner":
        menu_options = ['Leads Features']
    else:
        menu_options = ['Login Required']

    menu = option_menu(menu_title=None, orientation="horizontal", menu_icon=None,
                       options=menu_options)

    if menu == "Overview":
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

        row_3 = st.columns((4, 3))
        row_3[0].plotly_chart(lot_area_treemap(df), use_container_width=True)
        row_3[1].plotly_chart(leads_by_location(df), use_container_width=True)

    if menu == "Marketing Attribution":
        df = get_filters_and_data(data)

        metrics = st.columns(5)
        metrics[0].metric(label="Total Leads", value=len(df))
        metrics[1].metric(label="Total Residential Units", value=round(df['Wohneinheiten'].sum()))
        metrics[2].metric(label="Total Commercial Units", value=round(df['Gewerbeeinheiten'].sum()))
        metrics[3].metric(label="Avg. Living Area (sq meters)", value=f"{df['Wohnflaeche'].mean():.2f}")
        metrics[4].metric(label="Avg. Lot Area (sq meters)", value=f"{df['Grundstueckflaeche'].mean():.2f}")

        row_1 = st.columns((4,3))
        row_1[0].plotly_chart(leads_registration_overtime(df), use_container_width=True)
        row_1[1].plotly_chart(conversion_channels_dist(df), use_container_width=True)

    if menu == "Property Breakdown":
        df = get_filters_and_data(data)

        row_1 = st.columns(2)
        row_1[0].plotly_chart(property_type_breakdown(df), use_container_width=True)
        row_1[1].plotly_chart(property_units_breakdown(df), use_container_width=True)


    if menu == "Geographic Analytics":
        df = get_filters_and_data(data)

        row_1 = st.columns((3,5))
        row_1[0].plotly_chart(geographic_listing_analytics(df), use_container_width=True)

        with row_1[1]:
            folium_static(leads_cluster_map(df), height=500)


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

                st.write("---")

        else:
            st.write("No properties found for the selected lead.")
