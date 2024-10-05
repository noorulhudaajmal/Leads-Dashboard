import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu as option_menu
from utils import process_data, save_data
from streamlit_gsheets import GSheetsConnection
from auth import authenticate_user, handle_authentication_status
from css.streamlit_ui import main_styles, inner_styles, feature_html
from views import features_view, geographic_analytics_view, property_breakdown_view, marketing_attribution_view, \
    summary_view

pd.options.mode.chained_assignment = None

# -------------------------Page Config----------------------------------------
st.set_page_config(page_title="Stock Analysis", layout="wide")

# -------------------------CSS Styling----------------------------------------
with open("css/style.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

st.markdown(main_styles, unsafe_allow_html=True)

# # ------------------------------- Data -----------------------------------------
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
    # menu_options = ['Overview', 'Marketing Attribution', 'Property Breakdown',
    #                 'Geographic Analytics', 'Leads Features', 'Update Leads']
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
        summary_view(data)

    if menu == "Marketing Attribution":
        marketing_attribution_view(data)

    if menu == "Property Breakdown":
        property_breakdown_view(data)

    if menu == "Geographic Analytics":
        geographic_analytics_view(data)

    if menu == "Leads Features":
        features_view(data)

    if menu == "Update Leads":
        lead_id = st.columns((1,1,5))[1].selectbox(label="Lead Id", options=data['Id'].unique())

        df = data[data['Id']==lead_id]

        row_2 = st.columns((1,5,1))
        edited_data = row_2[1].data_editor(df.transpose(), num_rows="dynamic",
                                           use_container_width=True)
        new_data = edited_data.transpose()

        updated_data = data.copy()
        updated_data.loc[updated_data['Id'] == lead_id, new_data.columns] = new_data.values

        row_3 = st.columns((5,1,1))
        if row_3[1].button("Save Changes"):
            save_data(updated_data, conn)
            st.success("Data saved successfully!")
            st.rerun()

        st.write("---")
        st.subheader("Upload Leads Data")
        cols = st.columns(2)
        uploaded_file = cols[0].file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx"])

        if uploaded_file:
            if uploaded_file.name.endswith('.csv'):
                new_leads = pd.read_csv(uploaded_file)
            else:
                new_leads = pd.read_excel(uploaded_file)

            cols[1].dataframe(new_leads, use_container_width=True)

        if cols[0].button("Add") and uploaded_file:
            if all(col in data.columns for col in new_leads.columns):
                log_messages = []

                for index, row in new_leads.iterrows():
                    if row['Id'] in updated_data['Id'].values:
                        updated_data.loc[updated_data['Id'] == row['Id'], new_leads.columns] = row.values
                        log_messages.append(f"Updated Lead ID: {row['Id']}")
                    else:
                        updated_data = pd.concat([updated_data, pd.DataFrame([row])], ignore_index=True)
                        log_messages.append(f"Added Lead ID: {row['Id']}")


                save_data(updated_data, conn)
                cols[0].success("Leads data processed successfully!")

                st.subheader("Log:")
                for message in log_messages:
                    cols[0].info(message)

            else:
                st.error("Uploaded data columns do not match the existing data columns.")
        else:
            st.error("No data uploaded.")
