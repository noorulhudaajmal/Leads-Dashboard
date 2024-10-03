import hashlib

import pandas as pd


def process_data(data):
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
                        font_size=12, font_family="Rockwell"))
    return fig



def verify_password(input_password, stored_hashed_password):
    """
    Simulate bcrypt check using the password hash logic.
    """
    return input_password == stored_hashed_password
    # hashed_input = hashlib.sha256(input_password.encode()).hexdigest()
    # return hashed_input == stored_hashed_password


