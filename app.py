import random


import streamlit as st
import numpy as np
import pandas as pd
import logging

dft = pd.read_csv('params/final_database_formodel.csv')


coefficients = {'last_fico_range_high': -0.9802881227926592,
         'months_since_earliest_cr_line': 0.19950877324958569,
         'dti': -0.5582188013544902,
         'inq_last_12m': -0.6154840377547729,
         'term': -0.8695614957308108}

def calculate_scaling_factor(target_range, logistic_scores):
    logistic_score_range = np.max(logistic_scores) - np.min(logistic_scores)
    return target_range / logistic_score_range


def find_woe_for_value(input_value, column_name):
    # Convert the column to numeric (if not already)
    if column_name + '_bins' in dft.columns:
        #print(f"here already ")
        dframe = dft.groupby(column_name + '_bins')[column_name + '_WOE'].mean().reset_index()
        #st.write('======================================', dframe)
        dframe['low'] = dframe[column_name + '_bins'].apply(lambda x: float(x.split('-')[0][1:]) if '-0.01' not in x else 0.01)
        dframe['upp'] = dframe[column_name + '_bins'].apply(lambda x: float(x.split('-')[1][:-1]) if '-0.01' not in x else 624)
        #st.write('======================================', dframe)
        # print('1*****',dframe)
        result_row = dframe[dframe['upp'] > input_value]

        # print('2*****',result_row)
        result_row1 = result_row[result_row['low'] <= float(input_value)]
        # print('3*****',result_row1)
        if len(result_row1) > 0:
            r = result_row1[column_name + '_WOE'].values
            print(f"+++++++++++++++++++++ {r[0]} ++++++++++++++++++")
            return float(r[0])
        else:
            return 0
    else:
        print(f"The variable is not here")
        return 0


def probability(input, coefficients):
    tot = 0
    # print(f"This is the input {input}")
    for k, val in input.items():
        print(f"******************** {k}***  {val} *************************")
        if 'term' not in k:
            woe = find_woe_for_value(val, k)
        else:
            if val < 37:
                woe = 2.671585
            else:
                woe = 2.194182

        print(f" {woe * coefficients[k]} The woe is {woe}, {coefficients[k]}")

        tot += woe * coefficients[k]

        print(f"Accumulative tot: {tot} ")

    probabdefault = 1 / (1 + np.exp(-(tot)))

    return probabdefault


def evaluating(user_input):
    woe_values = {}

    # Calculate WOE values for each variable
    for k, val in user_input.items():
        print(f"******************** {k}***  {val} *************************")
        if 'term' not in k:
            woe = find_woe_for_value(val, k)
        else:
            if val < 37:
                woe = 2.671585
            else:
                woe = 2.194182

        print(f"******** {woe} ----- {coefficients[k]}")
        woe_values[k] = woe

    # Base score and logistic regression score
    base_score = 650
    logit_score = sum(-woe_values[var] * coefficients[var] for var in user_input.keys())

    target_range = [600, 850]


    # Find the minimum and maximum logistic scores in the test set
    #min_logit_score = np.percentile(logit_scores_test,10)
    #max_logit_score = np.percentile(logit_scores_test,90)


    # Logistic function to convert log-odds to probability
    probability = 1 / (1 + np.exp(logit_score))


    # Calculate the scaling factor
    scaling_factor = 10 #calculate_scaling_factor(target_range[1] - target_range[0], logit_scores_test)
    print(f"scaling_factor  {scaling_factor}")
    # Convert logistic score to credit score using the scorecard
    credit_score = base_score + (scaling_factor * logit_score)

    print(f"User input {user_input}")
    print(f"Credit-ninja Score: {credit_score:.2f}")
    print(f"Probability of default: {probability:.4f}")
    print(f"logit_score: {logit_score:.4f}")

    output = {"Userinput": user_input,
            "Credit-ninja Score":credit_score,
            "Probability of default":probability,
            "logit_score":logit_score}
    return output


def custom_output(results):
    # Extract user input details
    user_input = results['Userinput']
    term = user_input['term']
    fico_score = user_input['last_fico_range_high']
    months_since_cr_line = user_input['months_since_earliest_cr_line']
    credit_inquiries = user_input['inq_last_12m']
    ninja_score = results['Credit-ninja Score']

    # Display the summary
    st.title("Credit Approval Summary")

    # Display user input details
    st.write(f"Selected Term: {term} months")
    st.write(f"Last FICO Range High: {fico_score}")
    st.write(
        f"Months Since Earliest Credit Line: {months_since_cr_line // 12} years and {months_since_cr_line % 12} months")
    st.write(f"Number of Credit Inquiries in the Last 12 Months: {credit_inquiries}")

    # Display Credit-ninja Score and approval status
    st.write(f"Your Credit-ninja Score: {ninja_score:.2f}")
    if ninja_score>700:
        st.success("Congratulations You are approved!")
        amorurl = 'https://www.creditninja.com/amortization-calculator/'
        st.markdown(f"Click [here]({amorurl}) to visit the amortization table in our website.")
    else:
        st.success("Approval Status: We are sorry but we can not approve your request right now!")

    # Display additional information if needed
    st.write(f"Probability of Default: {results['Probability of default']:.4f}")
    #st.write(f"Logit Score: {results['logit_score']:.4f}")


def main():
    # Page title

    # Add a JPG image to the Streamlit app
    image_path = "images.png"
    st.image(image_path, caption='Credit Ninja', use_column_width=True)

    st.title("Credit Ninja")
    

    st.sidebar.title("Form:")

    # User input for name
    name = st.sidebar.text_input("What's your name?:")
    st.write(f"Hello, {name}, welcome to our site!")
    msg = "Welcome to credit ninja platform were we evaluate your request for an installment credit in the matter of minutes." \
          " We will utilize the fico score as one of our predictive inputs. No sociodemographic data is used in this evaluation " \
          "but just as informative for a better experience of our clients."

    st.write(f"{msg}")

    # User input for loan term
    loan_term = st.sidebar.slider("Select loan term (in months):", 12, 60, 36)

    term = [36 if loan_term<37 else 60][0]

    #st.write(f"You selected a loan term of {loan_term} months.")

    loanamount = st.sidebar.number_input("Enter the loan amount you are looking for please:")
    if loanamount>40000:
        st.write(f"The maximum loan is 40000 USD, please input other value!")

    annual_income = st.sidebar.number_input("Enter your annual income:")
    if annual_income<=20000 and annual_income>700000:
        st.write(f"Please provide a valid input!")

    # Display a button to submit the form
    if st.sidebar.button("Submit"):
        st.success("We are looking at your credit history!")

        probabilities = [0.7, 0.1, 0.05, 0.05,0.05,0.05]

        # Use random.choices to select a value based on the probabilities
        inquiries = random.choices([0, 1, 2, 3,5,7], weights=probabilities)[0]

        if inquiries>2:
            ficoscore = random.randint(600, 690)
        if inquiries ==1:
            ficoscore = random.randint(690, 720)
        else:
            ficoscore = random.randint(720, 850)
        credit_score_months = random.randint(37, 852)
        user_input = {'term': term,
                      "last_fico_range_high": ficoscore,
                      "months_since_earliest_cr_line": credit_score_months,
                      "dti": random.uniform(0, 100),
                      "inq_last_12m":inquiries
                      }

        out = evaluating(user_input)
        #st.write(f"Results {out}")
        custom_output(out)

if __name__ == "__main__":
    main()
