import datetime
import json

from django.http import JsonResponse
from django.shortcuts import render
import pandas as pd
# Create your views here.

price_types = {'A':10, 'B':20, 'C':30}
receipt_file_path = '/home/fuel_receipt.csv'

def add_fuel_receipt_records(request):
    input_records = json.loads(request.body)
    if validation_check(input_records):
        temp_df = pd.DataFrame(input_records)
        temp_df.to_csv(receipt_file_path, mode='a', header=False)
        return JsonResponse({'message':'success', 'status':200})
    else:
        return JsonResponse({'message':'Invalid Records', 'status':500})
    
def validation_check(input_records):
    is_valid = True
    for rec in input_records:
        if all([rec['driverid'], rec['fueltype'], rec['price'], rec['volume'], rec['date']]):
            if (rec['fueltype'] in price_types) and (rec['price'] == price_types[rec['fueltype']]):
                try:
                    _ = datetime.datetime.strptime(rec['date'], '%Y-%m-%d')
                    continue
                except:
                    is_valid = False
                    break
            else:
                is_valid = False
                break
        else:
            is_valid = False
            break
    return is_valid

def get_fuel_types(request):
    return JsonResponse(price_types)

def get_driver_fuel_stats(request, driverid):
    input_df = pd.read_csv(receipt_file_path)
    input_df = input_df.loc[input_df['driverid'] == driverid, :]
    input_df.reset_index(inplace=True, drop=True)   
    input_df['month'] = (input_df['date'].astype('str')
                        .apply(lambda x:datetime.datetime.strptime(x, '%Y-%m-%d').strftime('%b-%Y'))
                        )
    input_df['moneySpent'] = input_df['price'].astype('float')*input_df['volume'].astype('float')
    fuel_type_stats = (input_df.groupby(['month', 'fueltype', 'price'])
                        .agg({'volume':'sum', 'moneySpent':'sum'})
                        .reset_index()
                        .rename(columns={'moneySpent':'totalPrice', 'volume':'totalVolume'}))
    fuel_type_stats['rec'] = fuel_type_stats[['totalPrice', 'totalVolume', 'fueltype', 'price']].to_dict('records')
    fuel_type_stats = fuel_type_stats.groupby('month')['rec'].apply('list').to_dict()
    month_money_stats = (input_df.groupby('month')
                        .agg({'moneySpent':'sum'})
                        )
    fuel_type_stats = fuel_type_stats.to_dict('index')
    month_money_stats = month_money_stats.to_dict()
    input_df['fid'] = input_df.index
    input_df['rec'] = input_df[['fid', 'driverid', 'fueltype', 'price', 'volume', 'date', 'moneySpent']].to_dict('records')
    input_json_recs = input_df.groupby('month')['rec'].apply('list').to_dict()
    
    output_json = {month: {'totalAmountSpent':month_money_stats['month'],
                           'fuelConsumptionList':fuel_list,
                           'fuel_type_statics':fuel_type_stats['month']}
                          for month, fuel_list in input_json_recs.items()}              
    return JsonResponse(output_json)