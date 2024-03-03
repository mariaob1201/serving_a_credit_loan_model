import streamlit as st
import pandas as pd
import logging


import numpy as np



coefficients = {
    "last_fico_range_low": -0.988587,
    "months_since_earliest_cr_line": 0.362007,
    "annual_inc": -0.253591,
    "dti": -0.531807,
    "mths_since_last_delinq": 1.845135,
    "term": -0.971275
}

user_input = {
    "last_fico_range_low": 500,
    "months_since_earliest_cr_line": 10,
    "annual_inc": 30000,
    "dti": 0.25,
    "mths_since_last_delinq": 2,
    "term": 60
}


def calculate_scaling_factor(target_range, logistic_scores):
    logistic_score_range = np.max(logistic_scores) - np.min(logistic_scores)
    return target_range / logistic_score_range

woe_values = {}
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
base_score = 700
logit_score = sum(-woe_values[var] * coefficients[var] for var in woe_values.keys())

# Your target range for credit scores (adjust as needed)
target_range = [300, 850]

logit_scores_dataset = logreg_model.decision_function(X_test)

# Find the minimum and maximum logistic scores in the dataset
min_logit_score = np.min(logit_scores_dataset)
max_logit_score = np.max(logit_scores_dataset)
# Calculate the scaling factor
scaling_factor = (target_range[1] - target_range[0]) / (max_logit_score - min_logit_score)

# Convert logistic score to credit score using the scorecard
credit_score = base_score + (scaling_factor * logit_score)

print(f"Credit Score: {credit_score:.2f}")



###################### REWARDS


st.sidebar.markdown("## Credit Score")
