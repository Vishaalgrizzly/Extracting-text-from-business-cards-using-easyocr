import streamlit as st
import cv2
import time
import numpy as np
import easyocr
import mysql.connector
import pandas as pd
from mysql.connector import Error

# Connect to MySQL database
mydb = mysql.connector.connect(
    host="localhost",
    user="username",
    password="password",
    database="database name")

# Create a cursor object to execute SQL queries
mycursor = mydb.cursor()

# Create a table to store the business card information
mycursor.execute(
    "CREATE TABLE IF NOT EXISTS business1 (id INT AUTO_INCREMENT PRIMARY KEY, image LONGBLOB, name VARCHAR(255), job_title VARCHAR(255), address VARCHAR(255), postcode VARCHAR(255), phone VARCHAR(255), email VARCHAR(255), website VARCHAR(255), company_name VARCHAR(225))")

# Create an OCR object to read text from the image
reader = easyocr.Reader(['en'])

st.markdown(
    f"""
         <style>
         .stApp {{
             background-image: url("https://upload.wikimedia.org/wikipedia/commons/thumb/8/81/Portable_scanner_and_OCR_%28video%29.webm/1200px--Portable_scanner_and_OCR_%28video%29.webm.jpg");
             background-attachment: fixed;
             background-size: 
         }}
         </style>
         """,
    unsafe_allow_html=True

)
# displayed on the streamlit app
st.title(":Red[Streamlit app to extract text from images]")
progress_text = "Work in progress. Please wait."
my_bar = st.progress(0, text=progress_text)

for percent_complete in range(100):
    time.sleep(0.1)
    my_bar.progress(percent_complete + 1, text=progress_text)

# Create a file uploader widget
uploaded_file = st.file_uploader("Upload the image", type=["jpg", "jpeg", "png"])

# Create a sidebar menu with options to add, view, update, and delete business card information
menu = ['Upload', 'View the database', 'Update the database', 'Delete the entries']
choice = st.sidebar.selectbox("Choose the action", menu)

if choice == 'Upload':
    if uploaded_file is not None:
        # Read the image using OpenCV
        image = cv2.imdecode(np.fromstring(uploaded_file.read(), np.uint8), 1)
        # Display the uploaded image
        st.image(image, caption='Uploaded the image successfully', use_column_width=True)
        st.balloons()
        # Create a button to extract information from the image
        if st.button('Done'):
            st.balloons()
            # Call the function to extract the information from the image
            bounds = reader.readtext(image, detail=0)
            # Convert the extracted information to a string
            text = "\n".join(bounds)
            # Insert the extracted information and image into the database
            sql = "INSERT INTO business1(image, name, job_title, address, postcode, phone, email, website, company_name) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            retval, buffer = cv2.imencode('.jpg', image)
            val = (
            buffer.tobytes(), bounds[0], bounds[1], bounds[2], bounds[3], bounds[4], bounds[5], bounds[6], bounds[7])
            mycursor.execute(sql, val)
            mydb.commit()
            # Display a success message
            st.success("Information from image moved to the database.")
elif choice == 'View the database':
    # Display the stored business card information
    mycursor.execute("SELECT * FROM business1")
    result = mycursor.fetchall()
    df = pd.DataFrame(result,
                      columns=['id', 'image', 'name', 'job_title', 'address', 'postcode', 'phone', 'email', 'website',
                               'company_name'])
    st.write(df)

elif choice == 'Update the database':
    # Create a dropdown menu to select a business card to update
    mycursor.execute("SELECT id, name FROM business1")
    result = mycursor.fetchall()
    business_cards = {}
    for row in result:
        business_cards[row[1]] = row[0]
    selected_card_name = st.selectbox("Select a business card to update", list(business_cards.keys()))

    # Get the current information for the selected business card
    mycursor.execute("SELECT * FROM business1 WHERE name=%s", (selected_card_name,))
    result = mycursor.fetchone()

    # Display the current information for the selected business card
    st.write("Name:", result[2])
    st.write("Job Title:", result[3])
    st.write("Address:", result[4])
    st.write("Postcode:", result[5])
    st.write("Phone:", result[6])
    st.write("Email:", result[7])
    st.write("Website:", result[8])
    st.write("company_name:", result[9])

    # Get new information for the business card
    name = st.text_input("Name", result[2])
    job_title = st.text_input("Job Title", result[3])
    address = st.text_input("Address", result[4])
    postcode = st.text_input("Postcode", result[5])
    phone = st.text_input("Phone", result[6])
    email = st.text_input("Email", result[7])
    website = st.text_input("Website", result[8])
    company_name = st.text_input("Company Name", result[9])

    # Create a button to update the business card
    if st.button("Update Business Card"):
        # Update the information for the selected business card in the database
        mycursor.execute(
            "UPDATE business1 SET name=%s, job_title=%s, address=%s, postcode=%s, phone=%s, email=%s, website=%s, company_name=%s WHERE name=%s",
            (name, job_title, address, postcode, phone, email, website, company_name, selected_card_name))
        mydb.commit()
        st.success("Business card information updated in database.")
elif choice == 'Delete the entries':
    # Create a dropdown menu to select a business card to delete
    mycursor.execute("SELECT id, name FROM business1")
    result = mycursor.fetchall()
    business_cards = {}
    for row in result:
        business_cards[row[0]] = row[1]
    selected_card_id = st.selectbox("Select an image to delete", list(business_cards.keys()),
                                    format_func=lambda x: business_cards[x])

    # Get the name of the selected business card
    mycursor.execute("SELECT name FROM business1 WHERE id=%s", (selected_card_id,))
    result = mycursor.fetchone()
    selected_card_name = result[0]

    # Display the current information for the selected business card
    st.write("Name:", selected_card_name)
    # Display the rest of the information for the selected business card

    # Create a button to confirm the deletion of the selected business card
    if st.button("Delete Business Card"):
        mycursor.execute("DELETE FROM business1 WHERE name=%s", (selected_card_name,))
        mydb.commit()
        st.success("Business card information deleted from database.")
