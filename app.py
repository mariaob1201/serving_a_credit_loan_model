import random
import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json
# Read the CSV file
dft = pd.read_csv('params/final_database_formodel.csv')

file_path = 'params/params.json'

# Read the JSON file and load its contents into a dictionary
with open(file_path, 'r') as file:
    coefficients = json.load(file)


my_list = ['Verified', 'Source Verified', 'Unverified']
random_verif = random.choice(my_list)

def calculate_amortization_table(loan_amount, annual_interest_rate, loan_term):
    monthly_interest_rate = annual_interest_rate / 12 / 100
    monthly_payment = (loan_amount * monthly_interest_rate) / (1 - (1 + monthly_interest_rate) ** -loan_term)

    amortization_schedule = pd.DataFrame(columns=['No', 'Date', 'Payment', 'Principal', 'Interest', 'Remaining Balance'])
    remaining_balance = loan_amount
    current_date = datetime.now()

    for month in range(1, loan_term + 1):
        interest_payment = remaining_balance * monthly_interest_rate
        principal_payment = monthly_payment - interest_payment
        remaining_balance -= principal_payment

        current_date += timedelta(days=30)  # Add approximately one month

        row = {'No': month,
               'Date': current_date.strftime("%Y-%m-%d"),
               'Payment': monthly_payment,
               'Principal': principal_payment,
               'Interest': interest_payment,
               'Remaining Balance': remaining_balance}

        amortization_schedule = pd.concat([amortization_schedule, pd.DataFrame([row])], ignore_index=True)

    return amortization_schedule

def get_state_from_address(address):
    #geolocator = Nominatim(user_agent="state_emulator")
    try:
        location = geolocator.geocode(address, timeout=10)
        if location and 'address' in location.raw:
            state = location.raw['address'].get('state')
            return state
        else:
            return None
    except GeocoderTimedOut:
        print("Error: Geocoding service timed out.")
        return None
    except GeocoderServiceError as e:
        print(f"Error: {e}")
        return None

def calculate_scaling_factor(target_range, logistic_scores):
    logistic_score_range = np.max(logistic_scores) - np.min(logistic_scores)
    return target_range / logistic_score_range

def find_woe_for_value(input_value, column_name):
    if column_name + '_bins' in dft.columns:
        dframe = dft.groupby(column_name + '_bins')[column_name + '_WOE'].mean().reset_index()
        dframe['low'] = dframe[column_name + '_bins'].apply(lambda x: float(x.split('-')[0][1:]) if '-0.01' not in x else 0.01)
        dframe['upp'] = dframe[column_name + '_bins'].apply(lambda x: float(x.split('-')[1][:-1]) if '-0.01' not in x else 624)
        result_row = dframe[dframe['upp'] > input_value]
        result_row1 = result_row[result_row['low'] <= float(input_value)]
        if len(result_row1) > 0:
            r = result_row1[column_name + '_WOE'].values
            return float(r[0])
        else:
            return 0
    else:
        print(f"The variable is not here")
        return 0

def probability(input, coefficients):
    tot = 0
    for k, val in input.items():
        if 'term' not in k:
            woe = find_woe_for_value(val, k)
        else:
            woe = 2.671585 if val < 37 else 2.194182

        tot += woe * coefficients[k]

    probabdefault = 1 / (1 + np.exp(-(tot)))
    return probabdefault



def evaluating(user_input):
    woe_values = {}
    for k, val in user_input.items():
        if 'term' not in k:
            woe = find_woe_for_value(val, k)
        else:
            woe = 2.671585 if val < 37 else 2.194182

        woe_values[k] = woe

    base_score = 650
    logit_score = sum(-woe_values[var] * coefficients[var] for var in user_input.keys())
    target_range = [600, 850]
    probability = 1 / (1 + np.exp(logit_score))
    scaling_factor = 22
    credit_score = base_score + (scaling_factor * logit_score)

    output = {"Userinput": user_input,
              "Credit-ninja Score": credit_score,
              "Probability of default": probability,
              "logit_score": logit_score}
    return output

def generate_random_number():
    try:
        values = [20, 50, random.uniform(50, 100)]
        probabilities = [0.65, 0.25, 0.1]
        random_number = random.choices(values, probabilities)[0]
        return random_number
    except:
        return None

def custom_output(results, purpose, name, loan_term, loan_amount):
    try:
        user_input = results['Userinput']
        term = user_input['term']

        # Example usage
        rt = generate_random_number()
        ratio = np.round(rt, 2)
        fico_score = user_input['last_fico_range_high']
        months_since_cr_line = user_input['months_since_earliest_cr_line']
        credit_inquiries = user_input['inq_last_12m']
        ninja_score = results['Credit-ninja Score']

        # Display the summary
        st.title("Credit Approval Summary")

        # Display user input details
        st.write(f"Selected Term: {term} months")
        st.write(f"Last FICO Range High: {fico_score}")
        st.write(f"Your last Debt-to-Income ratio is: {ratio}, {['High' if ratio > 30 else ['Low' if ratio < 10 else 'Good'][0]][0]}")
        st.write(f"Months Since Earliest Credit Line: {months_since_cr_line // 12} years and {months_since_cr_line % 12} months")
        st.write(f"Number of Credit Inquiries in the Last 12 Months: {credit_inquiries}")

        if 'Un' in random_verif:
            st.write(f"Unverified income!")
        else:
            if 'Source' in random_verif:
                st.write(f"Your income source was verified!")
            else:
                st.write(f"Your income was verified!")

        # Check if the user is approved based on the CN Score
        if ninja_score > 700:
            st.success(f"Congratulations {name}, your CN Score is {ninja_score:.0f} and you are approved!")

            # Generate and display amortization table
            amortization_table = calculate_amortization_table(loan_amount, 8, loan_term)
            download_button = st.download_button(label="Download Amortization Table as CSV",
                                                 data=amortization_table.to_csv(index=False),
                                                 file_name="my_amortization_table.csv")

            # Display success message and download button
            st.write(f"You will be able to afford your goal already: {purpose}.")
            if download_button:
                st.success("Download successful!")

        else:
            # Display error message if the user is not approved
            st.error(f"Approval Status: We are sorry but we cannot approve your request right now! Your CN Score is: {ninja_score:.0f}")

    except Exception as e:
        print(f"Exception here {e}")

def main():
    # Page title
    st.title("CreditN")
    st.sidebar.title("Form:")

    # Add a JPG image to the Streamlit app
    image_path = "ninja.png"
    st.image(image_path, caption='CreditN', width=100)

    # User input for name, address, and purpose
    name = st.sidebar.text_input("What's your name?")
    address = st.sidebar.text_input("What is your address?")
    state = address[-3:] if address else None

    if state:
        pass
        #st.write(f"We have a lot of customers from {state}!")
    else:
        print("Unable to determine the state for the given address.")

    purpose = st.sidebar.text_input("What is your purpose for using this loan?")
    print('purpose ---', purpose)

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
    loan_term = 36 if '60' not in loan_term_s else 60
    term = loan_term

    loanamount = st.sidebar.number_input("Enter the loan amount you are looking for:")
    annual_income = st.sidebar.number_input("Enter your annual income:")

    # Check loan and income conditions
    if annual_income > 0 and loanamount > 0:
        label = True

        if loanamount > 40000:
            label = False
            st.write("The maximum loan is $40,000. Please enter a different value.")

        if 2000 < annual_income <= 700000:
            st.write("Please provide a valid income input.")
            label = False

        # Display a button to submit the form
        if st.button("Submit"):
            st.write("We are looking at your credit history!")

            # Generate random credit history values
            inquiries = random.choices([0, 1, 2, 3, 5, 7, 10], weights=[0.6, 0.2, 0.05, 0.05, 0.05, 0.04, 0.01])[0]

            if inquiries >= 2:
                ficoscore = random.randint(550, 650)
            elif inquiries == 1:
                ficoscore = random.randint(650, 700)
            else:
                ficoscore = random.randint(700, 850)

            credit_score_months = random.choices([37, 50, 60, 80, 110, 150, 350], weights=[0.6, 0.2, 0.05, 0.05, 0.05, 0.04, 0.01])[0]
            dti_r = random.choices(['Low','Mid','High'], weights=[0.3,.45,.25])[0]
            if dti_r=='Low':
                dti = random.uniform(0, 20)
            elif dti_r=='Mid':
                dti = random.uniform(20, 40)
            else:
                dti = random.uniform(40, 100)

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
