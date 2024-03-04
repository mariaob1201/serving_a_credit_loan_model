import streamlit as st
import numpy as np
import pandas as pd
import logging

dft = pd.read_csv('params/databasefinal_creditscore_input.csv')
st.write(f"{dft.head(5)}")

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
        logging.info(f"here already ")
        dframe = dft.groupby(column_name + '_bins')[column_name + '_WOE'].mean().reset_index()
        logging.info('======================================', dframe)
        dframe['low'] = dframe[column_name + '_bins'].apply(lambda x: float(x.split(',').split('-')[0][1:]))
        dframe['upp'] = dframe[column_name + '_bins'].apply(lambda x: float(x.split(',').split('-')[1][:-1]))

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
    min_logit_score = np.percentile(logit_scores_test,10)
    max_logit_score = np.percentile(logit_scores_test,90)


    # Logistic function to convert log-odds to probability
    probability = 1 / (1 + np.exp(logit_score))


    # Calculate the scaling factor
    scaling_factor = calculate_scaling_factor(target_range[1] - target_range[0], logit_scores_test)
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