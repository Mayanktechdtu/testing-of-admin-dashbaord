import streamlit as st
from datetime import datetime
import sqlite3

# Connect to the SQLite database (creates the file if it doesn’t exist)
conn = sqlite3.connect('/tmp/clients.db')
cursor = conn.cursor()

# Create the clients table if it doesn’t exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS clients (
        username TEXT PRIMARY KEY,
        password TEXT,
        expiry_date TEXT,
        permissions TEXT
    )
''')
conn.commit()

# Functions to manage clients in the database
def add_client(username, password, expiry_date, permissions):
    permissions_str = ','.join(permissions)
    cursor.execute('''
        INSERT INTO clients (username, password, expiry_date, permissions)
        VALUES (?, ?, ?, ?)
    ''', (username, password, expiry_date, permissions_str))
    conn.commit()

def get_client(username):
    cursor.execute('SELECT * FROM clients WHERE username = ?', (username,))
    client = cursor.fetchone()
    if client:
        return {
            'username': client[0],
            'password': client[1],
            'expiry_date': client[2],
            'permissions': client[3].split(',')
        }
    return None

def update_client(username, password, expiry_date, permissions):
    permissions_str = ','.join(permissions)
    cursor.execute('''
        UPDATE clients
        SET password = ?, expiry_date = ?, permissions = ?
        WHERE username = ?
    ''', (password, expiry_date, permissions_str, username))
    conn.commit()

def delete_client(username):
    cursor.execute('DELETE FROM clients WHERE username = ?', (username,))
    conn.commit()

# Admin Dashboard
def admin_dashboard():
    st.title("Admin Dashboard")
    st.write("Manage clients, expiry dates, and dashboard permissions.")

    # Section 1: View all clients
    cursor.execute('SELECT * FROM clients')
    clients = cursor.fetchall()
    st.write("### Current Clients:")
    if clients:
        for client in clients:
            st.write(f"**Client:** {client[0]} | **Expiry Date:** {client[2]} | **Dashboards Access:** {client[3]}")
    else:
        st.write("No clients added yet.")
    
    st.write("---")
    
    # Section 2: Add a new client
    new_username = st.text_input("Enter new client's username:")
    new_password = st.text_input("Enter new client's password:", type="password")
    expiry_date = st.date_input(f"Set expiry date for {new_username}", value=datetime(2024, 12, 31))
    dashboards = st.multiselect("Dashboards:", ['dashboard1', 'dashboard2', 'dashboard3', 'dashboard4', 'dashboard5', 'dashboard6'])
    
    if st.button(f"Add Client {new_username}"):
        if new_username and new_password:
            add_client(new_username, new_password, expiry_date.strftime('%Y-%m-%d'), dashboards)
            st.success(f"Client '{new_username}' added successfully!")
        else:
            st.error("Please provide both a username and password.")

    st.write("---")

    # Section 3: Update or delete existing client
    selected_client = st.selectbox("Select a client to update or delete:", ["Select"] + [client[0] for client in clients])
    
    if selected_client != "Select":
        client_data = get_client(selected_client)
        update_password = st.text_input(f"Update password for {selected_client}:", type="password", value=client_data['password'])
        update_expiry_date = st.date_input(f"Update expiry date for {selected_client}", value=datetime.strptime(client_data['expiry_date'], '%Y-%m-%d'))
        update_dashboards = st.multiselect(f"Update dashboards for {selected_client}:", ['dashboard1', 'dashboard2', 'dashboard3', 'dashboard4', 'dashboard5', 'dashboard6'], default=client_data['permissions'])

        if st.button(f"Update Client {selected_client}"):
            update_client(selected_client, update_password, update_expiry_date.strftime('%Y-%m-%d'), update_dashboards)
            st.success(f"Client '{selected_client}' updated successfully!")

        if st.button(f"Delete Client {selected_client}"):
            delete_client(selected_client)
            st.success(f"Client '{selected_client}' deleted successfully!")

# Run the admin dashboard
if __name__ == "__main__":
    admin_dashboard()
