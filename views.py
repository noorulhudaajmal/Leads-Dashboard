import pandas as pd
import streamlit as st
from filters import get_filters_and_data, get_lead_feature_filters
from streamlit_folium import folium_static
from plots import leads_by_location, property_type_breakdown, property_units_breakdown, lot_area_treemap, \
    residential_units_pie_chart, commercial_units_pie_chart, lead_count_pie_chart, features_map, property_condition_map, \
    conversion_channels_dist, features_table, leads_registration_overtime, geographic_listing_analytics, \
    leads_cluster_map, leads_features_heatmap, germany_feature_conditions_choropleth
from utils import get_lead_info, display_lead_metrics, \
    get_lead_location_info, format_date, display_plot_metrics
from css.streamlit_ui import main_styles, inner_styles, feature_html

import plotly.express as px
import plotly.graph_objects as go



def summary_view(data):
    df = get_filters_and_data(data)

    metrics = st.columns(6)
    metrics[0].metric(label="Total Leads", value=len(df))
    metrics[1].metric(label="Total Residential Units", value=round(df['Wohneinheiten'].sum()))
    metrics[2].metric(label="Total Commercial Units", value=round(df['Gewerbeeinheiten'].sum()))
    metrics[3].metric(label="Avg. Living Area (sq meters)", value=f"{df['Wohnflaeche'].mean():.2f}")
    metrics[4].metric(label="Avg. Lot Area (sq meters)", value=f"{df['Grundstueckflaeche'].mean():.2f}")
    metrics[5].metric(label="Avg. No. of Rooms", value=f"{round(df['Zimmeranzahl'].mean())}")

    row_2 = st.columns(3)
    row_2[0].plotly_chart(lead_count_pie_chart(df), use_container_width=True)
    row_2[1].plotly_chart(residential_units_pie_chart(df), use_container_width=True)
    row_2[2].plotly_chart(commercial_units_pie_chart(df), use_container_width=True)

    row_3 = st.columns((4, 3))
    row_3[0].plotly_chart(lot_area_treemap(df), use_container_width=True)
    row_3[1].plotly_chart(leads_by_location(df), use_container_width=True)

    st.write("---")
    st.write("#### Average Feature Usage")
    filter_by = st.columns(6)[0].selectbox(label="Analyze by", options=['State', 'City', 'Postal Code'])
    filter_map = {'State': 'bundesland', 'City': 'Ort', 'Postal Code': 'Postleitzahl_2'}
    filter_var = filter_map.get(filter_by)
    st.plotly_chart(leads_features_heatmap(df, filter_var), use_container_width=True)


def marketing_attribution_view(data):
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


def property_breakdown_view(data):
    df = get_filters_and_data(data)

    row_1 = st.columns(2)
    row_1[0].plotly_chart(property_type_breakdown(df), use_container_width=True)
    row_1[1].plotly_chart(property_units_breakdown(df), use_container_width=True)


def geographic_analytics_view(data):
    df = get_filters_and_data(data)

    row_1 = st.columns((3,5))
    row_1[0].plotly_chart(geographic_listing_analytics(df), use_container_width=True)

    with row_1[1]:
        folium_static(leads_cluster_map(df), height=500, width=1000)

    st.plotly_chart(germany_feature_conditions_choropleth(df), use_container_width=True)



def display_lead_info(filtered_data):
    st.write("#### ")
    if not filtered_data.empty:
        filtered_data = filtered_data.sort_values(by=['Email', 'Id'])
        for lead_email in filtered_data['Email'].unique():
            temp_df = filtered_data[filtered_data['Email'] == lead_email]
            name, email, phone = get_lead_info(temp_df)
            st.columns(4)[0].info(f"""👤 {name}  
                                          📧 {email}  
                                          📞 {phone}""")
            for idx, row in temp_df.iterrows():
                display_property_info(row, idx)
                st.write("# ")
                # st.write("---")

            st.write("---")
            st.write("# ")
    else:
        st.write("No properties found for the selected lead.")


def display_property_info(row, idx):
    name_row = st.columns((2, 2, 1, 1))
    name_row[0].write(f"### Property Listing no. {idx}")
    name_row[1].success(get_lead_location_info(row))
    name_row[2].success(f"##### {row['Quelle']}", icon="🔗")
    name_row[3].success(f"##### {format_date(row['Created_at'])}", icon="📅")

    display_lead_metrics(row)

    main_info = st.columns(3)
    with main_info[0]:
        with st.expander("Nachricht 💬"):
            field_value = row['Nachricht']
            st.write(field_value if not pd.isnull(field_value) else "No Message")
    with main_info[2]:
        with st.expander("Defect Information 🚨"):
            field_value = row['Schaeden/Maengel']
            st.write(field_value if not pd.isnull(field_value) else "No Defect.")
    with main_info[1]:
        with st.expander("Informationen zu besonderen Rechten 📄"):
            field_value = row['Informationen zu besonderen Rechten']
            st.write(field_value if not pd.isnull(field_value) else "No Info")

    display_property_details(row)

def display_property_details(row):
    property_type = 'No Info' if pd.isnull(row['Objekttyp']) else row['Objekttyp']
    house_type = 'No Info' if pd.isnull(row['Haustyp']) else row['Haustyp']
    house_condition = 'No Info' if pd.isnull(row['Objektzustand']) else row['Objektzustand']
    house_equip = 'No Info' if pd.isnull(row['Ausstattung']) else row['Ausstattung']
    house_use = 'No Info' if pd.isnull(row['Aktuelle Nutzung']) else row['Aktuelle Nutzung']
    attachment_info = 'No Info' if pd.isnull(row['Anhaenge/Dateien']) else row['Anhaenge/Dateien']

    row_2 = st.columns((2, 2, 2))
    with row_2[0]:
        col1, col2 = st.columns(2)
        col1.markdown(feature_html.format("Property Type", "🏠", property_type), unsafe_allow_html=True)
        col1.markdown(feature_html.format("House Type", "🏘️", house_type), unsafe_allow_html=True)
        col1.markdown(feature_html.format("House Condition", "📄", house_condition), unsafe_allow_html=True)
        col2.markdown(feature_html.format("Equipment", "⚙️", house_equip), unsafe_allow_html=True)
        col2.markdown(feature_html.format("House Use", "🔑", house_use), unsafe_allow_html=True)
        col2.markdown(feature_html.format("Files Attached", "📁", attachment_info), unsafe_allow_html=True)

    row_2[1].plotly_chart(features_table(row), use_container_width=True)
    row_2[2].plotly_chart(property_condition_map(row), use_container_width=True)


def features_view(data):
    filtered_data = get_lead_feature_filters(data)
    display_lead_info(filtered_data)