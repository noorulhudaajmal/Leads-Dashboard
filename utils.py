import hashlib
import pandas as pd
import streamlit as st
from datetime import datetime


def process_data(data):
    data = data.dropna(subset=['bundesland', 'Ort', 'Postleitzahl'])

    if data['Grundstueckflaeche'].isnull().any():
        mean_area = data['Grundstueckflaeche'].mean()
        data['Grundstueckflaeche'] = data['Grundstueckflaeche'].fillna(mean_area)

    data['Baujahr'] = pd.to_numeric(data['Baujahr'], errors='coerce')
    data['Baujahr'] = data['Baujahr'].dropna().astype(int).round()
    data = data[(data['Baujahr'] >= 1000) & (data['Baujahr'] <= 9999)]

    living_area_bins = [0, 800, 1100, 1300, 1500, 2000, 3000, 12900]
    living_area_labels = [
        'Up to 800 sqm',
        '800-1100 sqm',
        '1100-1300 sqm',
        '1300-1500 sqm',
        '1500-2000 sqm',
        '2000-3000 sqm',
        'Above 3000 sqm'
    ]
    data['property_area_range'] = pd.cut(data['Grundstueckflaeche'], bins=living_area_bins, labels=living_area_labels)
    data['Created_at'] = pd.to_datetime(data['Created_at'], errors='coerce')
    data['Postleitzahl_2'] = data['Postleitzahl'].apply(lambda x: f"DE-{x[-2:]}")
    return data


def format_hover_layout(fig):
    """
    Updates the layout of a Plotly figure

    Args:
        fig (Figure): The Plotly figure to update.

    Returns:
        Figure: The updated figure with updated hover-mode.
    """
    fig = fig.update_layout(
        height=400,
        hovermode="x unified",
        hoverlabel=dict(bgcolor="white", font_color="black",
                        font_size=12, font_family="Rockwell"),
        plot_bgcolor='rgba(255, 255, 255, 0.8)',
        paper_bgcolor='rgba(255, 255, 255, 0.8)',
        legend=dict(
            bgcolor='rgba(255, 255, 255, 0)',  # Transparent legend background
        ),
        xaxis=dict(
            showgrid=False,  # Hide x-axis gridlines
            zeroline=False,  # Hide x-axis zero line
        ),
        yaxis=dict(
            showgrid=False,  # Hide y-axis gridlines
            zeroline=False,  # Hide y-axis zero line
        )
    )

    return fig



def verify_password(input_password, stored_hashed_password):
    """
    Simulate bcrypt check using the password hash logic.
    """
    return input_password == stored_hashed_password
    # hashed_input = hashlib.sha256(input_password.encode()).hexdigest()
    # return hashed_input == stored_hashed_password



def get_lead_info(df):
    record = df.iloc[0]
    name = f"{record['Vorname']} {record['Nachname']}"
    email = record['Email']
    phone = record['Telefon']

    return name, email, phone


def display_lead_metrics(row):
    lot_area = round(row['Grundstueckflaeche']) if not pd.isna(row['Grundstueckflaeche']) else 0
    living_area = round(row['Wohnflaeche']) if not pd.isna(row['Wohnflaeche']) else 0
    business_area = round(row['Geschaeftsflaeche']) if not pd.isna(row['Geschaeftsflaeche']) else 0
    rental_income = row['Mieteinnahmen (Kaltmiete)'] if not pd.isna(row['Mieteinnahmen (Kaltmiete)']) else 0
    residential_units = row['Wohneinheiten'] if not pd.isna(row['Wohneinheiten']) else 0
    commercial_units = row['Gewerbeeinheiten'] if not pd.isna(row['Gewerbeeinheiten']) else 0
    num_floors = row['Etagenanzahl'] if not pd.isna(row['Etagenanzahl']) else 0
    num_rooms = row['Zimmeranzahl'] if not pd.isna(row['Zimmeranzahl']) else 0

    metrics_row = st.columns(9)
    metrics_row[0].metric(label="Year of Construction", value=round(row['Baujahr']))
    metrics_row[1].metric(label="Lot Area (sqm)", value=lot_area)
    metrics_row[2].metric(label="Living Area (sqm)", value=living_area)
    metrics_row[3].metric(label="Business Area (sqm)", value=business_area)
    metrics_row[4].metric(label="Rental Income", value=rental_income)
    metrics_row[5].metric(label="Residential Units", value=residential_units)
    metrics_row[6].metric(label="Commercial Units", value=commercial_units)
    metrics_row[7].metric(label="No. of Floors", value=num_floors)
    metrics_row[8].metric(label="No. of Rooms", value=num_rooms)


def display_plot_metrics(row):
    residential_units = row['Wohneinheiten'] if not pd.isna(row['Wohneinheiten']) else 0
    commercial_units = row['Gewerbeeinheiten'] if not pd.isna(row['Gewerbeeinheiten']) else 0
    num_floors = row['Etagenanzahl'] if not pd.isna(row['Etagenanzahl']) else 0
    num_rooms = row['Zimmeranzahl'] if not pd.isna(row['Zimmeranzahl']) else 0

    st.metric(label="Residential Units", value=residential_units)
    st.metric(label="Commercial Units", value=commercial_units)
    st.metric(label="Number of Floors", value=num_floors)
    st.metric(label="Number of Rooms", value=num_rooms)


def get_lead_location_info(row):
    """
    Generate a formatted address from the given row
    of data, including a clickable Google Maps link.
    """
    street = row['Strasse']
    postal_code = row['Postleitzahl']
    city = row['Ort']
    house_number = row['Hausnummer']
    state = row['bundesland']

    full_address = f"{street} {house_number}, {postal_code} {city}, {state}"
    google_maps_link = f"https://www.google.com/maps/search/?api=1&query={full_address.replace(' ', '+')}"

    formatted_address = f"""
    <div style="font-family: Arial, sans-serif; font-size: 14px;">
        <p> 📍 <a href="{google_maps_link}" target="_blank" style="text-decoration: none; color: blue;">{full_address}</a></p>
    </div>
    """
    formatted_address = f"📍 [{full_address}]({google_maps_link})\n"

    return formatted_address


def format_date(date_value):
    """
    Format the date from 'YYYY-MM-DD HH:MM:SS' to 'DDth Month, YYYY'
    """
    if isinstance(date_value, pd.Timestamp):
        date_obj = date_value.to_pydatetime()  # Convert Timestamp to datetime
    else:
        date_obj = datetime.strptime(date_value, "%Y-%m-%d %H:%M:%S")

    day = date_obj.day
    suffix = 'th' if 4 <= day <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
    formatted_day = f"{day}{suffix}"

    return f"{formatted_day} {date_obj.strftime('%b, %Y')}"


def save_data(df):
    # conn.update(data=df, worksheet='leads')
    df.to_csv("data/df.csv", index=False)
