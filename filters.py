import streamlit as st

def get_filters_and_data(data):
    n_filters = 5
    filters = st.columns(n_filters)

    selected_states = filters[0].multiselect(
        label="State(s)",
        options=data['bundesland'].unique(),
        placeholder='All'
    )

    if not selected_states:
        selected_states = data['bundesland'].unique()

    selected_property_types = filters[1].multiselect(
        label="Property Type(s)",
        options=data['Objekttyp'].unique(),
        placeholder='All'
    )

    if not selected_property_types:
        selected_property_types = data['Objekttyp'].unique()

    sale_guarantee = filters[4].multiselect(
        label="100-Tage-Verkaufsgarantie",
        options=data['100-Tage-Verkaufsgarantie'].unique(),
        placeholder='All'
    )

    if not sale_guarantee:
        sale_guarantee = data['100-Tage-Verkaufsgarantie'].unique()

    # Year of Construction filter
    year_options = sorted(data['Baujahr'].dropna().unique())
    selected_years = filters[2].multiselect(
        label="Year of Construction",
        options=year_options,
        placeholder='All'
    )

    if not selected_years:
        selected_years = year_options

    # Property Area filter
    living_area_options = sorted(data['property_area_range'].unique())
    selected_living_area = filters[3].multiselect(
        label="Property Area",
        options=living_area_options,
        placeholder='All'
    )

    if not selected_living_area:
        selected_living_area = living_area_options

    # Filter based on multiselect selections
    filtered_data = data[
        (data['bundesland'].isin(selected_states)) &
        (data['Objekttyp'].isin(selected_property_types)) &
        (data['100-Tage-Verkaufsgarantie'].isin(sale_guarantee)) &
        (data['Baujahr'].isin(selected_years)) &
        (data['property_area_range'].isin(selected_living_area))
        ]

    return filtered_data
