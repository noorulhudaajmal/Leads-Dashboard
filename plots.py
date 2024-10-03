import pandas as pd
import plotly.graph_objects as go


from utils import format_hover_layout

colors = ["#264653", "#2a9d8f", "#e9c46a", "#f4a261", "#e76f51", "#84a59d", "#006d77",
          "#f6bd60", "#90be6d", "#577590", "#e07a5f", "#81b29a", "#f2cc8f", "#0081a7"]

g_colors = {
    'Ja': "#0E9594",
    'Nein': "#127475",
    'Other': "#F5DFBB"
}

def leads_by_location(data):
    data['Postcode (first 2 digits)'] = data['Postleitzahl'].astype(str).str[:2]
    leads_by_postcode = data.groupby(['bundesland','Ort', 'Postcode (first 2 digits)'])['Id'].count().reset_index()
    leads_by_postcode.columns = ['State', 'City', 'Postcode', 'Number of Leads']
    leads_by_postcode = leads_by_postcode.sort_values(by='State')
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=list(leads_by_postcode.columns),
            font=dict(size=14, color='white', family='ubuntu'),
            fill_color='#264653',
            align=['center'],
            height=50
        ),
        cells=dict(
            values=[leads_by_postcode[K].tolist() for K in leads_by_postcode.columns],
            font=dict(size=12, color="black", family='ubuntu'),
            align=['center'],
            height=30
        ))]
    )
    fig.update_layout(
        title="Leads by Location",
        margin=dict(t=50, l=0, r=0, b=0),
        height=500
    )

    return fig


def property_type_breakdown(data):
    type_data = data.groupby(['Objekttyp', 'Haustyp'], observed=False)['Id'].count().reset_index()
    pivot_data = type_data.pivot(index='Objekttyp', columns='Haustyp', values='Id').fillna(0)

    fig = go.Figure()
    for i, house_type in enumerate(pivot_data.columns):
        fig.add_trace(go.Bar(
            x=pivot_data.index,
            y=pivot_data[house_type],
            name=house_type,
            marker_color=colors[i]
        ))

    fig.update_layout(
        title="Property Type Breakdown with House Types",
        xaxis_title="Property Type (Objekttyp)",
        yaxis_title="Number of Leads",
        barmode='stack',
        # legend_title="House Type (Haustyp)",
        legend=dict(orientation="h", xanchor='center', x=0.35, y=-0.25),
    )
    fig = format_hover_layout(fig)

    return fig


def property_units_breakdown(data):
    units_data = data.groupby('Objekttyp').agg({
        'Wohneinheiten': 'sum',
        'Gewerbeeinheiten': 'sum'
    }).reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=units_data['Objekttyp'],
        x=units_data['Wohneinheiten'],
        name='Residential Units (Wohneinheiten)',
        marker_color=colors[0],
        orientation='h'
    ))

    fig.add_trace(go.Bar(
        y=units_data['Objekttyp'],
        x=units_data['Gewerbeeinheiten'],
        name='Commercial Units (Gewerbeeinheiten)',
        marker_color=colors[1],
        orientation='h'
    ))

    fig.update_layout(
        title="Total Residential and Commercial Units by Property Type",
        xaxis_title="Property Type (Objekttyp)",
        yaxis_title="Total Units",
        barmode='stack',
        legend=dict(orientation="h", xanchor='center', x=0.25, y=-0.25),
    )
    fig = format_hover_layout(fig)

    return fig


def lot_area_treemap(data):
    city_lot_area = data.groupby('bundesland')['Grundstueckflaeche'].sum().reset_index()
    fig = go.Figure(go.Treemap(
        labels=city_lot_area['bundesland'],
        parents=[''] * len(city_lot_area),
        values=city_lot_area['Grundstueckflaeche'],
        textinfo='label+value',
        hoverinfo='label+value+percent entry',
    ))

    fig.update_layout(
        title="Sum of Lot Area by State",
        margin=dict(t=50, l=0, r=0, b=0),
        height=500
    )

    return fig


def lead_count_pie_chart(data):
    lead_data = data['Objekttyp'].value_counts().reset_index()
    lead_data.columns = ['Objekttyp', 'Lead Count']

    fig = go.Figure(go.Pie(
        labels=lead_data['Objekttyp'],
        values=lead_data['Lead Count'],
        textinfo='percent',
        hoverinfo='label+value',
        title="Property Type",
        marker=dict(colors=colors),
        hole=0.6,
        hovertemplate='<b>%{label}</b> <br>Total Properties= %{value} (%{percent})<extra></extra>',
    ))

    fig.update_layout(
        title="Property Type Distribution",
        legend=dict(orientation="h", xanchor='center', x=0.25, y=-0.15),
        margin=dict(t=50, l=0, r=0, b=0),
    )

    fig = format_hover_layout(fig)

    return fig


def residential_units_pie_chart(data):
    residential_data = data.groupby('Objekttyp')['Wohneinheiten'].sum().reset_index()
    residential_data = residential_data.sort_values(by='Wohneinheiten', ascending=False)

    fig = go.Figure(go.Pie(
        labels=residential_data['Objekttyp'],
        values=residential_data['Wohneinheiten'],
        textinfo='percent',
        hoverinfo='label+value',
        title="Residential Units",
        marker=dict(colors=colors),
        hole=0.6,
        hovertemplate='<b>%{label}</b> <br>Total Properties= %{value} (%{percent})<extra></extra>',
    ))

    fig.update_layout(
        title="Residential Units Distribution",
        legend=dict(orientation="h", xanchor='center', x=0.25, y=-0.15),
        margin=dict(t=50, l=0, r=0, b=0),
    )
    fig = format_hover_layout(fig)

    return fig


def commercial_units_pie_chart(data):
    commercial_data = data.groupby('Objekttyp')['Gewerbeeinheiten'].sum().reset_index()
    commercial_data = commercial_data.sort_values(by='Gewerbeeinheiten', ascending=False)
    fig = go.Figure(go.Pie(
        labels=commercial_data['Objekttyp'],
        values=commercial_data['Gewerbeeinheiten'],
        textinfo='percent',
        hoverinfo='label+value',
        title="Commercial Units",
        marker=dict(colors=colors),
        hole=0.6,
        hovertemplate='<b>%{label}</b> <br>Total Properties= %{value} (%{percent})<extra></extra>',
    ))

    fig.update_layout(
        title="Commercial Units Distribution",
        legend=dict(orientation="h", xanchor='center', x=0.25, y=-0.15),
        margin=dict(t=50, l=0, r=0, b=0),
    )
    fig = format_hover_layout(fig)

    return fig


def conversion_channels_dist(data):
    channel_counts = data['Quelle'].value_counts()

    fig = go.Figure(data=go.Pie(
        labels=channel_counts.index,
        values=channel_counts.values,
        textinfo='percent',
        hoverinfo='label+value',
        marker=dict(colors=colors[1:]),
        hovertemplate='<b>%{label}</b> <br>Total Conversions= %{value} (%{percent})<extra></extra>',
    ))

    fig = format_hover_layout(fig)
    fig.update_layout(
        title='Conversion Channels Distribution',
        legend=dict(orientation="h", xanchor='center', x=0.45, y=-0.15),
        margin=dict(t=50, l=0, r=0, b=0),
        height=350
    )

    return fig


def features_map(row):
    features = ['Gastwc', 'Vollvermietet', 'Balkon', 'Aufzug', 'Dachgeschoss', 'Keller',  'Bebaut', 'Alleinlage', 'Erschlossen']

    feature_values = {feature: row[feature] for feature in features}
    df = pd.DataFrame(list(feature_values.items()), columns=['Feature', 'Presence'])
    df['Presence'] = df['Presence'].fillna('Nein')
    df['Value'] = df['Presence'].map({'Ja': 1, 'Nein': -1})

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df['Feature'],
        y=df['Value'],
        marker=dict(color=df['Value'].map({1: "#588157", -1: "#e63946"})),
        text=df['Presence'],
        textposition='auto',
    ))

    fig.update_layout(
        title='Property Features',
        xaxis_title='Features',
        yaxis_title='',
        yaxis=dict(
            range=[-1, 1],
            tickvals=[1, -1],
            ticktext=['Ja', 'Nein'],
        ),
        showlegend=False,
    )

    return fig


def features_table(row):
    features = ['Gastwc', 'Vollvermietet', 'Balkon', 'Aufzug', 'Dachgeschoss', 'Keller', 'Bebaut', 'Alleinlage', 'Erschlossen']

    feature_values = {feature: row[feature] for feature in features}
    df = pd.DataFrame(list(feature_values.items()), columns=['Feature', 'Presence'])
    df['Presence'] = df['Presence'].fillna('Nein')  # Fill NaN with 'Nein'

    colors = df['Presence'].map({'Ja': '#a3b18a', 'Nein': '#f9844a'})

    fig = go.Figure(data=[go.Table(
        header=dict(values=['Feature', 'Presence'],
                    fill_color='#264653',
                    font=dict(size=14, color='white', family='ubuntu'),
                    height=50,
                    align='left'),
        cells=dict(values=[df['Feature'], df['Presence']],
                   fill_color=[['white'] * len(df), colors],
                   font=dict(size=14, color='black', family='ubuntu'),
                   height=35,
                   align='left'))
    ])
    fig.update_layout(title='Feature Presence Table',
                      margin=dict(t=50, l=0, r=0, b=0),
                      )

    return fig


def property_condition_map(row):
    features = ['Dach', 'Fenster', 'Leitungen', 'Heizung', 'Fassade', 'Badezimmer', 'Innenausbau', 'Grundrissgestaltung']

    feature_values = {feature: row[feature] for feature in features}

    for feature in features:
        if pd.isna(feature_values[feature]):
            feature_values[feature] = "keine"

    condition_mapping = {
        "0-5 Jahre": 1,
        "5-10 Jahre": 2,
        "10-15 Jahre": 3,
        "mehr als 15 Jahre": 4,
        "keine": 0
    }

    inverse_condition_mapping = {v: k for k, v in condition_mapping.items()}

    heatmap_values = [[condition_mapping[feature_values[feature]] for feature in features]]

    fig = go.Figure(data=go.Heatmap(
        z=heatmap_values,
        x=features,
        y=['Property'],
        colorscale=[
            [0, colors[0]],     #keine
            [0.25, colors[1]], #'0-5 Jahre'
            [0.5, colors[2]],  #5-10 Jahre
            [0.75, colors[3]], #10-15 Jahre
            [1, colors[4]]     #mehr als 15 Jahre
        ],
        colorbar=dict(
            title='Condition',
            tickvals=[0, 1, 2, 3, 4],
            ticktext=['keine', '0-5 Jahre', '5-10 Jahre', '10-15 Jahre', 'mehr als 15 Jahre']
        ),
        hoverongaps=False,
        hovertemplate='<b>%{x}</b> <br>%{customdata}<extra></extra>',
        customdata=[[inverse_condition_mapping[val] for val in row] for row in heatmap_values]
    ))

    fig.update_layout(
        title='Property Condition',
        xaxis_title='Features',
        yaxis_title='',
        yaxis=dict(showgrid=False, zeroline=False, showline=False),
        xaxis=dict(showgrid=False, zeroline=False, showline=False),
    )

    for i in range(len(features)):
        fig.add_shape(
            type='rect',
            x0=i - 0.5, x1=i + 0.5,
            y0=-0.5, y1=0.5,
            line=dict(color='white', width=1)
        )

    return fig


def leads_registration_overtime(data):
    data['Mon-Year'] = data['Created_at'].dt.strftime('%b-%Y')
    data = data.groupby('Mon-Year', observed=False)['Id'].count().reset_index()
    data = data.rename(columns={'Id': 'leads_count'})
    data['Mon-Year'] = pd.to_datetime(data['Mon-Year'], format='%b-%Y')

    data = data.sort_values(by='Mon-Year')
    data['Mon-Year'] = data['Mon-Year'].dt.strftime('%b-%Y')

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data['Mon-Year'],
        y=data['leads_count'],
        mode='lines+markers+text',
        text=data['leads_count'],
        textposition='top center',
        fill='tozeroy',
        fillcolor="#9CC1C1",
        line=dict(color='#094780', width=4),
        marker=dict(color='#094780', size=12),
        hovertemplate='Registered Leads= %{text}<extra></extra>',
    ))

    fig = format_hover_layout(fig)
    fig.update_layout(
        height=350,
        title="Leads Trend",
        xaxis_title="Time",
        yaxis_title="Leads Count",
        yaxis_range=[0, data['leads_count'].max() + 10],
    )

    return fig