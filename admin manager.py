import streamlit as st
from datetime import datetime
import json

# Load user data from a JSON file
def load_user_data():
    try:
        with open('user_data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Save user data to a JSON file
def save_user_data(users):
    with open('user_data.json', 'w') as f:
        json.dump(users, f, indent=4)

# Load existing users or initialize an empty dictionary
users = load_user_data()

# Admin Dashboard: Manage Clients, Expiry Dates, and Permissions
def admin_dashboard():
    st.title("Admin Dashboard")
    st.write("Manage your clients, their credentials, expiry dates, and dashboard permissions.")

    # Section 1: View all clients
    st.write("### Current Clients:")
    if users:
        for username, data in users.items():
            st.write(f"**Client:** {username} | **Expiry Date:** {data['expiry_date']} | **Dashboards Access:** {', '.join(data['permissions'])}")
    else:
        st.write("No clients added yet.")
    
    st.write("---")
    
    # Section 2: Add a new client with manual username, password input
    st.write("### Add New Client")
    new_username = st.text_input("Enter new client's username:")
    new_password = st.text_input("Enter new client's password:", type="password")
    expiry_date = st.date_input(f"Set expiry date for {new_username}", value=datetime(2024, 12, 31))

    # Grant dashboard permissions
    st.write("Select dashboards for this client:")
    dashboards = st.multiselect("Dashboards:", ['dashboard1', 'dashboard2', 'dashboard3', 'dashboard4', 'dashboard5', 'dashboard6'])
    
    if st.button(f"Add Client {new_username}"):
        if new_username and new_password:
            # Save client data in users dictionary
            users[new_username] = {
                'password': new_password,
                'role': 'client',
                'expiry_date': expiry_date.strftime('%Y-%m-%d'),
                'permissions': dashboards
            }
            # Save the updated users dictionary to the JSON file
            save_user_data(users)
            st.success(f"Client '{new_username}' added successfully!")
        else:
            st.error("Please provide both a username and password.")

    st.write("---")

    # Section 3: Update or delete existing client
    st.write("### Update or Delete Existing Client")
    selected_client = st.selectbox("Select a client to update or delete:", ["Select"] + list(users.keys()))
    
    if selected_client != "Select":
        # Display current details
        client_data = users[selected_client]
        st.write(f"**Current Expiry Date:** {client_data['expiry_date']}")
        st.write(f"**Current Dashboards Access:** {', '.join(client_data['permissions'])}")

        # Update client details
        update_password = st.text_input(f"Update password for {selected_client}:", type="password", value=client_data['password'])
        update_expiry_date = st.date_input(f"Update expiry date for {selected_client}", value=datetime.strptime(client_data['expiry_date'], '%Y-%m-%d'))

        # Update dashboard permissions
        update_dashboards = st.multiselect(f"Update dashboards for {selected_client}:", ['dashboard1', 'dashboard2', 'dashboard3', 'dashboard4', 'dashboard5', 'dashboard6'], default=client_data['permissions'])

        if st.button(f"Update Client {selected_client}"):
            # Save updated client data
            users[selected_client]['password'] = update_password
            users[selected_client]['expiry_date'] = update_expiry_date.strftime('%Y-%m-%d')
            users[selected_client]['permissions'] = update_dashboards
            save_user_data(users)
            st.success(f"Client '{selected_client}' updated successfully!")

        # Option to delete client
        if st.button(f"Delete Client {selected_client}"):
            del users[selected_client]
            save_user_data(users)
            st.success(f"Client '{selected_client}' deleted successfully!")

# Run the admin dashboard
if __name__ == "__main__":
    admin_dashboard()
