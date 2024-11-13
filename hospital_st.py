import streamlit as st
import hashlib
from pymongo import MongoClient
import pandas as pd

# MongoDB connection (Assuming MongoDB is running on localhost)
client = MongoClient("mongodb://localhost:27017/")  # Adjust the URI if necessary
db = client["hospital_finder"]
hospital_collection = db["hospitals"]
user_alerts_collection = db["alerts"]

# Function to hash passwords (for security)
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Signup page with additional hospital details
def hospital_signup():
    st.title("Hospital Signup")
    
    hospital_name = st.text_input("Hospital Name")
    location = st.text_input("Location")
    availability = st.selectbox("Availability", ["Available", "Not Available"])
    email = st.text_input("Unique Email ID")
    latitude = st.text_input("Latitude")
    longitude = st.text_input("Longitude")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    
    # Password confirmation check
    if password != confirm_password:
        st.error("Passwords do not match!")
    
    if st.button("Sign Up"):
        # Check if username or email already exists in MongoDB
        if hospital_collection.find_one({"username": username}):
            st.error("Username already taken.")
        elif hospital_collection.find_one({"email": email}):
            st.error("Email ID already registered.")
        else:
            # Store hospital details in MongoDB (password hashed)
            hospital_data = {
                "name": hospital_name,
                "location": location,
                "availability": availability,
                "email": email,
                "latitude": latitude,
                "longitude": longitude,
                "username": username,
                "password": hash_password(password)
            }
            hospital_collection.insert_one(hospital_data)
            st.success("Hospital successfully registered!")

# Login page
def hospital_login():
    st.title("Hospital Dashboard Login")
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        # Check if username exists and password matches
        hospital = hospital_collection.find_one({"username": username})
        if not hospital:
            st.error("Username not found!")
        elif hospital["password"] != hash_password(password):
            st.error("Incorrect password!")
        else:
            st.success("Login successful!")
            hospital_dashboard(username)

# Hospital Dashboard (after login)
def hospital_dashboard(username):
    st.title("Hospital Dashboard")
    
    # Show alerts from users
    st.subheader("User Alerts")
    alerts_cursor = user_alerts_collection.find()  # Fetch alerts from MongoDB
    alerts_list = list(alerts_cursor)
    alerts_df = pd.DataFrame(alerts_list)
    st.dataframe(alerts_df)
    
    # Option to update hospital credentials
    update_credentials = st.checkbox("Update Hospital Credentials")
    
    if update_credentials:
        st.subheader("Update Credentials")
        new_username = st.text_input("New Username", value=username)
        new_password = st.text_input("New Password", type="password")
        confirm_new_password = st.text_input("Confirm New Password", type="password")
        
        if new_password != confirm_new_password:
            st.error("Passwords do not match!")
        
        if st.button("Update Credentials"):
            # Update hospital username and/or password in MongoDB
            if new_username != username:
                hospital_collection.update_one(
                    {"username": username},
                    {"$set": {"username": new_username, "password": hash_password(new_password)}}
                )
                st.success("Credentials updated successfully!")
            else:
                hospital_collection.update_one(
                    {"username": username},
                    {"$set": {"password": hash_password(new_password)}}
                )
                st.success("Password updated successfully!")

# Main function to manage the flow
def main():
    st.sidebar.title("Hospital App")
    
    choice = st.sidebar.selectbox("Choose an action", ["Login", "Signup"])

    if choice == "Signup":
        hospital_signup()
    else:
        hospital_login()

# Run the app
if __name__ == "__main__":
    main()