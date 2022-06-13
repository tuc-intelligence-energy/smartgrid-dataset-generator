import pandas as pd
import numpy as np
import collections
import json

def Freq_Weight_Calculation (dataframe):
    hour_freq = np.array(dataframe)
    elements_count = collections.Counter(hour_freq)
    df_freq = pd.DataFrame.from_dict(elements_count, orient='index').reset_index()
    df_freq = df_freq.rename(columns={'index':'Values', 0:'Frequency'})
    df_freq = df_freq.sort_values(['Frequency', 'Values'],ascending=False,ignore_index=True)
    df_freq['Weights'] = df_freq['Frequency']/sum(df_freq['Frequency'])
    return df_freq

def Charge_Freq_Tables_Creation (jsonData):
    ############### Daily Number of Charges ###############
    ###### Weekdays ########
    df_charge_wdays['DailyChargeFreq'] = (df_charge_wdays['BatteryChargeStartDay'] != df_charge_wdays['BatteryChargeStartDay'].shift(1)).cumsum()
    charge_freq = df_charge_wdays.groupby('DailyChargeFreq').apply(lambda x: x.shape[0])
    charge_freq = charge_freq[charge_freq<=4]
    df_tmp = Freq_Weight_Calculation(charge_freq)
    df_tmp.to_csv(jsonData['pathFreqTableDailyChargeWdays'], index=False)
    ###### Weekend #########
    df_charge_wend['DailyChargeFreq'] = (df_charge_wend['BatteryChargeStartDay'] != df_charge_wend['BatteryChargeStartDay'].shift(1)).cumsum()
    charge_freq = df_charge_wend.groupby('DailyChargeFreq').apply(lambda x: x.shape[0])
    charge_freq = charge_freq[charge_freq<=4]
    df_tmp = Freq_Weight_Calculation(charge_freq)
    df_tmp.to_csv(jsonData['pathFreqTableDailyChargeWend'], index=False)
    ############### Charge Start Hour ###############
    ###### Weekdays ########
    df_tmp = Freq_Weight_Calculation(df_charge_wdays['BatteryChargeStartHour'])
    df_tmp.Values[df_tmp['Values']==0] = 24
    df_tmp.to_csv(jsonData['pathFreqTableChargeStartHourWdays'], index=False)
    ###### Weekend #########
    df_tmp = Freq_Weight_Calculation(df_charge_wend['BatteryChargeStartHour'])
    df_tmp.Values[df_tmp['Values']==0] = 24
    df_tmp.to_csv(jsonData['pathFreqTableChargeStartHourWend'], index=False)
    ############### Starting SoC ###############
    ###### Weekdays ########
    df_tmp1 = df_charge_wdays[df_charge_wdays['Starting_SoC']<1]
    df_tmp = Freq_Weight_Calculation(df_tmp1['Starting_SoC'])
    df_tmp.to_csv(jsonData['pathFreqTableStartingSoCWdays'], index=False)
    ###### Weekend #########
    df_tmp1 = df_charge_wend[df_charge_wend['Starting_SoC']<1]
    df_tmp = Freq_Weight_Calculation(df_tmp1['Starting_SoC'])
    df_tmp.to_csv(jsonData['pathFreqTableStartingSoCWend'], index=False)
    ############### Ending SoC ###############
    ###### Weekdays ########
    df_tmp = Freq_Weight_Calculation(df_charge_wdays['Ending_SoC'])
    df_tmp.to_csv(jsonData['pathFreqTableEndingSoCWdays'], index=False)
    ###### Weekend #########
    df_tmp = Freq_Weight_Calculation(df_charge_wend['Ending_SoC'])
    df_tmp.to_csv(jsonData['pathFreqTableEndingSoCWend'], index=False)

def Trip_Freq_Tables_Creation ():
    ############# Daily Number of Trips #########
    ###### Weekdays ########
    df_trip_wdays['DailyTripsFreq'] = (df_trip_wdays['TripStartDay'] != df_trip_wdays['TripStartDay'].shift(1)).cumsum()
    trip_freq = df_trip_wdays.groupby('DailyTripsFreq').apply(lambda x: x.shape[0])
    trip_freq = trip_freq[trip_freq<=6]
    df_tmp = Freq_Weight_Calculation(trip_freq)
    df_tmp.to_csv(jsonData['pathFreqTableDailyTripsWdays'], index=False)
    ###### Weekend #########
    df_trip_wend['DailyTripsFreq'] = (df_trip_wend['TripStartDay'] != df_trip_wend['TripStartDay'].shift(1)).cumsum()
    trip_freq = df_trip_wend.groupby('DailyTripsFreq').apply(lambda x: x.shape[0])
    trip_freq = trip_freq[trip_freq<=6]
    df_tmp = Freq_Weight_Calculation(trip_freq)
    df_tmp.to_csv(jsonData['pathFreqTableDailyTripsWend'], index=False)
    ############### Trip Start Hour ###############
    ###### Weekdays ########
    df_tmp = Freq_Weight_Calculation(df_trip_wdays['TripStartHour'])
    df_tmp.Values[df_tmp['Values']==0] = 24
    df_tmp.to_csv(jsonData['pathFreqTableTripStartHourWdays'], index=False)
    ###### Weekend #########
    df_tmp = Freq_Weight_Calculation(df_trip_wend['TripStartHour'])
    df_tmp.Values[df_tmp['Values']==0] = 24
    df_tmp.to_csv(jsonData['pathFreqTableTripStartHourWend'], index=False)
    ############### Velocity ###############
    ###### Weekdays ########
    df_tmp0 = df_trip_wdays[df_trip_wdays['Velocity(km/h)'].isin(range(20,100))]
    df_tmp1 = df_tmp0['Velocity(km/h)'].apply(lambda x: 5 * round(x / 5))
    df_tmp = Freq_Weight_Calculation(df_tmp1)
    df_tmp.to_csv(jsonData['pathFreqTableVelocityWdays'], index=False)
    ###### Weekend #########
    df_tmp0 = df_trip_wend[df_trip_wend['Velocity(km/h)'].isin(range(20,100))]
    df_tmp1 = df_tmp0['Velocity(km/h)'].apply(lambda x: 5 * round(x / 5))
    df_tmp = Freq_Weight_Calculation(df_tmp1)
    df_tmp.to_csv(jsonData['pathFreqTableVelocityWend'], index=False)

with open("InputData.json") as jsonFile:
    jsonData = json.load(jsonFile)
    jsonFile.close()
# with open(sys.argv[1]) as jsonFile:
#     jsonData = json.load(jsonFile)
#     jsonFile.close()
df = pd.read_csv(jsonData['pathEVChargeDataPreProcessed'])
df_charge_wdays = df[(df['BatteryChargeStartDay']!=6) & (df['BatteryChargeStartDay']!=7)]
df_charge_wend = df[(df['BatteryChargeStartDay']==6) | (df['BatteryChargeStartDay']==7)]

df_trip = pd.read_csv(jsonData['pathEVTripDataPreProcessed'])
df_trip_wdays = df_trip[(df_trip['TripStartDay']!=6) & (df_trip['TripStartDay']!=7)]
df_trip_wend = df_trip[(df_trip['TripStartDay']==6) | (df_trip['TripStartDay']==7)]

Charge_Freq_Tables_Creation(jsonData)
Trip_Freq_Tables_Creation()
