import streamlit as st
import nii as nii
import graphs as graphs
from datetime import date 
import datetime as dt 
from dateutil.relativedelta import relativedelta 
import pandas as pd
import altair as alt

def run_cf_model(row):
    if row['Account Type'] in('Fixed', 'Variable'):
        return nii.fixed_rate(
            pv          = row['Initial Investment Amount'],
            ir_rate     = row['Interest Rate'],
            start_date  = row['Start Date'],
            end_date    = row['End Date'],
            period      = row['Months']
        )
    else:
        return nii.regular_saver(
            pmt         = row['Monthly Payment Amount'], 
            ir_rate     = row['Interest Rate'], 
            start_date  = row['Start Date'], 
            end_date    = row['End Date'],
            period      = row['Months']
            )


def main():
    

    st.set_page_config(page_title="Savings Calculator", layout="wide")

    st.title("💰 Savings Calculator")

    # Input Section
    with st.container():
        st.markdown("### 📝 Account Details")
        col1, col2 = st.columns(2)
        with col1:
            provider_name = st.text_input("🏦 Provider Name")
            account_type = st.selectbox("📂 Account Type", ["Fixed", "Variable", "Regular Saver"])
        with col2:
            ir_rate = st.number_input("📈 Interest Rate (%)", value=5.0, step=0.1, format="%.2f")
            time_type = st.selectbox("⏳ Time Period Type", ["Start and End date", "Enter Months"])

    # Investment Section
    st.markdown("### 💸 Investment Details")

    if account_type in ["Fixed", "Variable"]:
        pv = st.number_input("💰 Initial Investment Amount", value=5000, step=100)
    else:
        pmt = st.number_input("💵 Monthly Payment Amount", value=250, step=10)

    # Time Input Section
    if time_type == "Start and End date":
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("📅 Start Date", value=date.today())
        with col2:
            end_date = st.date_input("📅 End Date", value=date.today())
    else:
        months = st.number_input("📆 Number of Months", value=12, step=1)

    # Submission
#    initiate tables to use. 
    if "fixedvar_df" not in st.session_state:
        st.session_state.fixedvar_df = pd.DataFrame(columns=[
        "Provider Name", "Account Type", "Interest Rate",
        "Start Date", "End Date", "Months",
        "Monthly Payment Amount", "Initial Investment Amount", "Ending Value"
    ])
    
    if "cf" not in st.session_state:
        st.session_state.cf = pd.DataFrame(columns=["provider_name",
        "period", "date", "start_balance", "pmt", "monthly_ir_rate", "monthly_ir_earned", "end_balance"
    ])
    
    if st.button("➕ Add"):
        st.success("✅ Details submitted!")
        
        fixedvar_dic = {
            "Provider Name": provider_name,
            "Account Type": account_type,
            "Interest Rate": ir_rate,
            "Start Date": start_date if time_type == "Start and End date" else None,
            "End Date": end_date if time_type == "Start and End date" else None,
            "Months": months if time_type == "Enter Months" else None,
            "Monthly Payment Amount": pmt if account_type == "Regular Saver" else None,
            "Initial Investment Amount": pv if account_type in ["Fixed", "Variable"] else None,
        }
        # Add the new row to the DataFrame
        st.session_state.fixedvar_df.loc[len(st.session_state.fixedvar_df)] = fixedvar_dic
        # clean up the dataframe
        st.session_state.fixedvar_df['Provider Name'] = st.session_state.fixedvar_df.apply(
            lambda row: f"Savings_{row.name}" if pd.isna(row['Provider Name']) or row['Provider Name'] == "" else row['Provider Name'],
            axis=1
            )
        st.session_state.fixedvar_df["Months"] = st.session_state.fixedvar_df.apply(
            lambda row: nii.period_converter(start_date=row["Start Date"], end_date=row["End Date"]) 
            if pd.isna(row['Months']) else row['Months'],
            axis=1
            )
        st.session_state.fixedvar_df["Start Date"] = st.session_state.fixedvar_df.apply(
            lambda row: dt.datetime.today().strftime("%Y-%m") if pd.isna(row['Start Date']) else row['Start Date'],
                axis=1
            )
        # adds 12 months is its regular saver else adds 11 months if the account type is fixed, varibale keeps it consistent with the cashflow 
        st.session_state.fixedvar_df["End Date"] = st.session_state.fixedvar_df.apply(
            lambda row: (pd.to_datetime(row["Start Date"]) + relativedelta(
                months = 12 if row["Account Type"] == "Regular Saver" else row["Months"]-1 )).strftime("%Y-%m") if pd.isna(row['End Date']) else row['End Date'],
                axis=1
            )
        
        

        results = []
        for idx, row in st.session_state.fixedvar_df.iterrows():
            cf_reuslt = run_cf_model(row)
            cf_reuslt["provider_name"] = row["Provider Name"]
            results.append(cf_reuslt)

        if results:
            st.session_state.cf = pd.concat([st.session_state.cf, results[-1]], ignore_index=True)  
      

        ending_values = st.session_state.cf.groupby("provider_name").last()["end_balance"]
        st.session_state.fixedvar_df["Ending Value"] = st.session_state.fixedvar_df["Provider Name"].map(ending_values)
    
# Display summary table and clear all button 
    if not st.session_state.fixedvar_df.empty:
        with st.container():
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### 📊 Summary Table")
                # """clears all the tables, cf and fixedvar"""
            with col2:  
                st.button("Clear All",
                         key="clear_all", 
                         on_click=lambda: (
                             st.session_state.fixedvar_df.drop(st.session_state.fixedvar_df.index, inplace=True),
                             st.session_state.cf.drop(st.session_state.cf.index, inplace=True)
                         )
                         )

# DISPLAY TABLES
        st.dataframe(st.session_state.fixedvar_df, use_container_width=True,  width=2000)
        st.data_editor(st.session_state.cf, use_container_width=True, hide_index=True, num_rows="dynamic", key="cf_table")
# KEY HEADLINE NUMBERS 
        col1,col2,col3, col4 = st.columns(4)
        with col1:            
            st.metric(label="Total Amount Invested", 
                      value=int(st.session_state.cf["pmt"].sum() + st.session_state.fixedvar_df["Initial Investment Amount"].sum()),
                      border =True)
        with col2:    
            st.metric(label="Total Ending Value", 
                      value= int(st.session_state.fixedvar_df["Ending Value"].sum()),
                      border =True)
        with col3:
            st.metric(label="Total Interest Earned at Maturity ", 
                      value= int(st.session_state.cf["monthly_ir_earned"].sum()),
                      border =True)
        with col4:

            st.metric(label="Total Effective Interest Rate ", 
                      value = f"{round((st.session_state.cf['monthly_ir_earned'].sum() / st.session_state.fixedvar_df['Ending Value'].sum()) * 100, 2)}%",
                      border = True)


# DISPLAY GRAPHS  
    st.markdown("### 📈 Graphs")

    st.altair_chart(graphs.bar(st.session_state.fixedvar_df.copy()), use_container_width=True)



            
if __name__ == "__main__":
    main()
    
    
