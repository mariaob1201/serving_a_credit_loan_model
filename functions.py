import pandas as pd


def find_woe_for_value(input_value, column_name):
    # Convert the column to numeric (if not already)
    if column_name + '_bins' in dfmodel.columns:
        print(f"here already ")
        dframe = dfmodel.groupby(column_name + '_bins')[column_name + '_WOE'].mean().reset_index()
        print('======================================', dframe)
        dframe['low'] = dframe[column_name + '_bins'].apply(lambda x: float(x.split(',')[0][1:]))
        dframe['upp'] = dframe[column_name + '_bins'].apply(lambda x: float(x.split(',')[1][:-1]))

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
    # f"The input value {input_value} belongs to the bin {result_row[column_name+'_bins'].values} with WOE value {resul}"
