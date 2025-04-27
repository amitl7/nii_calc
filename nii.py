import pandas as pd 
import datetime as dt
import numpy as np
# assumptons
# revieve interest monthly

# define the parameters
# date: 
start_date = "2025-01-01"
end_date = "2025-12-31"
ir_rate = 5
pv = 5000
pmt = 250

def date_convert(date_input):
    if isinstance(date_input, str):
        return dt.datetime.strptime(date_input, "%Y-%m-%d")
    elif isinstance(date_input, dt.date):
        return dt.datetime.combine(date_input, dt.time.min)
    elif isinstance(date_input, dt.datetime):
        return date_input
    else:
        raise TypeError("Input must be a string, date, or datetime object.")

def period_converter(start_date, end_date):
    # Convert string dates to datetime objects
    start = date_convert(start_date)
    end = date_convert(end_date)
    # Calculate the difference in months
    months = (end.year - start.year) * 12 + (end.month - start.month)
    return months

def fixed_rate(pv,ir_rate,start_date, end_date):
    
    period = period_converter(start_date,end_date)

    fv = pv *(1 + (ir_rate/100))** (period / 12)
    total_ir_earned = (fv-pv)
    monthly_ir_earned = total_ir_earned / period
    monthly_ir_rate = monthly_ir_earned / pv 

    cf = pd.DataFrame({
        "period": range(1, period + 1),
        "date": pd.date_range(start=start_date, periods=period, freq='MS').strftime("%Y-%m"),
        "start_balance": round(pv,2),
        "pmt": 0,
        "monthly_ir_rate": round(monthly_ir_rate,4),
        "monthly_ir_earned": round(monthly_ir_earned,2)
        })
    cf["end_balance"] = cf.monthly_ir_earned + cf["end_balance"].shift(1).fillna(cf.start_balance[0]) 

    return cf 

def regular_saver(pmt,start_date, end_date,ir_rate):
    pmt = pmt
    period = period_converter(start_date, end_date) + 2
    monthly_ir_rate = (1+ (ir_rate/100))**(1/12) -1

    cf = pd.DataFrame({
    "period": range(1, period + 1),
    "date": pd.date_range(start=start_date, periods=period, freq='MS').strftime("%Y-%m"),
    "start_balance": [0.0] * period,
    "pmt": [pmt] * (period - 1) + [0],  # last month is interest-only
    "monthly_ir_rate": [round(monthly_ir_rate, 4)] * period,
    "monthly_ir_earned": [0.0] * period,
    "end_balance": [0.0] * period
})
    
    for i in cf.index:
        
        if i == 0:
            cf.at[i, 'start_balance'] = 0
            cf.at[i,'monthly_ir_earned'] = 0
   
        else:
            cf.at[i, 'start_balance'] = cf.at[i - 1, 'end_balance']
        
        cf.at[i, 'monthly_ir_earned'] = round(cf.at[i,'start_balance'] * monthly_ir_rate,2)
        cf.at[i, 'end_balance'] = cf.at[i, 'start_balance'] + cf.at[i, 'pmt'] + cf.at[i, 'monthly_ir_earned']

    return cf 




def variable_rate():
    # just assume that the rate stays the same as fixed. 
    pass


