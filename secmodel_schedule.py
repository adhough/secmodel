#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 24 06:54:06 2020

@author: adhough
"""


import pandas as pd
from datetime import date
import numpy as np
from collections import OrderedDict
from dateutil.relativedelta import relativedelta
import warnings


def securitise(principal, default_amt, interest_rate, years, sen_interest_rate, sub_interest_rate, addl_principal=0, annual_payments=12, start_date=date.today()):
    
    original_balance = np.float64(principal)
    sen_principal = np.float64(principal) * 0.9
    sub_principal = np.float64(principal) * 0.1
    reserve = np.float64(principal) * 0.01
    pmt = -round(np.pmt(np.float64(interest_rate)/np.float64(annual_payments), np.float64(years)*np.float64(annual_payments), np.float64(original_balance)), 2)
    
    # initialize the variables to keep track of the periods and running balances
    p = 1
    beg_balance = np.float64(principal)
    end_balance = np.float64(principal)
    beg_balance_actual = np.float64(principal)
    end_balance_actual = np.float64(principal)
    sen_beg_balance = sen_principal
    sen_end_balance = sen_principal
    sub_beg_balance = sub_principal
    sub_end_balance = sub_principal
    beg_balance_reserve = reserve
    end_balance_reserve = reserve

    while end_balance > 0:

        # Original - no default or prepayments
        interest = round(((np.float64(interest_rate)/np.float64(annual_payments)) * (np.float64(beg_balance))), 2)

      
        pmt = min(pmt, beg_balance + interest)
        principal = pmt - interest
     
        end_balance = beg_balance - principal
        
        #amortise percent used for asset principal repaymebt
        amortise_percent = 1 - (end_balance/beg_balance)
        
        #asset amortisation        
        interest_actual = max(round(((np.float64(interest_rate)/np.float64(annual_payments)) * (np.float64(beg_balance_actual)-np.float64(default_amt))), 2), 0)       
        principal_actual = max((np.float64(beg_balance_actual)-np.float64(default_amt))*np.float64(amortise_percent), 0)

        end_balance_actual = max(np.float64(beg_balance_actual) - np.float64(default_amt) - np.float64(principal_actual) - np.float64(addl_principal), 0)
        recovery = max(0.5 * np.float64(default_amt),0)
        asset_fee = max((beg_balance_actual * 0.02)/annual_payments, 0)
        cash_avail = max(np.float64(interest_actual) + np.float64(principal_actual) + np.float64(addl_principal) + np.float64(recovery) - np.float(asset_fee), 0)
        
        #senior bond 
        sen_interest = max(round(sen_beg_balance * (np.float64(sen_interest_rate)/annual_payments), 2), 0)
        sen_interest_paid = min(cash_avail, sen_interest)
        sen_interest_unpaid = max(sen_interest - sen_interest_paid, 0)
        sen_interest_reserve = min(beg_balance_reserve, sen_interest_unpaid)
        sen_principal = max(min((np.float64(principal_actual)+ np.float64(addl_principal) + np.float64(default_amt))*0.9, sen_beg_balance), 0)
        sen_principal_paid = min((cash_avail - sen_interest_paid), sen_principal)
        sen_principal_unpaid = max(sen_principal - sen_principal_paid, 0)
        sen_principal_reserve = min(beg_balance_reserve - sen_interest_unpaid, sen_principal_unpaid)
        
        sen_end_balance = max(sen_beg_balance - sen_principal_paid - sen_principal_reserve, 0)

        sen_cash_remain = max(cash_avail - sen_interest_paid - sen_principal_paid, 0)
        
        #reserve for senior bond
        reserve_withdrawal = max(sen_interest_reserve + sen_principal_reserve, 0)
        reserve_reimbursements = max(min(reserve-beg_balance_reserve, sen_cash_remain),0)
        end_balance_reserve = max(beg_balance_reserve - reserve_withdrawal + reserve_reimbursements, 0)
        reserve_cash_remain = max(sen_cash_remain - reserve_reimbursements, 0)
        
        #subordinated loan
        sub_interest = max(round(sub_beg_balance * (np.float64(sub_interest_rate)/annual_payments), 2), 0)
        sub_interest_paid = min(sen_cash_remain, sub_interest)
        sub_interest_unpaid = max(sub_interest - sub_interest_paid, 0)
        sub_principal = max(min((np.float64(principal_actual)+ np.float64(addl_principal) + np.float64(default_amt))*0.1, sub_beg_balance), 0)
        sub_principal_paid = min((sen_cash_remain - sub_interest_paid), sub_principal)
        sub_principal_unpaid = max(sub_principal - sub_principal_paid, 0)
        
        sub_end_balance = max(sub_beg_balance - sub_principal_paid, 0)

        sub_cash_remain = max(sen_cash_remain - sub_interest_paid - sub_principal_paid, 0)
        
        #returns
        asset_return = max(np.float64(interest_actual) + np.float64(principal_actual) + np.float64(addl_principal) + np.float64(recovery), 0)
        senior_return = max(sen_interest_paid + sen_interest_reserve + sen_principal_paid + sen_principal_reserve, 0)
        sub_return = max(sub_interest_paid + sub_principal_paid, 0)
        
        
        yield OrderedDict([('Month',start_date),
                           ('Period', p),
                           ('Begin Balance', beg_balance),
                           ('Interest Rate', interest_rate),
                           ('Payment', pmt),
                           ('Principal', principal),
                           ('Interest', interest),
                           ('End Balance', end_balance),
                           ('Amortise_Percent', amortise_percent),
                           ('Begin Balance Actual', beg_balance_actual),
                           ('Default_Amt', default_amt),
                           ('Interest Rate Actual', interest_rate),
                           ('Principal Actual', principal_actual),
                           ('Interest Actual', interest_actual),
                           ('Additional Principal', addl_principal),
                           ('End Balance Actual', end_balance_actual),
                           ('Recovery', recovery),
                           ('Asset Fee', asset_fee),
                           ('Cash Avail', cash_avail),
                           ('Senior Begin Balance', sen_beg_balance),
                           ('Senior Interest Rate', sen_interest_rate),
                           ('Senior Interest', sen_interest),
                           ('Senior Interest Paid', sen_interest_paid),
                           ('Senior Interest Unpaid', sen_interest_unpaid),
                           ('Senior Interest Reserve', sen_interest_reserve),
                           ('Senior Principal', sen_principal),
                           ('Senior Principal Paid', sen_principal_paid),
                           ('Senior Principal Unpaid', sen_principal_unpaid),
                           ('Senior Principal Reserve', sen_principal_reserve),
                           ('Senior End Balance', sen_end_balance),
                           ('Senior Remaining Cash', sen_cash_remain),
                           ('Reserve Begin Balance', beg_balance_reserve),
                           ('Reserve Withdrawls', reserve_withdrawal),
                           ('Reserve Reimbursements', reserve_reimbursements), 
                           ('Reserve End Balance', end_balance_reserve),
                           ('Reserve Remaining Cash', reserve_cash_remain),
                           ('Sub Begin Balance', sub_beg_balance),
                           ('Sub Interest Rate', sub_interest_rate),
                           ('Sub Interest', sub_interest),
                           ('Sub Interest Paid', sub_interest_paid),
                           ('Sub Interest Unpaid', sub_interest_unpaid),
                           ('Sub Principal', sub_principal),
                           ('Sub Principal Paid', sub_principal_paid),
                           ('Sub Principal Unpaid', sub_principal_unpaid),
                           ('Sub End Balance', sub_end_balance),
                           ('Sub Remaining Cash', sub_cash_remain),
                           ('Asset Return', asset_return),
                           ('Senior Return', senior_return),
                           ('Subordinated Return', sub_return)])

        # Increment the counter, balance and date
        p += 1
        start_date += relativedelta(months=1)
        beg_balance = end_balance
        beg_balance_actual = end_balance_actual
        sen_beg_balance = sen_end_balance
        sub_beg_balance = sub_end_balance
        beg_balance_reserve = end_balance_reserve

        
        

# schedule = pd.DataFrame(securitise(100000000, 100, .06, 30, 0.04, 0.07, addl_principal=200, start_date=date(2020, 7,1)))
schedule = pd.DataFrame(securitise(principal=100000000, default_amt=100, interest_rate=0.06, years=30, sen_interest_rate=0.04, sub_interest_rate=0.06, addl_principal=200, start_date=date(2020, 7,1)))

warnings.filterwarnings('ignore', category=DeprecationWarning)
asset_endbalance = round(schedule.iloc[359, 15], 2)
senior_endbalance = round(schedule.iloc[359, 29], 2)
subordinated_endbalance = round(schedule.iloc[359, 44], 2)
reserve_balance_due = round((schedule.iloc[0, 31]) - (schedule.iloc[359, 34]), 2)

#asset irr
asset_return_list = schedule.iloc[:, 46].to_list()
asset_return_list.insert(0, -schedule.iloc[0,9])
irr_asset = round(((1+np.irr(asset_return_list))**12)-1, 4)

#senior irr
senior_return_list = schedule.iloc[:, 47].to_list()
senior_return_list.insert(0, -schedule.iloc[0,19])
irr_senior = round(((1+np.irr(senior_return_list))**12)-1, 4)

#subordinated irr
sub_return_list = schedule.iloc[:, 48].to_list()
sub_return_list.insert(0, -schedule.iloc[0,36])
irr_subordinated = round(((1+np.irr(sub_return_list))**12)-1, 4)
# irr_senior = round(np.irr[-(schedule.iloc[0, 10], schedule.iloc[:, 46])])
# irr_subordinated = round(np.irr[-(schedule.iloc[0, 10], schedule.iloc[:, 46])])


print("Asset End Balance = " + str(asset_endbalance))
print("Senior End Balance = " + str(senior_endbalance))
print("Subordinated End Balance = " + str(subordinated_endbalance))
print("Reserve Balance Due = " + str(reserve_balance_due))
print("Internal Rate of Return of Asset Portfolio = " + str(irr_asset))
print("Internal Rate of Return of Senior Bond = " + str(irr_senior))
print("Internal Rate of Return of Subordinated Loan = " + str(irr_subordinated))
