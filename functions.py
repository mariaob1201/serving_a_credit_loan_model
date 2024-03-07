import random
import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json
import logging


# Read the CSV file
try:
    dft = pd.read_csv('params/final_database_formodel.csv')
    print(f"Here reading the input ")
except Exception as e:
    logging.error(f"----------------------------------- The exception is {e}")
    dft = None

st.write(dft)
file_path = 'params/params.json'
base_score = 600
scaling_factor = 22

# Read the JSON file and load its contents into a dictionary
with open(file_path, 'r') as file:
    coefficients = json.load(file)


my_list = ['Verified', 'Source Verified', 'Unverified']
random_verif = random.choice(my_list)

# Read the JSON file and load its contents into a dictionary
with open(file_path, 'r') as file:
    coefficients = json.load(file)


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
    if dft is not None:
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
    else:
        return -999

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

    logit_score = sum(-woe_values[var] * coefficients[var] for var in user_input.keys())
    #target_range = [600, 850]
    probability = 1 / (1 + np.exp(logit_score))
    credit_score = base_score + (scaling_factor * logit_score)

    output = {"Userinput": user_input,
              "Credit-ninja Score": credit_score,
              "Probability of default": probability,
              "logit_score": logit_score
              }

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