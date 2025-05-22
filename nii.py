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

def generate_starting_dates(start_date, period):
    actual_start = start_date if start_date is not None else dt.datetime.today()
    return pd.date_range(start=actual_start, periods=period, freq='MS').strftime("%Y-%m")


def fixed_rate(pv,ir_rate,start_date =None , end_date = None, period = None):
    
    if period is None or period == 0:
        period = period_converter(start_date,end_date)
        if period == 0:
            period = 1

    fv = pv *(1 + (ir_rate/100))** (period / 12)
    total_ir_earned = (fv-pv)
    monthly_ir_earned = total_ir_earned / period
    monthly_ir_rate = monthly_ir_earned / pv 
# if we have the period and not the start date then we make up the start date as today

    cf = pd.DataFrame({
        "period"        : range(1, period + 1),
        "date"          : generate_starting_dates(start_date, period),
        "start_balance" : round(pv,2),
        "pmt"           : 0,
        "monthly_ir_rate": round(monthly_ir_rate,4),
        "monthly_ir_earned": round(monthly_ir_earned,2)
        })
    cf["end_balance"] = 0.0 

    for i in cf.index:
        if i == 0:
            cf.at[i,"end_balance"] = cf.at[i,"start_balance"] + cf.at[i,"monthly_ir_earned"]
        else:
            cf.at[i,"start_balance"] = cf.at[i-1,"end_balance"]
            cf["end_balance"] = cf.monthly_ir_earned + cf["start_balance"]

    return cf 

def regular_saver(pmt,ir_rate,start_date =  None, end_date = None, period = None):

    # if not period:
    #     period = period_converter(start_date, end_date)

    # period = period + 2
    if period is None or period == 0:
        period = period_converter(start_date, end_date) + 2
        if period == 0:
            period = 1
    else:
        period = period + 1

    pmt = pmt
    monthly_ir_rate = (1+ (ir_rate/100))**(1/12) -1

    cf = pd.DataFrame({
    "period"            : range(1, period + 1),
    "date"              : generate_starting_dates(start_date, period),
    "start_balance"     : [0.0] * period, 
    "pmt"               : [pmt] * (period - 1) + [0],  # last month is interest-only
    "monthly_ir_rate"   : [round(monthly_ir_rate, 4)] * period,
    "monthly_ir_earned" : [0.0] * period,
    "end_balance"       : [0.0] * period
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

def run_cf_model(row):
    if row['Account Type'] in('Fixed', 'Variable'):
        return fixed_rate(
            pv          = row['Initial Investment Amount'],
            ir_rate     = row['Interest Rate'],
            start_date  = row['Start Date'],
            end_date    = row['End Date'],
            period      = row['Months']
        )
    else:
        return regular_saver(
            pmt         = row['Monthly Payment Amount'], 
            ir_rate     = row['Interest Rate'], 
            start_date  = row['Start Date'], 
            end_date    = row['End Date'],
            period      = row['Months']
            )


def get_monthly_rate(annual_rate, months):
    return round( (annual_rate / 100) / (12 * (months/12)),4)

def get_rate_shifts( annual_rate, rate_shift = None ):
    if rate_shift is None:
        rate_shift = (0.25)

    upper_rates = [annual_rate + i * rate_shift for i in range (1,4) ]
    lower_rates = [annual_rate - i * rate_shift for i in range (1,4) ]

    return sorted([*lower_rates,annual_rate,*upper_rates ])

# pass the fixed var df here and take the interest rate out. 
def get_summarytable_shifts(df): 
    summary_table_with_shifts = []

    for index, row in df.iterrows():          
        interest_rate = row['Interest Rate']
        shifted_rates = get_rate_shifts(annual_rate = interest_rate)
        
        for rate in shifted_rates:
            new_row = row.copy()
            new_row['Interest Rate'] = rate
            new_row['Provider Name'] = row['Provider Name']
            summary_table_with_shifts.append(new_row)

    return pd.DataFrame(summary_table_with_shifts).drop_duplicates()


    
        
    
    


