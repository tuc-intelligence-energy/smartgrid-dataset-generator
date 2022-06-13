import pandas as pd
import numpy as np
import collections
import sys
import time
import json
import os

def Freq_Weight_Calculation (dataframe):
    hour_freq = np.array(dataframe)
    elements_count = collections.Counter(hour_freq)
    df_freq = pd.DataFrame.from_dict(elements_count, orient='index').reset_index()
    df_freq = df_freq.rename(columns={'index':'Values', 0:'Frequency'})
    df_freq = df_freq.sort_values(['Frequency', 'Values'],ascending=False,ignore_index=True)
    df_freq['Weights'] = df_freq['Frequency']/sum(df_freq['Frequency'])
    return df_freq

def Charge_Freq_Tables_Creation (df_charge, df_gen, jsonData, path):
    #######################################################
    ####################   ORIGINAL    ####################
    #######################################################
    ############### Daily Number of Charges ###############
    df_charge['DailyChargeFreq'] = (df_charge['BatteryChargeStartDay'] != df_charge['BatteryChargeStartDay'].shift(1)).cumsum()
    charge_freq = df_charge.groupby('DailyChargeFreq').apply(lambda x: x.shape[0])
    charge_freq = charge_freq[charge_freq<=4]
    df_tmp = Freq_Weight_Calculation(charge_freq)
    fileName = path+'/'+jsonData['pathFreqTableCompDailyChargeOrig']
    df_tmp.to_csv(fileName, index=False)
    ############### Charge Start Hour ###############
    df_tmp = Freq_Weight_Calculation(df_charge['BatteryChargeStartHour'])
    df_tmp.Values[df_tmp['Values']==0] = 24
    fileName = path+'/'+jsonData['pathFreqTableCompChargeStartHourOrig']
    df_tmp.to_csv(fileName, index=False)
    ############### Starting SoC ###############
    df_tmp1 = df_charge[df_charge['Starting_SoC'] < 1]
    df_tmp = Freq_Weight_Calculation(df_tmp1['Starting_SoC'])
    fileName = path+'/'+jsonData['pathFreqTableCompStartingSoCOrig']
    df_tmp.to_csv(fileName, index=False)
    ############### Ending SoC ###############
    df_tmp = Freq_Weight_Calculation(df_charge['Ending_SoC'])
    fileName = path+'/'+jsonData['pathFreqTableCompEndingSoCOrig']
    df_tmp.to_csv(fileName, index=False)
    #######################################################
    ###################   GENERATED    ####################
    #######################################################
    df_tmp0 = df_gen[df_gen['FirstLastCharge'] == 1]
    ############### Daily Number of Charges ###############
    df_tmp0['DailyChargeFreq'] = (df_tmp0['Date'] != df_tmp0['Date'].shift(1)).cumsum()
    charge_freq = df_tmp0.groupby('DailyChargeFreq').apply(lambda x: x.shape[0])
    df_tmp = Freq_Weight_Calculation(charge_freq)
    ############### Charge Start Hour ###############
    df_tmp1 = Freq_Weight_Calculation(df_tmp0['Time_of_Day'])
    ############### Starting SoC ###############
    df_tmp2 = Freq_Weight_Calculation(df_tmp0['Starting_SoC'])
    ############### Ending SoC ###############
    df_tmp0 = df_gen[df_gen['FirstLastCharge'] == 2]
    df_tmp3 = Freq_Weight_Calculation(df_tmp0['Ending_SoC'])
    ##########################################
    mode = jsonData['checksMode']
    if mode=="Strict":
        fileName = path + '/' + jsonData['pathFreqTableCompDailyChargeStrict']
        df_tmp.to_csv(fileName, index=False)
        fileName = path + '/' + jsonData['pathFreqTableCompChargeStartHourStrict']
        df_tmp1.to_csv(fileName, index=False)
        fileName = path + '/' + jsonData['pathFreqTableCompStartingSoCStrict']
        df_tmp2.to_csv(fileName, index=False)
        fileName = path + '/' + jsonData['pathFreqTableCompEndingSoCStrict']
        df_tmp3.to_csv(fileName, index=False)
    elif mode=="Looser":
        fileName = path + '/' + jsonData['pathFreqTableCompDailyChargeLooser']
        df_tmp.to_csv(fileName, index=False)
        fileName = path + '/' + jsonData['pathFreqTableCompChargeStartHourLooser']
        df_tmp1.to_csv(fileName, index=False)
        fileName = path + '/' + jsonData['pathFreqTableCompStartingSoCLooser']
        df_tmp2.to_csv(fileName, index=False)
        fileName = path + '/' + jsonData['pathFreqTableCompEndingSoCLooser']
        df_tmp3.to_csv(fileName, index=False)
    elif mode=="Min":
        fileName = path + '/' + jsonData['pathFreqTableCompDailyChargeMin']
        df_tmp.to_csv(fileName, index=False)
        fileName = path + '/' + jsonData['pathFreqTableCompChargeStartHourMin']
        df_tmp1.to_csv(fileName, index=False)
        fileName = path + '/' + jsonData['pathFreqTableCompStartingSoCMin']
        df_tmp2.to_csv(fileName, index=False)
        fileName = path + '/' + jsonData['pathFreqTableCompEndingSoCMin']
        df_tmp3.to_csv(fileName, index=False)

def Trip_Freq_Tables_Creation (df_trip, df_gen, jsonData, path):
    #######################################################
    ####################   ORIGINAL    ####################
    #######################################################
    ############# Daily Number of Trips #########
    df_trip['DailyTripsFreq'] = (df_trip['TripStartDay'] != df_trip['TripStartDay'].shift(1)).cumsum()
    trip_freq = df_trip.groupby('DailyTripsFreq').apply(lambda x: x.shape[0])
    trip_freq = trip_freq[trip_freq<=6]
    df_tmp = Freq_Weight_Calculation(trip_freq)
    fileName = path+'/'+jsonData['pathFreqTableCompDailyTripsOrig']
    df_tmp.to_csv(fileName, index=False)
    ############### Trip Start Hour ###############
    df_tmp = Freq_Weight_Calculation(df_trip['TripStartHour'])
    df_tmp.Values[df_tmp['Values']==0] = 24
    fileName = path+'/'+jsonData['pathFreqTableCompTripStartHourOrig']
    df_tmp.to_csv(fileName, index=False)
    #######################################################
    ###################   GENERATED    ####################
    #######################################################
    df_tmp0 = df_gen[df_gen['FirstTrip'] == 1]
    ############ Daily Number of Trips ##########
    df_tmp0['DailyChargeFreq'] = (df_tmp0['Date'] != df_tmp0['Date'].shift(1)).cumsum()
    charge_freq = df_tmp0.groupby('DailyChargeFreq').apply(lambda x: x.shape[0])
    df_tmp = Freq_Weight_Calculation(charge_freq)
    ############### Trip Start Hour ###############
    df_tmp1 = Freq_Weight_Calculation(df_tmp0['Time_of_Day'])
    ###############################################
    mode = jsonData['checksMode']
    if mode=="Strict":
        fileName = path + '/' + jsonData['pathFreqTableCompDailyTripsStrict']
        df_tmp.to_csv(fileName, index=False)
        fileName = path + '/' + jsonData['pathFreqTableCompTripStartHourStrict']
        df_tmp1.to_csv(fileName, index=False)
    elif mode=="Looser":
        fileName = path + '/' + jsonData['pathFreqTableCompDailyTripsLooser']
        df_tmp.to_csv(fileName, index=False)
        fileName = path + '/' + jsonData['pathFreqTableCompTripStartHourLooser']
        df_tmp1.to_csv(fileName, index=False)
    elif mode=="Min":
        fileName = path + '/' + jsonData['pathFreqTableCompDailyTripsMin']
        df_tmp.to_csv(fileName, index=False)
        fileName = path + '/' + jsonData['pathFreqTableCompTripStartHourMin']
        df_tmp1.to_csv(fileName, index=False)

def FrequencyTables_GeneratedData (df_gen, jsonData, pathDriverBeh):
    # Create the appropriate directory if doesn't exist
    strName0 = jsonData['pathFreqTableComparison']
    path = pathDriverBeh+'/'+strName0
    isExist = os.path.exists(path)
    if not isExist:
        os.makedirs(path)

    df_charge = pd.read_csv(jsonData['pathEVChargeDataPreProcessed'])
    df_trip = pd.read_csv(jsonData['pathEVTripDataPreProcessed'])

    df_gen['Date'] = pd.DatetimeIndex(df_gen['Date']).day
    df_gen.insert(21, 'FirstLastCharge', 0)
    df_gen.insert(22, 'FirstTrip', 0)

    for index, row in df_gen.iterrows():
        if index == 0:
            if (df_gen.loc[index, 'Status'] == 1):
                df_gen.loc[index, 'FirstLastCharge'] = 1
            elif (df_gen.loc[index, 'Status'] == 2):
                df_gen.loc[index, 'FirstTrip'] = 1
        elif index != df_gen.index[-1]:
            if ((df_gen.loc[index, 'Status'] == 1) & (pd.isnull(df_gen.loc[index - 1, 'Charger_Type']))):
                df_gen.loc[index, 'FirstLastCharge'] = 1
            elif ((df_gen.loc[index, 'Status'] == 1) & (pd.isnull(df_gen.loc[index + 1, 'Charger_Type']))):
                df_gen.loc[index, 'FirstLastCharge'] = 2
            if ((df_gen.loc[index, 'Status'] == 2) & (pd.isnull(df_gen.loc[index - 1, 'Trip_Time(mins)']))):
                df_gen.loc[index, 'FirstTrip'] = 1

    Charge_Freq_Tables_Creation(df_charge, df_gen, jsonData, path)
    Trip_Freq_Tables_Creation(df_trip, df_gen, jsonData, path)


# if __name__ == '__main__':
#     start_time = time.time()
#     with open("InputData.json") as jsonFile:
#         jsonData = json.load(jsonFile)
#         jsonFile.close()
#     # with open(sys.argv[1]) as jsonFile:
#     #     jsonData = json.load(jsonFile)
#     #     jsonFile.close()
#     mode = jsonData['checksMode']
#     if mode == "Strict":
#         strName1 = "/GeneratedData_DriverBehavior_StrictChecks.csv"
#     elif mode == "Looser":
#         strName1 = "/GeneratedData_DriverBehavior_LooserChecks.csv"
#     elif mode == "Min":
#         strName1 = "/GeneratedData_DriverBehavior_MinChecks.csv"
#     else:
#         print("\nERROR: Wrong configuration for variable 'checksMode'\nCheck .json file")
#         sys.exit()
#     fileName = "%s%s" % (jsonData['pathGeneratedDriversData'],strName1)
#     df_gen = pd.read_csv(fileName)
#
#     FrequencyTables_GeneratedData (df_gen,jsonData)
#
#     total_elapsed_time = round(time.time() - start_time, 2)
#     print("Total execution time:  {} seconds".format(total_elapsed_time))