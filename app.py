import random
import streamlit as st
from functions import *



import streamlit as st


def address_to_location(address):
    try:
        from geopy.geocoders import Nominatim

        geolocator = Nominatim(user_agent="location_app")
        location = geolocator.geocode(address)
        return location
    except Exception as e:
        return None

def addresstolocation(address):

    if address:
        # Convert address to location
        location = address_to_location(address)

        if location:
            st.success(f"Location found for '{address}':")

            # Create a DataFrame with explicit latitude and longitude columns
            data = {'lat': [location.latitude], 'lon': [location.longitude]}
            df = pd.DataFrame(data)

            # Display the map with specified latitude and longitude columns
            st.map(df, lat_column='lat', lon_column='lon')

            st.write(f"Latitude: {location.latitude}, Longitude: {location.longitude}")
        else:
            st.error(f"Unable to find location for '{address}'. Please enter a valid address.")


def settings_customer():
    inquiries = random.choices([0, 1, 2, 3, 5, 7, 10],
                           weights=[0.6, 0.2, 0.05, 0.05, 0.05, 0.04, 0.01])[0]
    credit_score_months = random.choices([37, 50, 60, 80, 110, 150, 350],
                           weights=[0.6, 0.2, 0.05, 0.05, 0.05, 0.04, 0.01])[0]
    dti_r = random.choices(['Low', 'Mid', 'High'],
                           weights=[0.3, .45, .25])[0]
    # Generate random credit history values
    if inquiries >= 2:
        ficoscore = random.randint(550, 650)
    elif inquiries == 1:
        ficoscore = random.randint(650, 700)
    else:
        ficoscore = random.randint(700, 850)

    if dti_r == 'Low':
        dti = random.uniform(0, 20)
    elif dti_r == 'Mid':
        dti = random.uniform(20, 40)
    else:
        dti = random.uniform(40, 100)

    return inquiries, credit_score_months, dti, ficoscore

def main():
    # Page title
    st.title("CreditN")
    st.sidebar.title("Form:")

    # Add a JPG image to the Streamlit app
    image_path = "ninja.png"
    st.image(image_path, caption='CreditN', width=100)

    # Link to external CSS file
    css_styles = """
        body {
            font-family: Arial, sans-serif;
            background-color: #f0f0f0;
            color: #333;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #fff;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }

        h1 {
            font-size: 28px;
            font-weight: bold;
            color: #007bff;
            margin-bottom: 20px;
        }

        """

    # Embed CSS styles using HTML
    st.markdown(f"<style>{css_styles}</style>", unsafe_allow_html=True)

    # User input for name, address, and purpose
    name = st.sidebar.text_input("What's your name?")
    address = st.sidebar.text_input("What is your address?")
    purpose = st.sidebar.text_input("What is your purpose for using this loan?")

    # Welcome message
    if name:
        regards = f"Hello, {name}, welcome to our site!"
    else:
        regards = 'Hello!'
    st.write(f"{regards}")

    msg = "Welcome to CreditN platform where we evaluate your request for an installment credit in a matter of minutes." \
          " We utilize the FICO score as one of our predictive inputs. No sociodemographic data is used in this evaluation " \
          "but just as informative for a better experience for our clients."
    st.write(f"{msg}")

    # User input for loan term, amount, and annual income
    loan_term_s = st.sidebar.radio("Select loan term:", ["36 mo", "60 mo"])

    inquiries, credit_score_months, dti, ficoscore = settings_customer()

    loanamount = st.sidebar.number_input("Enter the loan amount you are looking for:")
    annual_income = st.sidebar.number_input("Enter your annual income:")

    # Check loan and income conditions
    if annual_income > 0 and loanamount > 0:

        # Display a button to submit the form
        if st.button("Submit"):
            st.write("We are looking at your credit history!")
            term = 36 if '60' not in loan_term_s else 60
            # Create user input dictionary
            user_input = {'term': term,
                          "last_fico_range_high": ficoscore,
                          "months_since_earliest_cr_line": credit_score_months,
                          "dti": dti,
                          "inq_last_12m": inquiries}

            # Evaluate and display results
            out = evaluating(user_input)
            custom_output(out, purpose, name, term, loanamount)

if __name__ == "__main__":
    main()