import streamlit as st
from datetime import datetime
import sqlite3
import os

# Database connection
def get_db_connection():
    # Use /tmp/ for Streamlit Cloud (ephemeral file system)
    db_path = '/tmp/clients.db'
    conn = sqlite3.connect(db_path)
    return conn

# Create the clients table if it doesn’t exist
def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            username TEXT PRIMARY KEY,
            password TEXT,
            expiry_date TEXT,
            permissions TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Functions to manage clients in the database
def add_client(username, password, expiry_date, permissions):
    try:
        permissions_str = ','.join(permissions)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO clients (username, password, expiry_date, permissions)
            VALUES (?, ?, ?, ?)
        ''', (username, password, expiry_date, permissions_str))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error adding client: {e}")
        return False

def get_all_clients():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients')
    clients = cursor.fetchall()
    conn.close()
    return clients

def get_client(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients WHERE username = ?', (username,))
    client = cursor.fetchone()
    conn.close()
    if client:
        return {
            'username': client[0],
            'password': client[1],
            'expiry_date': client[2],
            'permissions': client[3].split(',')
        }
    return None

def update_client(username, password, expiry_date, permissions):
    try:
        permissions_str = ','.join(permissions)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE clients
            SET password = ?, expiry_date = ?, permissions = ?
            WHERE username = ?
        ''', (password, expiry_date, permissions_str, username))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error updating client: {e}")
        return False

def delete_client(username):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM clients WHERE username = ?', (username,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error deleting client: {e}")
        return False

# Admin Dashboard UI
def admin_dashboard():
    st.title("Admin Dashboard")
    st.write("Manage clients, expiry dates, and dashboard permissions.")

    # Section 1: View all clients
    st.write("### Current Clients:")
    clients = get_all_clients()
    if clients:
        for client in clients:
            st.write(f"**Client:** {client[0]} | **Expiry Date:** {client[2]} | **Dashboards Access:** {client[3]}")
    else:
        st.write("No clients added yet.")
    
    st.write("---")
    
    # Section 2: Add a new client
    st.write("### Add New Client:")
    new_username = st.text_input("Enter new client's username:")
    new_password = st.text_input("Enter new client's password:", type="password")
    expiry_date = st.date_input(f"Set expiry date for {new_username}", value=datetime(2024, 12, 31))
    dashboards = st.multiselect("Dashboards:", ['dashboard1', 'dashboard2', 'dashboard3', 'dashboard4', 'dashboard5', 'dashboard6'])
    
    if st.button(f"Add Client {new_username}"):
        if new_username and new_password:
            success = add_client(new_username, new_password, expiry_date.strftime('%Y-%m-%d'), dashboards)
            if success:
                st.success(f"Client '{new_username}' added successfully!")
                st.experimental_rerun()  # Refresh the page to show updated client list
        else:
            st.error("Please provide both a username and password.")

    st.write("---")

    # Section 3: Update or delete existing client
    st.write("### Update/Delete Client:")
    if clients:
        selected_client = st.selectbox("Select a client to update or delete:", ["Select"] + [client[0] for client in clients])
    
        if selected_client != "Select":
            client_data = get_client(selected_client)
            update_password = st.text_input(f"Update password for {selected_client}:", type="password", value=client_data['password'])
            update_expiry_date = st.date_input(f"Update expiry date for {selected_client}", value=datetime.strptime(client_data['expiry_date'], '%Y-%m-%d'))
            update_dashboards = st.multiselect(f"Update dashboards for {selected_client}:", ['dashboard1', 'dashboard2', 'dashboard3', 'dashboard4', 'dashboard5', 'dashboard6'], default=client_data['permissions'])

            if st.button(f"Update Client {selected_client}"):
                success = update_client(selected_client, update_password, update_expiry_date.strftime('%Y-%m-%d'), update_dashboards)
                if success:
                    st.success(f"Client '{selected_client}' updated successfully!")
                    st.experimental_rerun()  # Refresh the page to show updated client list

            if st.button(f"Delete Client {selected_client}"):
                success = delete_client(selected_client)
                if success:
                    st.success(f"Client '{selected_client}' deleted successfully!")
                    st.experimental_rerun()  # Refresh the page to show updated client list
    else:
        st.write("No clients available to update or delete.")

# Ensure the table is created before the app starts
create_table()

# Run the admin dashboard
if __name__ == "__main__":
    admin_dashboard()
