import pandas as pd
import streamlit as st
from filters import get_filters_and_data
from streamlit_folium import folium_static
from plots import leads_by_location, property_type_breakdown, property_units_breakdown, lot_area_treemap, \
    residential_units_pie_chart, commercial_units_pie_chart, lead_count_pie_chart, features_map, property_condition_map, \
    conversion_channels_dist, features_table, leads_registration_overtime, geographic_listing_analytics, \
    leads_cluster_map
from utils import get_lead_info, display_lead_metrics, \
    get_lead_location_info, format_date, display_plot_metrics
from css.streamlit_ui import main_styles, inner_styles, feature_html


def summary_view(data):
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
        folium_static(leads_cluster_map(df), height=500)


def features_view(data):
    filters_row = st.columns((2,4,2))
    selected_email = filters_row[0].selectbox("Select Email", data['Email'].unique())
    filtered_data = data[(data['Email'] == selected_email)]
    name, email, phone = get_lead_info(filtered_data)
    filters_row[2].info(f"""👤 {name}  
                                📧 {email}  
                                📞 {phone}"""
                        )
    if not filtered_data.empty:
        filtered_data = filtered_data.sort_values(by='Baujahr')
        for idx, row in filtered_data.iterrows():
            name_row = st.columns((2,2,1,1))
            name_row[0].write(f"### Property Listing no. {idx}")
            name_row[1].success(get_lead_location_info(row))
            name_row[2].success(f"#####     {row['Quelle']}", icon="🔗")
            name_row[3].success(f"#####     {format_date(row['Created_at'])}", icon="📅")

            display_lead_metrics(row)

            main_info = st.columns(3)
            with main_info[0]:
                with st.expander("Nachricht 💬"):
                    field_value = row['Nachricht']
                    if not pd.isnull(field_value):
                        st.write(f"""{field_value}""")
                    else:
                        st.write("No Message")
            with main_info[2]:
                with st.expander("Defect Information 🚨"):
                    field_value = row['Schaeden/Maengel']
                    if not pd.isnull(field_value):
                        st.write(f"""{field_value}""")
                    else:
                        st.write("No Defect.")
            with main_info[1]:
                with st.expander("Informationen zu besonderen Rechten 📄"):
                    field_value = row['Informationen zu besonderen Rechten']
                    if not pd.isnull(field_value):
                        st.write(f"""{field_value}""")
                    else:
                        st.write("No Info")

            info_row_3 = st.columns((1,3,3,3,3,3,1))
            property_type = 'No Info' if pd.isnull(row['Objekttyp']) else row['Objekttyp']
            info_row_3[1].markdown(feature_html.format("Property Type", "🏠", property_type), unsafe_allow_html=True)

            house_type = 'No Info' if pd.isnull(row['Haustyp']) else row['Haustyp']
            info_row_3[2].markdown(feature_html.format("House Type", "🏘️", house_type), unsafe_allow_html=True)

            house_condition = 'No Info' if pd.isnull(row['Objektzustand']) else row['Objektzustand']
            info_row_3[3].markdown(feature_html.format("House Condition", "📄", house_condition), unsafe_allow_html=True)

            house_equip = 'No Info' if pd.isnull(row['Ausstattung']) else row['Ausstattung']
            info_row_3[4].markdown(feature_html.format("Equipment", "⚙️", house_equip), unsafe_allow_html=True)

            house_use = 'No Info' if pd.isnull(row['Aktuelle Nutzung']) else row['Aktuelle Nutzung']
            info_row_3[5].markdown(feature_html.format("House Use", "🔑", house_use), unsafe_allow_html=True)


            st.write("### ")
            row_2 = st.columns((1,2,2))
            with row_2[0]:
                st.write("## Structural Overview")
                display_plot_metrics(row)
            row_2[1].plotly_chart(features_table(row), use_container_width=True)
            row_2[2].plotly_chart(property_condition_map(row), use_container_width=True)

            st.write("---")
            st.write("# ")

    else:
        st.write("No properties found for the selected lead.")