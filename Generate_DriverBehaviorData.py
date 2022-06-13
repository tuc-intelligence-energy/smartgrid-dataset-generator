import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import math
import glob
import os
import json
import sys

def Sampling_Daily_Charges(numdays,isWeekend,jdata):
    ############### Number of Daily Charges ###############
    if isWeekend == 0:
        df1 = pd.read_csv(jdata['pathFreqTableDailyChargeWdays'])
    else:
        df1 = pd.read_csv(jdata['pathFreqTableDailyChargeWend'])
    df1_samples = df1.sample(n=numdays, replace=True, weights='Weights').reset_index(drop=True)
    df1_samples = df1_samples['Values']
    # print(df1_samples)
    return df1_samples

def Sampling_EV_Specs(samples,jdata):
    ################## EV_Specs ##################
    EVCategory = jdata['EVCategory']
    ChargerCategory = jdata['ChargerCategory']
    df_tmp1 = pd.read_csv(jdata['pathEVSpecs'])
    catA_per = EVCategory[0]/100
    catB_per = EVCategory[1]/100
    catC_per = EVCategory[2]/100
    if ((0<=catA_per<=1 and 0<=catB_per<=1 and 0<=catC_per<=1)
            and catA_per+catB_per+catC_per==1):
        catA = round(catA_per*samples)
        catB = round(catB_per*samples)
        catC = samples-(catA+catB)
        # if (catC==0 and catC_per!=0):
        #     if(catA>catB):
        #         catA = catA-1
        #     else:
        #         catB = catB-1
        #     catC = 1
    else:
        print("\nERROR: Wrong configuration for variable 'EVCategory'\nCheck .json file")
        sys.exit()
    if (catC_per!=0 and (ChargerCategory[1]==0 and ChargerCategory[2]==0)):
        print("\nERROR: Wrong configuration for variables 'EVCategory' and 'ChargerCategory'\nCheck .json file")
        sys.exit()
    df_tmp1_catA = df_tmp1[df_tmp1['Category']==1].sample(n=catA, replace=True, ignore_index=True)
    df_tmp1_catB = df_tmp1[df_tmp1['Category']==2].sample(n=catB, replace=True, ignore_index=True)
    df_tmp1_catC = df_tmp1[df_tmp1['Category']==3].sample(n=catC, replace=True, ignore_index=True)

    df_concat = pd.concat([df_tmp1_catA,df_tmp1_catB,df_tmp1_catC], axis=0).reset_index(drop=True)
    df_concat = df_concat.rename(columns={'CarModel':'EV_Model', 'BatteryCapacity(kWh)':'Battery_Capacity(kWh)',
                              'MeanEnergyConsumption(kWh/100km)':'Mean_Energy_Consumption(kWh/100km)',
                              'Maximum_DC_Charging_Power(kW)':'Max_DC_Power(kW)'})
    return df_concat

def Sampling_Charger_Specs(samples,jdata,EVcat):
    ################## EV_Specs ##################
    ChargerCategory = jdata['ChargerCategory']
    df_tmp1 = pd.read_csv(jdata['pathChargerSpecs'])
    slow = ChargerCategory[0]/100
    fast = ChargerCategory[1]/100
    rapid = ChargerCategory[2]/100

    if not(0<=slow<=1 and 0<=fast<=1 and 0<=rapid<=1):
        print("\nERROR: Wrong configuration for variable 'ChargerCategory'\nCheck .json file")
        sys.exit()

    df_tmp1['Weights'] = np.nan
    for index, row in df_tmp1.iterrows():
        if (row['ChargerRating']=='Slow'):
            df_tmp1.loc[index, 'Weights'] = slow
            if (EVcat == 3):
                df_tmp1.loc[index, 'Weights'] = 0
        elif (row['ChargerRating']=='Fast'):
            df_tmp1.loc[index, 'Weights'] = fast
        else:
            df_tmp1.loc[index, 'Weights'] = rapid

    df_tmp1_samples = df_tmp1.sample(n=samples, replace=True, ignore_index=True, weights='Weights')

    return df_tmp1_samples

def Calculate_Charging_Hours(chargePower,maxDC,endSoc,startSoc,batCapacity):
    charge_rate = chargePower
    if chargePower>=50:
        charge_rate = min(chargePower, maxDC)
    battery_load = endSoc-startSoc
    charging_time = round((batCapacity*battery_load)/charge_rate,2)
    return charging_time

def Sampling_Charge_Data(check,samples,minHour,dataframe4,df_EVSpecs,checkSoC,preEndingSoC,isWeekend,jdata):
    df_final = pd.DataFrame(columns=['Start_Hour','Starting_SoC','Ending_SoC','SoC_Diff','EV_Model','Battery_Capacity(kWh)',
                                     'Category','Mean_Energy_Consumption(kWh/100km)','Max_DC_Power(kW)',
                                     'Charger_Type','Charger_Power(kW)','Charging_Hours'])
    ############### Charge Start Hour ###############
    if isWeekend==0:
        df1 = pd.read_csv(jdata['pathFreqTableChargeStartHourWdays'])
    else:
        df1 = pd.read_csv(jdata['pathFreqTableChargeStartHourWend'])

    try:
        df1_samples = df1[df1['Values'] > minHour].sample(n=samples, replace=True, weights='Weights').reset_index(drop=True)
    # If minHour=23 or 24, then sample any value bigger than 0 or 1 respectively
    except ValueError:
        df1_samples = df1[df1['Values'] > minHour-24].sample(n=samples, replace=True, weights='Weights').reset_index(drop=True)
    df_final['Start_Hour'] = df1_samples['Values']
    ########### Starting SoC / Ending SoC ###########
    if isWeekend == 0:
        df2 = pd.read_csv(jdata['pathFreqTableStartingSoCWdays'])
        df3 = pd.read_csv(jdata['pathFreqTableEndingSoCWdays'])
    else:
        df2 = pd.read_csv(jdata['pathFreqTableStartingSoCWend'])
        df3 = pd.read_csv(jdata['pathFreqTableEndingSoCWend'])

    for i, row in enumerate(df_final.itertuples(index=False)):
        # df2_samples = df2.sample(n=1, replace=True, weights='Weights').reset_index(drop=True)
        if (checkSoC == 1):
            df2_samples = df2[df2['Values'] < preEndingSoC].sample(n=1, replace=True, weights='Weights').reset_index(
                drop=True)
        else:
            df2_samples = df2.sample(n=1, replace=True, weights='Weights').reset_index(drop=True)
        startSoc = df2_samples['Values'].values[0]
        df_final.loc[i, 'Starting_SoC'] = startSoc
        df3_samples = df3[df3['Values']>startSoc].sample(n=1, replace=True, weights='Weights').reset_index(drop=True)
        df_final.loc[i, 'Ending_SoC'] = df3_samples['Values'].values[0]
        df_final.loc[i, 'SoC_Diff'] = round(df_final.loc[i, 'Ending_SoC'] - df_final.loc[i, 'Starting_SoC'],2)

    ################## EV_Specs ##################
    if check==0:
        df4 = df_EVSpecs.sample(n=1, replace=False)
        df_EVSpecs = df_EVSpecs.drop(df4.index).reset_index(drop=True)
    else:
        df4 = dataframe4
    df_final['EV_Model'] = df4['EV_Model'].values[0]
    df_final['Battery_Capacity(kWh)'] = df4['Battery_Capacity(kWh)'].values[0]
    df_final['Category'] = df4['Category'].values[0]
    df_final['Mean_Energy_Consumption(kWh/100km)'] = df4['Mean_Energy_Consumption(kWh/100km)'].values[0]
    df_final['Max_DC_Power(kW)'] = df4['Max_DC_Power(kW)'].values[0]

    ############### Charging_Specs ###############
    EVcategory = df4['Category'].values[0]
    df5_samples = Sampling_Charger_Specs(samples,jdata,EVcategory)

    df_final['Charger_Type'] = df5_samples['ChargerType']
    df_final['Charger_Power(kW)'] = df5_samples['Rated_Power(kW)']
    df_final['Charging_Hours'] = df_final.apply(lambda row : Calculate_Charging_Hours(row['Charger_Power(kW)'],
                                                                                     row['Max_DC_Power(kW)'],
                                                                                     row['Ending_SoC'],
                                                                                     row['Starting_SoC'],
                                                                                      row['Battery_Capacity(kWh)']),axis=1)
    return df_final,df_EVSpecs

def Case_Charges_1(df_new,df_tmp,i):
    timeCharging = df_tmp.loc[df_tmp.index[0],'Charging_Hours']
    floorHours = math.floor(timeCharging)
    hour = 60
    minutes = round((timeCharging*hour) % hour)
    idxStart = i - 1 + df_tmp.loc[df_tmp.index[0],'Start_Hour']
    if timeCharging<1:
        df_new.at[idxStart, 'Status'] = 1
        df_new.at[idxStart, 'Charging_Time(mins)'] = minutes
        df_new.loc[idxStart, 'Consumption_Charging(kW)'] = round((df_tmp.loc[df_tmp.index[0],'Charger_Power(kW)']*minutes)/hour,2)
        df_new.loc[idxStart, 'Charger_Type'] = df_tmp.loc[df_tmp.index[0],'Charger_Type']
        df_new.loc[idxStart, 'Charger_Power(kW)'] = df_tmp.loc[df_tmp.index[0],'Charger_Power(kW)']
        df_new.loc[idxStart, 'Starting_SoC'] = df_tmp.loc[df_tmp.index[0],'Starting_SoC']
        df_new.loc[idxStart, 'Ending_SoC'] = df_tmp.loc[df_tmp.index[0],'Ending_SoC']
        pDate = df_new['Date'].dt.date[idxStart]
        pHour = df_new.loc[idxStart, 'Time_of_Day'] +1
        pEndSoC = df_new.loc[idxStart, 'Ending_SoC']
    else:
        idxEnd = idxStart + floorHours
        df_new.at[idxStart:idxEnd, 'Status'] = 1
        df_new.at[idxStart:idxEnd, 'Charging_Time(mins)'] = hour
        df_new.at[idxEnd, 'Charging_Time(mins)'] = minutes
        df_new.at[idxStart:idxEnd, 'Consumption_Charging(kW)'] = df_tmp.loc[df_tmp.index[0],'Charger_Power(kW)']
        df_new.loc[idxEnd, 'Consumption_Charging(kW)'] = round((df_tmp.loc[df_tmp.index[0],'Charger_Power(kW)']*minutes)/hour,2)
        df_new.loc[idxStart:idxEnd, 'Charger_Type'] = df_tmp.loc[df_tmp.index[0],'Charger_Type']
        df_new.loc[idxStart:idxEnd, 'Charger_Power(kW)'] = df_tmp.loc[df_tmp.index[0],'Charger_Power(kW)']
        # df_gen.loc[idxStart, 'Starting_SoC'] = df_ChargeSamples['Starting_SoC'].values[c1]
        # df_gen.loc[idxEnd, 'Ending_SoC'] = df_ChargeSamples['Ending_SoC'].values[c1]

        startSOC = df_tmp.loc[df_tmp.index[0],'Starting_SoC']
        stepSoc = df_tmp.loc[df_tmp.index[0],'SoC_Diff'] / timeCharging
        for j in range(idxStart, idxEnd+1):
            df_new.loc[j, 'Starting_SoC'] = round(startSOC, 2)
            ending = startSOC + stepSoc
            df_new.loc[j, 'Ending_SoC'] = round(ending, 2)
            startSOC = ending
        df_new.loc[idxEnd, 'Ending_SoC'] = df_tmp.loc[df_tmp.index[0],'Ending_SoC']

        pDate = df_new['Date'].dt.date[idxEnd]
        pHour = df_new.loc[idxEnd, 'Time_of_Day'] +1
        pEndSoC = df_new.loc[idxEnd, 'Ending_SoC']

    return pDate,pHour,pEndSoC

###########################################################################

def Generate_DriverData (jsonData,dirName):

    pathDriverBeh = dirName+'/'+jsonData['pathGeneratedDriversData']
    # Create the appropriate output directory
    isExist = os.path.exists(pathDriverBeh)
    if not isExist:
        os.makedirs(pathDriverBeh)

    pathDriversData = pathDriverBeh+'/'+jsonData['pathDriversData']
    # Create the appropriate output directory
    isExist = os.path.exists(pathDriversData)
    if not isExist:
        os.makedirs(pathDriversData)

    mode = jsonData['checksMode']
    # Check the checksMode
    if (mode=="Strict"):
        strName1 = '/GeneratedData_DriverBehavior_StrictChecks_'
    elif (mode=="Looser"):
        strName1 = '/GeneratedData_DriverBehavior_LooserChecks_'
    elif (mode=="Min"):
        strName1 = '/GeneratedData_DriverBehavior_MinChecks_'
    else:
        print("\nERROR: Wrong configuration for variable 'checksMode'\nCheck .json file")
        sys.exit()

    strName2 = '.csv'

    numOfDrivers = jsonData['numOfDrivers']
    startDate = jsonData['startDate']
    endDate = jsonData['endDate']
    startDate = datetime.strptime(startDate, '%Y-%m-%d')
    endDate = datetime.strptime(endDate, '%Y-%m-%d') + timedelta(1)
    numOfDays = (endDate - startDate).days

    df_EVSpecs = Sampling_EV_Specs(numOfDrivers,jsonData)

    for mycsv in range(1,numOfDrivers+1):

        df_new = pd.DataFrame(columns=['Date','DriverID','Year','Month_of_Year','Day_of_Week','Time_of_Day',
                                       'EV_Model','Battery_Capacity(kWh)','Category',
                                       'Mean_Energy_Consumption(kWh/100km)','Max_DC_Power(kW)','Status',
                                       'Starting_SoC','Ending_SoC','Charger_Type','Charger_Power(kW)',
                                       'Charging_Time(mins)','Consumption_Charging(kW)',
                                       'Trip_Time(mins)','Trip_Distance(km)','Trip_Consumption(kwh)'])
        df_new['Date'] = pd.date_range(start = startDate, end = endDate, freq ='H')
        df_new['Year'] = df_new['Date'].dt.year
        df_new['Month_of_Year'] = df_new['Date'].dt.month
        df_new['Day_of_Week'] = df_new['Date'].dt.dayofweek + 1
        df_new['Time_of_Day'] = df_new['Date'].dt.hour +1
        df_new.drop(df_new.tail(1).index,inplace=True)

        # This is passed to 'Sampling_Charge_Data' for the case we want to make an extra sampling
        df_to4 = pd.DataFrame()
        df_DailyCharges = Sampling_Daily_Charges(numOfDays,0,jsonData)
        df_DailyCharges_Wend = Sampling_Daily_Charges(round(numOfDays/2),1,jsonData)
        prevEndSoC = 2
        df_ChargeSamples, df_EVSpecs = Sampling_Charge_Data(0,numOfDays*4,0,df_to4,df_EVSpecs,0,prevEndSoC,0,jsonData)

        strDriver = 'DR'
        driverName = "%s%s" % (strDriver, mycsv)

        df_new.loc[:,'DriverID'] = driverName
        df_new.loc[:,'EV_Model'] = df_ChargeSamples['EV_Model'].values[0]
        df_new.loc[:,'Battery_Capacity(kWh)'] = df_ChargeSamples['Battery_Capacity(kWh)'].values[0]
        df_new.loc[:,'Category'] = df_ChargeSamples['Category'].values[0]
        df_new.loc[:,'Mean_Energy_Consumption(kWh/100km)'] = df_ChargeSamples['Mean_Energy_Consumption(kWh/100km)'].values[0]
        df_new.loc[:,'Max_DC_Power(kW)'] = df_ChargeSamples['Max_DC_Power(kW)'].values[0]
        # This is passed to 'Sampling_Charge_Data' for the case we want to make an extra sampling
        df_to4['EV_Model'] = [df_new.loc[0,'EV_Model']]
        df_to4['Battery_Capacity(kWh)'] = df_new.loc[0,'Battery_Capacity(kWh)']
        df_to4['Category'] = df_new.loc[0,'Category']
        df_to4['Mean_Energy_Consumption(kWh/100km)'] = df_new.loc[0,'Mean_Energy_Consumption(kWh/100km)']
        df_to4['Max_DC_Power(kW)'] = df_new.loc[0,'Max_DC_Power(kW)']

        df_ChargeSamples_Wend, df_EVSpecs = Sampling_Charge_Data(1,numOfDays,0,df_to4,df_EVSpecs,0,prevEndSoC,1,jsonData)

        myRange = range(1,25)
        c1=0
        c2=0
        prevDate = df_new['Date'].dt.date[0]
        prevHour = 0
        # For the case of StrictChecks
        if (mode == "Strict"):
            for i in range(0,len(df_new),24):
                # Weekdays
                if ((df_new.loc[i,'Day_of_Week'] != 6) & (df_new.loc[i,'Day_of_Week'] != 7)):
                    if (df_new['Date'].dt.date[i] == (endDate - timedelta(1)).date()):
                        break
                    # Check that the next charging time is after the end of the previous one
                    # c1==0 is only for the first iteration, when we don't have a previous charge
                    if (df_new['Date'].dt.date[i]>prevDate or c1==0 ):
                        df_tmp = df_ChargeSamples.sample(n=1, replace=False)

                        if (df_tmp['Starting_SoC'].values[0] < prevEndSoC):
                            df_ChargeSamples = df_ChargeSamples.drop(df_tmp.index).reset_index(drop=True)
                        else:
                            prevHour = 0
                            df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour,df_to4,df_EVSpecs,1,prevEndSoC,0,jsonData)
                    else:
                        # If not, try to take another sample from the list, otherwise take a new sample
                        try:
                            df_tmp = df_ChargeSamples[(df_ChargeSamples['Start_Hour'] > prevHour) &
                                                      (df_ChargeSamples['Starting_SoC'] < prevEndSoC)].sample(n=1, replace=False)
                            df_ChargeSamples = df_ChargeSamples.drop(df_tmp.index).reset_index(drop=True)
                        except ValueError:
                            df_tmp,df_EVSpecs = Sampling_Charge_Data(1,1,prevHour,df_to4,df_EVSpecs,1,prevEndSoC,0,jsonData)

                    if df_DailyCharges.values[c1]==1:
                        # Do the 1 and only Charge
                        prevDate,prevHour,prevEndSoC = Case_Charges_1(df_new,df_tmp,i)

                    elif df_DailyCharges.values[c1]==2:
                        # Divide the 24-hours into 2 12-hours
                        bigBucket = np.array_split(np.array(myRange), 2)
                        # Do the 1st Charge
                        prevDate, prevHour,prevEndSoC = Case_Charges_1(df_new, df_tmp,i)
                        # If the end of the 1st charge is into the 1st 12-hours, do the 2nd charge
                        if ((df_new['Date'].dt.date[i] == prevDate) and (prevHour-1 in bigBucket[0])):
                            # Do the 2nd Charge
                            # Try to take another sample from the list, otherwise take a new sample
                            try:
                                df_tmp = df_ChargeSamples[(df_ChargeSamples['Start_Hour'] > prevHour) &
                                                          (df_ChargeSamples['Starting_SoC'] < prevEndSoC)].sample(n=1, replace=False)
                                df_ChargeSamples = df_ChargeSamples.drop(df_tmp.index).reset_index(drop=True)
                            except ValueError:
                                df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour, df_to4,df_EVSpecs,1,prevEndSoC,0,jsonData)
                            prevDate, prevHour,prevEndSoC = Case_Charges_1(df_new, df_tmp,i)

                    elif df_DailyCharges.values[c1] == 3:
                        # Divide the 24-hours into 3 8-hours
                        bigBucket = np.array_split(np.array(myRange), 3)
                        # Do the 1st Charge
                        prevDate, prevHour,prevEndSoC = Case_Charges_1(df_new, df_tmp,i)
                        # If the end of the 1st charge is into the 1st 8-hours, do the 2nd charge
                        if ((df_new['Date'].dt.date[i] == prevDate) and (prevHour-1 in bigBucket[0])):
                            # Do the 2nd Charge
                            # Try to take another sample from the list, otherwise take a new sample
                            try:
                                df_tmp = df_ChargeSamples[(df_ChargeSamples['Start_Hour'] > prevHour) &
                                                          (df_ChargeSamples['Starting_SoC'] < prevEndSoC)].sample(n=1, replace=False)
                                df_ChargeSamples = df_ChargeSamples.drop(df_tmp.index).reset_index(drop=True)
                            except ValueError:
                                df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour,df_to4,df_EVSpecs,1,prevEndSoC,0,jsonData)
                            prevDate, prevHour,prevEndSoC = Case_Charges_1(df_new, df_tmp,i)
                            # If the end of the 2nd charge is into the 2nd 8-hours, do the 3rd charge
                            if ((df_new['Date'].dt.date[i] == prevDate) and (prevHour - 1 in bigBucket[1])):
                                # Do the 3rd Charge
                                # Try to take another sample from the list, otherwise take a new sample
                                try:
                                    df_tmp = df_ChargeSamples[(df_ChargeSamples['Start_Hour'] > prevHour) &
                                                              (df_ChargeSamples['Starting_SoC'] < prevEndSoC)].sample(n=1, replace=False)
                                    df_ChargeSamples = df_ChargeSamples.drop(df_tmp.index).reset_index(drop=True)
                                except ValueError:
                                    df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour,df_to4,df_EVSpecs,1,prevEndSoC,0,jsonData)
                                prevDate, prevHour,prevEndSoC = Case_Charges_1(df_new, df_tmp,i)
                        # If the end of the 1st charge is into the 2nd 8-hours, do the 2nd charge
                        elif ((df_new['Date'].dt.date[i] == prevDate) and (prevHour-1 in bigBucket[1])):
                            # Do the 2nd Charge
                            # Try to take another sample from the list, otherwise take a new sample
                            try:
                                df_tmp = df_ChargeSamples[(df_ChargeSamples['Start_Hour'] > prevHour) &
                                                          (df_ChargeSamples['Starting_SoC'] < prevEndSoC)].sample(n=1, replace=False)
                                df_ChargeSamples = df_ChargeSamples.drop(df_tmp.index).reset_index(drop=True)
                            except ValueError:
                                df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour,df_to4,df_EVSpecs,1,prevEndSoC,0,jsonData)
                            prevDate, prevHour,prevEndSoC = Case_Charges_1(df_new, df_tmp,i)
                    else:
                        # Divide the 24-hours into 4 6-hours
                        bigBucket = np.array_split(np.array(myRange), 4)
                        # Do the 1st Charge
                        prevDate, prevHour,prevEndSoC = Case_Charges_1(df_new, df_tmp,i)
                        # If the end of the 1st charge is into the 1st 6-hours, do the 2nd charge
                        if ((df_new['Date'].dt.date[i] == prevDate) and (prevHour-1 in bigBucket[0])):
                            # Do the 2nd Charge
                            # Try to take another sample from the list, otherwise take a new sample
                            try:
                                df_tmp = df_ChargeSamples[(df_ChargeSamples['Start_Hour'] > prevHour) &
                                                          (df_ChargeSamples['Starting_SoC'] < prevEndSoC)].sample(n=1, replace=False)
                                df_ChargeSamples = df_ChargeSamples.drop(df_tmp.index).reset_index(drop=True)
                            except ValueError:
                                df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour,df_to4,df_EVSpecs,1,prevEndSoC,0,jsonData)
                            prevDate, prevHour,prevEndSoC = Case_Charges_1(df_new, df_tmp,i)
                            # If the end of the 2nd charge is into the 2nd 6-hours, do the 3rd charge
                            if ((df_new['Date'].dt.date[i] == prevDate) and (prevHour - 1 in bigBucket[1])):
                                # Do the 3rd Charge
                                # Try to take another sample from the list, otherwise take a new sample
                                try:
                                    df_tmp = df_ChargeSamples[(df_ChargeSamples['Start_Hour'] > prevHour) &
                                                              (df_ChargeSamples['Starting_SoC'] < prevEndSoC)].sample(n=1, replace=False)
                                    df_ChargeSamples = df_ChargeSamples.drop(df_tmp.index).reset_index(drop=True)
                                except ValueError:
                                    df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour,df_to4,df_EVSpecs,1,prevEndSoC,0,jsonData)
                                prevDate, prevHour,prevEndSoC = Case_Charges_1(df_new, df_tmp,i)
                                # If the end of the 3rd charge is into the 3rd 6-hours, do the 4th charge
                                if ((df_new['Date'].dt.date[i] == prevDate) and (prevHour - 1 in bigBucket[2])):
                                    # Do the 4th Charge
                                    # Try to take another sample from the list, otherwise take a new sample
                                    try:
                                        df_tmp = df_ChargeSamples[(df_ChargeSamples['Start_Hour'] > prevHour) &
                                                                  (df_ChargeSamples['Starting_SoC'] < prevEndSoC)].sample(n=1, replace=False)
                                        df_ChargeSamples = df_ChargeSamples.drop(df_tmp.index).reset_index(drop=True)
                                    except ValueError:
                                        df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour,df_to4,df_EVSpecs,1,prevEndSoC,0,jsonData)
                                    prevDate, prevHour,prevEndSoC = Case_Charges_1(df_new, df_tmp,i)
                            # If the end of the 2nd charge is into the 3rd 6-hours, do the 3rd charge
                            elif ((df_new['Date'].dt.date[i] == prevDate) and (prevHour - 1 in bigBucket[2])):
                                # Do the 3rd Charge
                                # Try to take another sample from the list, otherwise take a new sample
                                try:
                                    df_tmp = df_ChargeSamples[(df_ChargeSamples['Start_Hour'] > prevHour) &
                                                              (df_ChargeSamples['Starting_SoC'] < prevEndSoC)].sample(n=1, replace=False)
                                    df_ChargeSamples = df_ChargeSamples.drop(df_tmp.index).reset_index(drop=True)
                                except ValueError:
                                    df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour, df_to4,df_EVSpecs,1,prevEndSoC,0,jsonData)
                                prevDate, prevHour,prevEndSoC = Case_Charges_1(df_new, df_tmp,i)
                        # If the end of the 1st charge is into the 2nd 6-hours, do the 2nd charge
                        elif ((df_new['Date'].dt.date[i] == prevDate) and (prevHour-1 in bigBucket[1])):
                            # Do the 2nd Charge
                            # Try to take another sample from the list, otherwise take a new sample
                            try:
                                df_tmp = df_ChargeSamples[(df_ChargeSamples['Start_Hour'] > prevHour) &
                                                          (df_ChargeSamples['Starting_SoC'] < prevEndSoC)].sample(n=1, replace=False)
                                df_ChargeSamples = df_ChargeSamples.drop(df_tmp.index).reset_index(drop=True)
                            except ValueError:
                                df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour, df_to4,df_EVSpecs,1,prevEndSoC,0,jsonData)
                            prevDate, prevHour,prevEndSoC = Case_Charges_1(df_new, df_tmp,i)
                            # If the end of the 2nd charge is into the 3rd 6-hours, do the 3rd charge
                            if ((df_new['Date'].dt.date[i] == prevDate) and (prevHour - 1 in bigBucket[2])):
                                # Do the 3rd Charge
                                # Try to take another sample from the list, otherwise take a new sample
                                try:
                                    df_tmp = df_ChargeSamples[(df_ChargeSamples['Start_Hour'] > prevHour) &
                                                              (df_ChargeSamples['Starting_SoC'] < prevEndSoC)].sample(n=1, replace=False)
                                    df_ChargeSamples = df_ChargeSamples.drop(df_tmp.index).reset_index(drop=True)
                                except ValueError:
                                    df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour, df_to4,df_EVSpecs,1,prevEndSoC,0,jsonData)
                                prevDate, prevHour,prevEndSoC = Case_Charges_1(df_new, df_tmp,i)
                        # If the end of the 1st charge is into the 3rd 6-hours, do the 2nd charge
                        elif ((df_new['Date'].dt.date[i] == prevDate) and (prevHour-1 in bigBucket[2])):
                            # Do the 2nd Charge
                            # Try to take another sample from the list, otherwise take a new sample
                            try:
                                df_tmp = df_ChargeSamples[(df_ChargeSamples['Start_Hour'] > prevHour) &
                                                          (df_ChargeSamples['Starting_SoC'] < prevEndSoC)].sample(n=1, replace=False)
                                df_ChargeSamples = df_ChargeSamples.drop(df_tmp.index).reset_index(drop=True)
                            except ValueError:
                                df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour,df_to4,df_EVSpecs,1,prevEndSoC,0,jsonData)
                            prevDate, prevHour,prevEndSoC = Case_Charges_1(df_new, df_tmp,i)
                    c1 += 1
                # Weekend
                else:
                    if (df_new['Date'].dt.date[i] == (endDate - timedelta(1)).date()):
                        break
                    # Check that the next charging time is after the end of the previous one
                    # c1==0 is only for the first iteration, when we don't have a previous charge
                    if (df_new['Date'].dt.date[i] > prevDate or c2 == 0):
                        df_tmp = df_ChargeSamples_Wend.sample(n=1, replace=False)

                        if (df_tmp['Starting_SoC'].values[0] < prevEndSoC):
                            df_ChargeSamples_Wend = df_ChargeSamples_Wend.drop(df_tmp.index).reset_index(drop=True)
                        else:
                            prevHour = 0
                            df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour, df_to4,df_EVSpecs, 1, prevEndSoC, 1,jsonData)
                    else:
                        # If not, try to take another sample from the list, otherwise take a new sample
                        try:
                            df_tmp = df_ChargeSamples_Wend[(df_ChargeSamples_Wend['Start_Hour'] > prevHour) &
                                                      (df_ChargeSamples_Wend['Starting_SoC'] < prevEndSoC)].sample(n=1,
                                                                                                              replace=False)
                            df_ChargeSamples_Wend = df_ChargeSamples_Wend.drop(df_tmp.index).reset_index(drop=True)
                        except ValueError:
                            df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour, df_to4,df_EVSpecs, 1, prevEndSoC, 1,jsonData)

                    if df_DailyCharges_Wend.values[c2] == 1:
                        # Do the 1 and only Charge
                        prevDate, prevHour, prevEndSoC = Case_Charges_1(df_new, df_tmp,i)

                    elif df_DailyCharges_Wend.values[c2] == 2:
                        # Divide the 24-hours into 2 12-hours
                        bigBucket = np.array_split(np.array(myRange), 2)
                        # Do the 1st Charge
                        prevDate, prevHour, prevEndSoC = Case_Charges_1(df_new, df_tmp,i)
                        # If the end of the 1st charge is into the 1st 12-hours, do the 2nd charge
                        if ((df_new['Date'].dt.date[i] == prevDate) and (prevHour - 1 in bigBucket[0])):
                            # Do the 2nd Charge
                            # Try to take another sample from the list, otherwise take a new sample
                            try:
                                df_tmp = df_ChargeSamples_Wend[(df_ChargeSamples_Wend['Start_Hour'] > prevHour) &
                                                          (df_ChargeSamples_Wend['Starting_SoC'] < prevEndSoC)].sample(n=1,
                                                                                                                  replace=False)
                                df_ChargeSamples_Wend = df_ChargeSamples_Wend.drop(df_tmp.index).reset_index(drop=True)
                            except ValueError:
                                df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour, df_to4,df_EVSpecs, 1, prevEndSoC, 1,jsonData)
                            prevDate, prevHour, prevEndSoC = Case_Charges_1(df_new, df_tmp,i)

                    elif df_DailyCharges_Wend.values[c2] == 3:
                        # Divide the 24-hours into 3 8-hours
                        bigBucket = np.array_split(np.array(myRange), 3)
                        # Do the 1st Charge
                        prevDate, prevHour, prevEndSoC = Case_Charges_1(df_new, df_tmp,i)
                        # If the end of the 1st charge is into the 1st 8-hours, do the 2nd charge
                        if ((df_new['Date'].dt.date[i] == prevDate) and (prevHour - 1 in bigBucket[0])):
                            # Do the 2nd Charge
                            # Try to take another sample from the list, otherwise take a new sample
                            try:
                                df_tmp = df_ChargeSamples_Wend[(df_ChargeSamples_Wend['Start_Hour'] > prevHour) &
                                                          (df_ChargeSamples_Wend['Starting_SoC'] < prevEndSoC)].sample(n=1,
                                                                                                                  replace=False)
                                df_ChargeSamples_Wend = df_ChargeSamples_Wend.drop(df_tmp.index).reset_index(drop=True)
                            except ValueError:
                                df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour, df_to4,df_EVSpecs, 1, prevEndSoC, 1,jsonData)
                            prevDate, prevHour, prevEndSoC = Case_Charges_1(df_new, df_tmp,i)
                            # If the end of the 2nd charge is into the 2nd 8-hours, do the 3rd charge
                            if ((df_new['Date'].dt.date[i] == prevDate) and (prevHour - 1 in bigBucket[1])):
                                # Do the 3rd Charge
                                # Try to take another sample from the list, otherwise take a new sample
                                try:
                                    df_tmp = df_ChargeSamples_Wend[(df_ChargeSamples_Wend['Start_Hour'] > prevHour) &
                                                              (df_ChargeSamples_Wend['Starting_SoC'] < prevEndSoC)].sample(n=1,
                                                                                                                      replace=False)
                                    df_ChargeSamples_Wend = df_ChargeSamples_Wend.drop(df_tmp.index).reset_index(drop=True)
                                except ValueError:
                                    df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour, df_to4,df_EVSpecs, 1, prevEndSoC, 1,jsonData)
                                prevDate, prevHour, prevEndSoC = Case_Charges_1(df_new, df_tmp,i)
                        # If the end of the 1st charge is into the 2nd 8-hours, do the 2nd charge
                        elif ((df_new['Date'].dt.date[i] == prevDate) and (prevHour - 1 in bigBucket[1])):
                            # Do the 2nd Charge
                            # Try to take another sample from the list, otherwise take a new sample
                            try:
                                df_tmp = df_ChargeSamples_Wend[(df_ChargeSamples_Wend['Start_Hour'] > prevHour) &
                                                          (df_ChargeSamples_Wend['Starting_SoC'] < prevEndSoC)].sample(n=1,
                                                                                                                  replace=False)
                                df_ChargeSamples_Wend = df_ChargeSamples_Wend.drop(df_tmp.index).reset_index(drop=True)
                            except ValueError:
                                df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour, df_to4,df_EVSpecs, 1, prevEndSoC, 1,jsonData)
                            prevDate, prevHour, prevEndSoC = Case_Charges_1(df_new, df_tmp,i)
                    else:
                        # Divide the 24-hours into 4 6-hours
                        bigBucket = np.array_split(np.array(myRange), 4)
                        # Do the 1st Charge
                        prevDate, prevHour, prevEndSoC = Case_Charges_1(df_new, df_tmp,i)
                        # If the end of the 1st charge is into the 1st 6-hours, do the 2nd charge
                        if ((df_new['Date'].dt.date[i] == prevDate) and (prevHour - 1 in bigBucket[0])):
                            # Do the 2nd Charge
                            # Try to take another sample from the list, otherwise take a new sample
                            try:
                                df_tmp = df_ChargeSamples_Wend[(df_ChargeSamples_Wend['Start_Hour'] > prevHour) &
                                                          (df_ChargeSamples_Wend['Starting_SoC'] < prevEndSoC)].sample(n=1,
                                                                                                                  replace=False)
                                df_ChargeSamples_Wend = df_ChargeSamples_Wend.drop(df_tmp.index).reset_index(drop=True)
                            except ValueError:
                                df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour, df_to4,df_EVSpecs, 1, prevEndSoC, 1,jsonData)
                            prevDate, prevHour, prevEndSoC = Case_Charges_1(df_new, df_tmp,i)
                            # If the end of the 2nd charge is into the 2nd 6-hours, do the 3rd charge
                            if ((df_new['Date'].dt.date[i] == prevDate) and (prevHour - 1 in bigBucket[1])):
                                # Do the 3rd Charge
                                # Try to take another sample from the list, otherwise take a new sample
                                try:
                                    df_tmp = df_ChargeSamples_Wend[(df_ChargeSamples_Wend['Start_Hour'] > prevHour) &
                                                              (df_ChargeSamples_Wend['Starting_SoC'] < prevEndSoC)].sample(n=1,
                                                                                                                      replace=False)
                                    df_ChargeSamples_Wend = df_ChargeSamples_Wend.drop(df_tmp.index).reset_index(drop=True)
                                except ValueError:
                                    df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour, df_to4,df_EVSpecs, 1, prevEndSoC, 1,jsonData)
                                prevDate, prevHour, prevEndSoC = Case_Charges_1(df_new, df_tmp,i)
                                # If the end of the 3rd charge is into the 3rd 6-hours, do the 4th charge
                                if ((df_new['Date'].dt.date[i] == prevDate) and (prevHour - 1 in bigBucket[2])):
                                    # Do the 4th Charge
                                    # Try to take another sample from the list, otherwise take a new sample
                                    try:
                                        df_tmp = df_ChargeSamples_Wend[(df_ChargeSamples_Wend['Start_Hour'] > prevHour) &
                                                                  (df_ChargeSamples_Wend['Starting_SoC'] < prevEndSoC)].sample(n=1,
                                                                                                                          replace=False)
                                        df_ChargeSamples_Wend = df_ChargeSamples_Wend.drop(df_tmp.index).reset_index(drop=True)
                                    except ValueError:
                                        df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour, df_to4,df_EVSpecs, 1, prevEndSoC, 1,jsonData)
                                    prevDate, prevHour, prevEndSoC = Case_Charges_1(df_new, df_tmp,i)
                            # If the end of the 2nd charge is into the 3rd 6-hours, do the 3rd charge
                            elif ((df_new['Date'].dt.date[i] == prevDate) and (prevHour - 1 in bigBucket[2])):
                                # Do the 3rd Charge
                                # Try to take another sample from the list, otherwise take a new sample
                                try:
                                    df_tmp = df_ChargeSamples_Wend[(df_ChargeSamples_Wend['Start_Hour'] > prevHour) &
                                                              (df_ChargeSamples_Wend['Starting_SoC'] < prevEndSoC)].sample(n=1,
                                                                                                                      replace=False)
                                    df_ChargeSamples_Wend = df_ChargeSamples_Wend.drop(df_tmp.index).reset_index(drop=True)
                                except ValueError:
                                    df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour, df_to4,df_EVSpecs, 1, prevEndSoC, 1,jsonData)
                                prevDate, prevHour, prevEndSoC = Case_Charges_1(df_new, df_tmp,i)
                        # If the end of the 1st charge is into the 2nd 6-hours, do the 2nd charge
                        elif ((df_new['Date'].dt.date[i] == prevDate) and (prevHour - 1 in bigBucket[1])):
                            # Do the 2nd Charge
                            # Try to take another sample from the list, otherwise take a new sample
                            try:
                                df_tmp = df_ChargeSamples_Wend[(df_ChargeSamples_Wend['Start_Hour'] > prevHour) &
                                                          (df_ChargeSamples_Wend['Starting_SoC'] < prevEndSoC)].sample(n=1,
                                                                                                                  replace=False)
                                df_ChargeSamples_Wend = df_ChargeSamples_Wend.drop(df_tmp.index).reset_index(drop=True)
                            except ValueError:
                                df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour, df_to4,df_EVSpecs, 1, prevEndSoC, 1,jsonData)
                            prevDate, prevHour, prevEndSoC = Case_Charges_1(df_new, df_tmp,i)
                            # If the end of the 2nd charge is into the 3rd 6-hours, do the 3rd charge
                            if ((df_new['Date'].dt.date[i] == prevDate) and (prevHour - 1 in bigBucket[2])):
                                # Do the 3rd Charge
                                # Try to take another sample from the list, otherwise take a new sample
                                try:
                                    df_tmp = df_ChargeSamples_Wend[(df_ChargeSamples_Wend['Start_Hour'] > prevHour) &
                                                              (df_ChargeSamples_Wend['Starting_SoC'] < prevEndSoC)].sample(n=1,
                                                                                                                      replace=False)
                                    df_ChargeSamples_Wend = df_ChargeSamples_Wend.drop(df_tmp.index).reset_index(drop=True)
                                except ValueError:
                                    df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour, df_to4,df_EVSpecs, 1, prevEndSoC, 1,jsonData)
                                prevDate, prevHour, prevEndSoC = Case_Charges_1(df_new, df_tmp,i)
                        # If the end of the 1st charge is into the 3rd 6-hours, do the 2nd charge
                        elif ((df_new['Date'].dt.date[i] == prevDate) and (prevHour - 1 in bigBucket[2])):
                            # Do the 2nd Charge
                            # Try to take another sample from the list, otherwise take a new sample
                            try:
                                df_tmp = df_ChargeSamples_Wend[(df_ChargeSamples_Wend['Start_Hour'] > prevHour) &
                                                          (df_ChargeSamples_Wend['Starting_SoC'] < prevEndSoC)].sample(n=1,
                                                                                                                  replace=False)
                                df_ChargeSamples_Wend = df_ChargeSamples_Wend.drop(df_tmp.index).reset_index(drop=True)
                            except ValueError:
                                df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour, df_to4,df_EVSpecs, 1, prevEndSoC, 1,jsonData)
                            prevDate, prevHour, prevEndSoC = Case_Charges_1(df_new, df_tmp,i)
                    c2+=1
        # For the case of LooserChecks
        elif (mode == "Looser"):
            for i in range(0, len(df_new), 24):
                # Weekdays
                if ((df_new.loc[i, 'Day_of_Week'] != 6) & (df_new.loc[i, 'Day_of_Week'] != 7)):
                    if (df_new['Date'].dt.date[i] == (endDate - timedelta(1)).date()):
                        break
                    # Check that the next charging time is after the end of the previous one
                    # c1==0 is only for the first iteration, when we don't have a previous charge
                    if (df_new['Date'].dt.date[i] > prevDate or c1 == 0):
                        df_tmp = df_ChargeSamples.sample(n=1, replace=False)

                        if (df_tmp['Starting_SoC'].values[0] < prevEndSoC):
                            df_ChargeSamples = df_ChargeSamples.drop(df_tmp.index).reset_index(drop=True)
                        else:
                            prevHour = 0
                            df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour, df_to4,df_EVSpecs, 1, prevEndSoC, 0, jsonData)
                    else:
                        # If not, try to take another sample from the list, otherwise take a new sample
                        try:
                            df_tmp = df_ChargeSamples[(df_ChargeSamples['Start_Hour'] > prevHour) &
                                                      (df_ChargeSamples['Starting_SoC'] < prevEndSoC)].sample(n=1,
                                                                                                              replace=False)
                            df_ChargeSamples = df_ChargeSamples.drop(df_tmp.index).reset_index(drop=True)
                        except ValueError:
                            df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour, df_to4,df_EVSpecs, 1, prevEndSoC, 0, jsonData)

                    if df_DailyCharges.values[c1] == 1:
                        # Do the 1 and only Charge
                        prevDate, prevHour, prevEndSoC = Case_Charges_1(df_new, df_tmp,i)

                    elif df_DailyCharges.values[c1] == 2:
                        # Do the 1st Charge
                        prevDate, prevHour, prevEndSoC = Case_Charges_1(df_new, df_tmp,i)
                        # If the end of the 1st charge ends before 23:00, do the 2nd charge
                        if ((df_new['Date'].dt.date[i] == prevDate) and (prevHour < 24)):
                            # Do the 2nd Charge
                            # Try to take another sample from the list, otherwise take a new sample
                            try:
                                df_tmp = df_ChargeSamples[(df_ChargeSamples['Start_Hour'] > prevHour) &
                                                          (df_ChargeSamples['Starting_SoC'] < prevEndSoC)].sample(n=1,
                                                                                                                  replace=False)
                                df_ChargeSamples = df_ChargeSamples.drop(df_tmp.index).reset_index(drop=True)
                            except ValueError:
                                df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour, df_to4,df_EVSpecs, 1, prevEndSoC, 0, jsonData)
                            prevDate, prevHour, prevEndSoC = Case_Charges_1(df_new, df_tmp,i)

                    elif df_DailyCharges.values[c1] == 3:
                        # Do the 1st Charge
                        prevDate, prevHour, prevEndSoC = Case_Charges_1(df_new, df_tmp,i)
                        # If the end of the 1st charge ends before 23:00, do the 2nd charge
                        if ((df_new['Date'].dt.date[i] == prevDate) and (prevHour < 24)):
                            # Do the 2nd Charge
                            # Try to take another sample from the list, otherwise take a new sample
                            try:
                                df_tmp = df_ChargeSamples[(df_ChargeSamples['Start_Hour'] > prevHour) &
                                                          (df_ChargeSamples['Starting_SoC'] < prevEndSoC)].sample(n=1,
                                                                                                                  replace=False)
                                df_ChargeSamples = df_ChargeSamples.drop(df_tmp.index).reset_index(drop=True)
                            except ValueError:
                                df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour, df_to4,df_EVSpecs, 1, prevEndSoC, 0, jsonData)
                            prevDate, prevHour, prevEndSoC = Case_Charges_1(df_new, df_tmp,i)
                            # If the end of the 2nd charge ends before 23:00, do the 3rd charge
                            if ((df_new['Date'].dt.date[i] == prevDate) and (prevHour < 24)):
                                # Do the 3rd Charge
                                # Try to take another sample from the list, otherwise take a new sample
                                try:
                                    df_tmp = df_ChargeSamples[(df_ChargeSamples['Start_Hour'] > prevHour) &
                                                              (df_ChargeSamples['Starting_SoC'] < prevEndSoC)].sample(n=1,
                                                                                                                      replace=False)
                                    df_ChargeSamples = df_ChargeSamples.drop(df_tmp.index).reset_index(drop=True)
                                except ValueError:
                                    df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour, df_to4,df_EVSpecs, 1, prevEndSoC, 0, jsonData)
                                prevDate, prevHour, prevEndSoC = Case_Charges_1(df_new, df_tmp,i)

                    else:
                        # Do the 1st Charge
                        prevDate, prevHour, prevEndSoC = Case_Charges_1(df_new, df_tmp,i)
                        # If the end of the 1st charge ends before 23:00, do the 2nd charge
                        if ((df_new['Date'].dt.date[i] == prevDate) and (prevHour < 24)):
                            # Do the 2nd Charge
                            # Try to take another sample from the list, otherwise take a new sample
                            try:
                                df_tmp = df_ChargeSamples[(df_ChargeSamples['Start_Hour'] > prevHour) &
                                                          (df_ChargeSamples['Starting_SoC'] < prevEndSoC)].sample(n=1,
                                                                                                                  replace=False)
                                df_ChargeSamples = df_ChargeSamples.drop(df_tmp.index).reset_index(drop=True)
                            except ValueError:
                                df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour, df_to4,df_EVSpecs, 1, prevEndSoC, 0, jsonData)
                            prevDate, prevHour, prevEndSoC = Case_Charges_1(df_new, df_tmp,i)
                            # If the end of the 2nd charge ends before 23:00, do the 3rd charge
                            if ((df_new['Date'].dt.date[i] == prevDate) and (prevHour < 24)):
                                # Do the 3rd Charge
                                # Try to take another sample from the list, otherwise take a new sample
                                try:
                                    df_tmp = df_ChargeSamples[(df_ChargeSamples['Start_Hour'] > prevHour) &
                                                              (df_ChargeSamples['Starting_SoC'] < prevEndSoC)].sample(n=1,
                                                                                                                      replace=False)
                                    df_ChargeSamples = df_ChargeSamples.drop(df_tmp.index).reset_index(drop=True)
                                except ValueError:
                                    df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour, df_to4,df_EVSpecs, 1, prevEndSoC, 0, jsonData)
                                prevDate, prevHour, prevEndSoC = Case_Charges_1(df_new, df_tmp,i)
                                # If the end of the 3rd charge ends before 23:00, do the 4th charge
                                if ((df_new['Date'].dt.date[i] == prevDate) and (prevHour < 24)):
                                    # Do the 4th Charge
                                    # Try to take another sample from the list, otherwise take a new sample
                                    try:
                                        df_tmp = df_ChargeSamples[(df_ChargeSamples['Start_Hour'] > prevHour) &
                                                                  (df_ChargeSamples['Starting_SoC'] < prevEndSoC)].sample(
                                            n=1, replace=False)
                                        df_ChargeSamples = df_ChargeSamples.drop(df_tmp.index).reset_index(drop=True)
                                    except ValueError:
                                        df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour, df_to4,df_EVSpecs, 1, prevEndSoC, 0, jsonData)
                                    prevDate, prevHour, prevEndSoC = Case_Charges_1(df_new, df_tmp,i)
                    c1 += 1
                # Weekend
                else:
                    if (df_new['Date'].dt.date[i] == (endDate - timedelta(1)).date()):
                        break
                    # Check that the next charging time is after the end of the previous one
                    # c2==0 is only for the first iteration, when we don't have a previous charge
                    if (df_new['Date'].dt.date[i] > prevDate or c2 == 0):
                        df_tmp = df_ChargeSamples_Wend.sample(n=1, replace=False)

                        if (df_tmp['Starting_SoC'].values[0] < prevEndSoC):
                            df_ChargeSamples_Wend = df_ChargeSamples_Wend.drop(df_tmp.index).reset_index(drop=True)
                        else:
                            prevHour = 0
                            df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour, df_to4,df_EVSpecs, 1, prevEndSoC, 1, jsonData)
                    else:
                        # If not, try to take another sample from the list, otherwise take a new sample
                        try:
                            df_tmp = df_ChargeSamples_Wend[(df_ChargeSamples_Wend['Start_Hour'] > prevHour) &
                                                           (df_ChargeSamples_Wend['Starting_SoC'] < prevEndSoC)].sample(n=1,
                                                                                                                        replace=False)
                            df_ChargeSamples_Wend = df_ChargeSamples_Wend.drop(df_tmp.index).reset_index(drop=True)
                        except ValueError:
                            df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour, df_to4,df_EVSpecs, 1, prevEndSoC, 1, jsonData)

                    if df_DailyCharges_Wend.values[c2] == 1:
                        # Do the 1 and only Charge
                        prevDate, prevHour, prevEndSoC = Case_Charges_1(df_new, df_tmp,i)
                    elif df_DailyCharges_Wend.values[c2] == 2:
                        # Do the 1st Charge
                        prevDate, prevHour, prevEndSoC = Case_Charges_1(df_new, df_tmp,i)
                        # If the end of the 1st charge ends before 23:00, do the 2nd charge
                        if ((df_new['Date'].dt.date[i] == prevDate) and (prevHour < 24)):
                            # Do the 2nd Charge
                            # Try to take another sample from the list, otherwise take a new sample
                            try:
                                df_tmp = df_ChargeSamples_Wend[(df_ChargeSamples_Wend['Start_Hour'] > prevHour) &
                                                               (df_ChargeSamples_Wend['Starting_SoC'] < prevEndSoC)].sample(
                                    n=1,
                                    replace=False)
                                df_ChargeSamples_Wend = df_ChargeSamples_Wend.drop(df_tmp.index).reset_index(drop=True)
                            except ValueError:
                                df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour, df_to4,df_EVSpecs, 1, prevEndSoC, 1, jsonData)
                            prevDate, prevHour, prevEndSoC = Case_Charges_1(df_new, df_tmp,i)

                    elif df_DailyCharges_Wend.values[c2] == 3:
                        # Do the 1st Charge
                        prevDate, prevHour, prevEndSoC = Case_Charges_1(df_new, df_tmp,i)
                        # If the end of the 1st charge ends before 23:00, do the 2nd charge
                        if ((df_new['Date'].dt.date[i] == prevDate) and (prevHour < 24)):
                            # Do the 2nd Charge
                            # Try to take another sample from the list, otherwise take a new sample
                            try:
                                df_tmp = df_ChargeSamples_Wend[(df_ChargeSamples_Wend['Start_Hour'] > prevHour) &
                                                               (df_ChargeSamples_Wend['Starting_SoC'] < prevEndSoC)].sample(
                                    n=1,
                                    replace=False)
                                df_ChargeSamples_Wend = df_ChargeSamples_Wend.drop(df_tmp.index).reset_index(drop=True)
                            except ValueError:
                                df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour, df_to4,df_EVSpecs, 1, prevEndSoC, 1, jsonData)
                            prevDate, prevHour, prevEndSoC = Case_Charges_1(df_new, df_tmp,i)
                            # If the end of the 2nd charge ends before 23:00, do the 3rd charge
                            if ((df_new['Date'].dt.date[i] == prevDate) and (prevHour < 24)):
                                # Do the 3rd Charge
                                # Try to take another sample from the list, otherwise take a new sample
                                try:
                                    df_tmp = df_ChargeSamples_Wend[(df_ChargeSamples_Wend['Start_Hour'] > prevHour) &
                                                                   (df_ChargeSamples_Wend[
                                                                        'Starting_SoC'] < prevEndSoC)].sample(n=1,
                                                                                                              replace=False)
                                    df_ChargeSamples_Wend = df_ChargeSamples_Wend.drop(df_tmp.index).reset_index(drop=True)
                                except ValueError:
                                    df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour, df_to4,df_EVSpecs, 1, prevEndSoC, 1, jsonData)
                                prevDate, prevHour, prevEndSoC = Case_Charges_1(df_new, df_tmp,i)

                    else:
                        # Do the 1st Charge
                        prevDate, prevHour, prevEndSoC = Case_Charges_1(df_new, df_tmp,i)
                        # If the end of the 1st charge ends before 23:00, do the 2nd charge
                        if ((df_new['Date'].dt.date[i] == prevDate) and (prevHour < 24)):
                            # Do the 2nd Charge
                            # Try to take another sample from the list, otherwise take a new sample
                            try:
                                df_tmp = df_ChargeSamples_Wend[(df_ChargeSamples_Wend['Start_Hour'] > prevHour) &
                                                               (df_ChargeSamples_Wend['Starting_SoC'] < prevEndSoC)].sample(
                                    n=1,
                                    replace=False)
                                df_ChargeSamples_Wend = df_ChargeSamples_Wend.drop(df_tmp.index).reset_index(drop=True)
                            except ValueError:
                                df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour, df_to4,df_EVSpecs, 1, prevEndSoC, 1, jsonData)
                            prevDate, prevHour, prevEndSoC = Case_Charges_1(df_new, df_tmp,i)
                            # If the end of the 2nd charge ends before 23:00, do the 3rd charge
                            if ((df_new['Date'].dt.date[i] == prevDate) and (prevHour < 24)):
                                # Do the 3rd Charge
                                # Try to take another sample from the list, otherwise take a new sample
                                try:
                                    df_tmp = df_ChargeSamples_Wend[(df_ChargeSamples_Wend['Start_Hour'] > prevHour) &
                                                                   (df_ChargeSamples_Wend[
                                                                        'Starting_SoC'] < prevEndSoC)].sample(n=1,
                                                                                                              replace=False)
                                    df_ChargeSamples_Wend = df_ChargeSamples_Wend.drop(df_tmp.index).reset_index(drop=True)
                                except ValueError:
                                    df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour, df_to4,df_EVSpecs, 1, prevEndSoC, 1, jsonData)
                                prevDate, prevHour, prevEndSoC = Case_Charges_1(df_new, df_tmp,i)
                                # If the end of the 3rd charge ends before 23:00, do the 4th charge
                                if ((df_new['Date'].dt.date[i] == prevDate) and (prevHour < 24)):
                                    # Do the 4th Charge
                                    # Try to take another sample from the list, otherwise take a new sample
                                    try:
                                        df_tmp = df_ChargeSamples_Wend[(df_ChargeSamples_Wend['Start_Hour'] > prevHour) &
                                                                       (df_ChargeSamples_Wend[
                                                                            'Starting_SoC'] < prevEndSoC)].sample(n=1,
                                                                                                                  replace=False)
                                        df_ChargeSamples_Wend = df_ChargeSamples_Wend.drop(df_tmp.index).reset_index(
                                            drop=True)
                                    except ValueError:
                                        df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour, df_to4,df_EVSpecs, 1, prevEndSoC, 1, jsonData)
                                    prevDate, prevHour, prevEndSoC = Case_Charges_1(df_new, df_tmp,i)
                    c2 += 1
        # For the case of MinChecks
        else:
            for i in range(0, len(df_new), 24):
                # Weekdays
                if ((df_new.loc[i, 'Day_of_Week'] != 6) & (df_new.loc[i, 'Day_of_Week'] != 7)):
                    if (df_new['Date'].dt.date[i] == (endDate - timedelta(1)).date()):
                        break
                    # Check that the next charging time is after the end of the previous one
                    # c1==0 is only for the first iteration, when we don't have a previous charge
                    if (df_new['Date'].dt.date[i] > prevDate or c1 == 0):
                        df_tmp = df_ChargeSamples.sample(n=1, replace=False)

                        if (df_tmp['Starting_SoC'].values[0] < prevEndSoC):
                            df_ChargeSamples = df_ChargeSamples.drop(df_tmp.index).reset_index(drop=True)
                        else:
                            prevHour = 0
                            df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour, df_to4,df_EVSpecs, 1, prevEndSoC, 0, jsonData)
                    else:
                        # If not, try to take another sample from the list, otherwise take a new sample
                        try:
                            df_tmp = df_ChargeSamples[(df_ChargeSamples['Start_Hour'] > prevHour) &
                                                      (df_ChargeSamples['Starting_SoC'] < prevEndSoC)].sample(n=1,
                                                                                                              replace=False)
                            df_ChargeSamples = df_ChargeSamples.drop(df_tmp.index).reset_index(drop=True)
                        except ValueError:
                            df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour, df_to4,df_EVSpecs, 1, prevEndSoC, 0, jsonData)

                    if df_DailyCharges.values[c1] == 1:
                        # Do the 1 and only Charge
                        prevDate, prevHour, prevEndSoC = Case_Charges_1(df_new, df_tmp,i)

                    elif df_DailyCharges.values[c1] == 2:
                        # Do the 1st Charge
                        prevDate, prevHour, prevEndSoC = Case_Charges_1(df_new, df_tmp,i)
                        # Do the 2nd Charge
                        # Try to take another sample from the list, otherwise take a new sample
                        try:
                            df_tmp = df_ChargeSamples[(df_ChargeSamples['Start_Hour'] > prevHour) &
                                                      (df_ChargeSamples['Starting_SoC'] < prevEndSoC)].sample(n=1,
                                                                                                              replace=False)
                            df_ChargeSamples = df_ChargeSamples.drop(df_tmp.index).reset_index(drop=True)
                        except ValueError:
                            df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour, df_to4,df_EVSpecs, 1, prevEndSoC, 0, jsonData)
                        prevDate, prevHour, prevEndSoC = Case_Charges_1(df_new, df_tmp,i)

                    elif df_DailyCharges.values[c1] == 3:
                        # Do the 1st Charge
                        prevDate, prevHour, prevEndSoC = Case_Charges_1(df_new, df_tmp,i)
                        # Do the 2nd Charge
                        # Try to take another sample from the list, otherwise take a new sample
                        try:
                            df_tmp = df_ChargeSamples[(df_ChargeSamples['Start_Hour'] > prevHour) &
                                                      (df_ChargeSamples['Starting_SoC'] < prevEndSoC)].sample(n=1,
                                                                                                              replace=False)
                            df_ChargeSamples = df_ChargeSamples.drop(df_tmp.index).reset_index(drop=True)
                        except ValueError:
                            df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour, df_to4,df_EVSpecs, 1, prevEndSoC, 0, jsonData)
                        prevDate, prevHour, prevEndSoC = Case_Charges_1(df_new, df_tmp,i)
                        # Do the 3rd Charge
                        # Try to take another sample from the list, otherwise take a new sample
                        try:
                            df_tmp = df_ChargeSamples[(df_ChargeSamples['Start_Hour'] > prevHour) &
                                                      (df_ChargeSamples['Starting_SoC'] < prevEndSoC)].sample(n=1,
                                                                                                              replace=False)
                            df_ChargeSamples = df_ChargeSamples.drop(df_tmp.index).reset_index(drop=True)
                        except ValueError:
                            df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour, df_to4,df_EVSpecs, 1, prevEndSoC, 0, jsonData)
                        prevDate, prevHour, prevEndSoC = Case_Charges_1(df_new, df_tmp,i)

                    else:
                        # Do the 1st Charge
                        prevDate, prevHour, prevEndSoC = Case_Charges_1(df_new, df_tmp,i)
                        # Do the 2nd Charge
                        # Try to take another sample from the list, otherwise take a new sample
                        try:
                            df_tmp = df_ChargeSamples[(df_ChargeSamples['Start_Hour'] > prevHour) &
                                                      (df_ChargeSamples['Starting_SoC'] < prevEndSoC)].sample(n=1,
                                                                                                              replace=False)
                            df_ChargeSamples = df_ChargeSamples.drop(df_tmp.index).reset_index(drop=True)
                        except ValueError:
                            df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour, df_to4,df_EVSpecs, 1, prevEndSoC, 0, jsonData)
                        prevDate, prevHour, prevEndSoC = Case_Charges_1(df_new, df_tmp,i)
                        # Do the 3rd Charge
                        # Try to take another sample from the list, otherwise take a new sample
                        try:
                            df_tmp = df_ChargeSamples[(df_ChargeSamples['Start_Hour'] > prevHour) &
                                                      (df_ChargeSamples['Starting_SoC'] < prevEndSoC)].sample(n=1,
                                                                                                              replace=False)
                            df_ChargeSamples = df_ChargeSamples.drop(df_tmp.index).reset_index(drop=True)
                        except ValueError:
                            df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour, df_to4,df_EVSpecs, 1, prevEndSoC, 0, jsonData)
                        prevDate, prevHour, prevEndSoC = Case_Charges_1(df_new, df_tmp,i)
                        # Do the 4th Charge
                        # Try to take another sample from the list, otherwise take a new sample
                        try:
                            df_tmp = df_ChargeSamples[(df_ChargeSamples['Start_Hour'] > prevHour) &
                                                      (df_ChargeSamples['Starting_SoC'] < prevEndSoC)].sample(n=1,
                                                                                                              replace=False)
                            df_ChargeSamples = df_ChargeSamples.drop(df_tmp.index).reset_index(drop=True)
                        except ValueError:
                            df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour, df_to4,df_EVSpecs, 1, prevEndSoC, 0, jsonData)
                        prevDate, prevHour, prevEndSoC = Case_Charges_1(df_new, df_tmp,i)
                    c1 += 1
                # Weekend
                else:
                    if (df_new['Date'].dt.date[i] == (endDate - timedelta(1)).date()):
                        break
                    # Check that the next charging time is after the end of the previous one
                    # c2==0 is only for the first iteration, when we don't have a previous charge
                    if (df_new['Date'].dt.date[i] > prevDate or c2 == 0):
                        df_tmp = df_ChargeSamples_Wend.sample(n=1, replace=False)

                        if (df_tmp['Starting_SoC'].values[0] < prevEndSoC):
                            df_ChargeSamples_Wend = df_ChargeSamples_Wend.drop(df_tmp.index).reset_index(drop=True)
                        else:
                            prevHour = 0
                            df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour, df_to4,df_EVSpecs, 1, prevEndSoC, 1, jsonData)
                    else:
                        # If not, try to take another sample from the list, otherwise take a new sample
                        try:
                            df_tmp = df_ChargeSamples_Wend[(df_ChargeSamples_Wend['Start_Hour'] > prevHour) &
                                                           (df_ChargeSamples_Wend['Starting_SoC'] < prevEndSoC)].sample(n=1,
                                                                                                                        replace=False)
                            df_ChargeSamples_Wend = df_ChargeSamples_Wend.drop(df_tmp.index).reset_index(drop=True)
                        except ValueError:
                            df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour, df_to4,df_EVSpecs, 1, prevEndSoC, 1, jsonData)

                    if df_DailyCharges_Wend.values[c2] == 1:
                        # Do the 1 and only Charge
                        prevDate, prevHour, prevEndSoC = Case_Charges_1(df_new, df_tmp,i)
                    elif df_DailyCharges_Wend.values[c2] == 2:
                        # Do the 1st Charge
                        prevDate, prevHour, prevEndSoC = Case_Charges_1(df_new, df_tmp,i)
                        # Do the 2nd Charge
                        # Try to take another sample from the list, otherwise take a new sample
                        try:
                            df_tmp = df_ChargeSamples_Wend[(df_ChargeSamples_Wend['Start_Hour'] > prevHour) &
                                                           (df_ChargeSamples_Wend['Starting_SoC'] < prevEndSoC)].sample(n=1,
                                                                                                                        replace=False)
                            df_ChargeSamples_Wend = df_ChargeSamples_Wend.drop(df_tmp.index).reset_index(drop=True)
                        except ValueError:
                            df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour, df_to4,df_EVSpecs, 1, prevEndSoC, 1, jsonData)
                        prevDate, prevHour, prevEndSoC = Case_Charges_1(df_new, df_tmp,i)

                    elif df_DailyCharges_Wend.values[c2] == 3:
                        # Do the 1st Charge
                        prevDate, prevHour, prevEndSoC = Case_Charges_1(df_new, df_tmp,i)
                        # Do the 2nd Charge
                        # Try to take another sample from the list, otherwise take a new sample
                        try:
                            df_tmp = df_ChargeSamples_Wend[(df_ChargeSamples_Wend['Start_Hour'] > prevHour) &
                                                           (df_ChargeSamples_Wend['Starting_SoC'] < prevEndSoC)].sample(n=1,
                                                                                                                        replace=False)
                            df_ChargeSamples_Wend = df_ChargeSamples_Wend.drop(df_tmp.index).reset_index(drop=True)
                        except ValueError:
                            df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour, df_to4,df_EVSpecs, 1, prevEndSoC, 1, jsonData)
                        prevDate, prevHour, prevEndSoC = Case_Charges_1(df_new, df_tmp,i)
                        # Do the 3rd Charge
                        # Try to take another sample from the list, otherwise take a new sample
                        try:
                            df_tmp = df_ChargeSamples_Wend[(df_ChargeSamples_Wend['Start_Hour'] > prevHour) &
                                                           (df_ChargeSamples_Wend['Starting_SoC'] < prevEndSoC)].sample(n=1,
                                                                                                                        replace=False)
                            df_ChargeSamples_Wend = df_ChargeSamples_Wend.drop(df_tmp.index).reset_index(drop=True)
                        except ValueError:
                            df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour, df_to4,df_EVSpecs, 1, prevEndSoC, 1, jsonData)
                        prevDate, prevHour, prevEndSoC = Case_Charges_1(df_new, df_tmp,i)

                    else:
                        # Do the 1st Charge
                        prevDate, prevHour, prevEndSoC = Case_Charges_1(df_new, df_tmp,i)
                        # Do the 2nd Charge
                        # Try to take another sample from the list, otherwise take a new sample
                        try:
                            df_tmp = df_ChargeSamples_Wend[(df_ChargeSamples_Wend['Start_Hour'] > prevHour) &
                                                           (df_ChargeSamples_Wend['Starting_SoC'] < prevEndSoC)].sample(n=1,
                                                                                                                        replace=False)
                            df_ChargeSamples_Wend = df_ChargeSamples_Wend.drop(df_tmp.index).reset_index(drop=True)
                        except ValueError:
                            df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour, df_to4,df_EVSpecs, 1, prevEndSoC, 1, jsonData)
                        prevDate, prevHour, prevEndSoC = Case_Charges_1(df_new, df_tmp,i)
                        # Do the 3rd Charge
                        # Try to take another sample from the list, otherwise take a new sample
                        try:
                            df_tmp = df_ChargeSamples_Wend[(df_ChargeSamples_Wend['Start_Hour'] > prevHour) &
                                                           (df_ChargeSamples_Wend['Starting_SoC'] < prevEndSoC)].sample(n=1,
                                                                                                                        replace=False)
                            df_ChargeSamples_Wend = df_ChargeSamples_Wend.drop(df_tmp.index).reset_index(drop=True)
                        except ValueError:
                            df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour, df_to4,df_EVSpecs, 1, prevEndSoC, 1, jsonData)
                        prevDate, prevHour, prevEndSoC = Case_Charges_1(df_new, df_tmp,i)
                        # Do the 4th Charge
                        # Try to take another sample from the list, otherwise take a new sample
                        try:
                            df_tmp = df_ChargeSamples_Wend[(df_ChargeSamples_Wend['Start_Hour'] > prevHour) &
                                                           (df_ChargeSamples_Wend['Starting_SoC'] < prevEndSoC)].sample(n=1,
                                                                                                                        replace=False)
                            df_ChargeSamples_Wend = df_ChargeSamples_Wend.drop(df_tmp.index).reset_index(drop=True)
                        except ValueError:
                            df_tmp,df_EVSpecs = Sampling_Charge_Data(1, 1, prevHour, df_to4,df_EVSpecs, 1, prevEndSoC, 1, jsonData)
                        prevDate, prevHour, prevEndSoC = Case_Charges_1(df_new, df_tmp,i)
                    c2 += 1

        df_new['Date'] = df_new['Date'].dt.date
        # df_gen.drop(df_gen.columns[0], axis = 1, inplace = True)
        df_vel = pd.read_csv(jsonData['pathFreqTableVelocityWdays'])
        df_vel_Wend = pd.read_csv(jsonData['pathFreqTableVelocityWend'])
        df_tmp0 = pd.DataFrame()
        idx0 = 0
        flag = 0
        # Iterate the whole dataframe to complete the "necessary" trips
        for index, row in df_new.iterrows():
            if (pd.notnull(df_new.loc[index, 'Starting_SoC']) and flag==0):
                # Keep the row with charge
                idx0 = index
                df_tmp0 = df_new.loc[index]
                if pd.isna(df_new.loc[idx0+1, 'Starting_SoC']):
                    flag = 1
                else:
                    flag = 0
            elif (pd.notnull(df_new.loc[index, 'Starting_SoC']) and flag==1):
                # Keep the row with the next different charge
                # and make all the calculations for the trip between these 2 charges
                idx1 = index
                df_tmp1 = df_new.loc[index]
                SoCDiff = df_tmp0['Ending_SoC'] - df_tmp1['Starting_SoC']
                # Make a Trip only if the car battery has run low between 2 consecutive charges
                if SoCDiff>0:
                    battCons = SoCDiff * df_tmp0['Battery_Capacity(kWh)']
                    kmDriven = round((battCons * 100)/df_tmp0['Mean_Energy_Consumption(kWh/100km)'],2)
                    if ((df_new.loc[index, 'Day_of_Week'] != 6) & (df_new.loc[index, 'Day_of_Week'] != 7)):
                        df_vel_samples = df_vel.sample(n=1, replace=True, weights='Weights').reset_index(drop=True)
                    else:
                        df_vel_samples = df_vel_Wend.sample(n=1, replace=True, weights='Weights').reset_index(drop=True)
                    velocity = df_vel_samples['Values'].values[0]
                    tripTime = round(kmDriven/velocity,2)
                    availCells = idx1 - idx0 -1
                    floorHours = math.floor(tripTime)
                    hour = 60
                    minutes = round((tripTime * hour) % hour)
                    idxEnd = idx1 - 1

                    if (availCells < math.ceil(tripTime)):
                        idxStart = idx1 - availCells
                        desiredVel = math.ceil(kmDriven/(availCells))
                        # Try to take another sample from the list, otherwise set velocity equal to the desired
                        try:
                            if ((df_new.loc[index, 'Day_of_Week'] != 6) & (df_new.loc[index, 'Day_of_Week'] != 7)):
                                df_vel_samples = df_vel[df_vel['Values'] > desiredVel].sample(n=1, replace=True,
                                                                                              weights='Weights').reset_index(drop=True)
                                velocity = df_vel_samples['Values'].values[0]
                            else:
                                df_vel_samples = df_vel_Wend[df_vel_Wend['Values'] > desiredVel].sample(n=1, replace=True,
                                                                                              weights='Weights').reset_index(drop=True)
                                velocity = df_vel_samples['Values'].values[0]
                        except ValueError:
                            velocity = desiredVel
                    else:
                        idxStart = idx1 - floorHours

                    if tripTime < 1:
                        df_new.at[idxEnd, 'Status'] = 2
                        df_new.at[idxEnd, 'Trip_Time(mins)'] = minutes
                        df_new.loc[idxEnd, 'Trip_Distance(km)'] = round((velocity * minutes)/60,2)
                        df_new.loc[idxEnd, 'Trip_Consumption(kwh)'] = round((df_new.loc[idxEnd, 'Trip_Distance(km)'] *
                                                                         df_tmp0['Mean_Energy_Consumption(kWh/100km)'])/100,2)
                        df_new.loc[idxEnd, 'Starting_SoC'] = df_tmp0['Ending_SoC']
                        df_new.loc[idxEnd, 'Ending_SoC'] = df_tmp1['Starting_SoC']
                    else:
                        df_new.at[idxStart:idxEnd, 'Status'] = 2
                        df_new.at[idxStart:idxEnd, 'Trip_Time(mins)'] = hour
                        df_new.at[idxEnd, 'Trip_Time(mins)'] = minutes
                        df_new.loc[idxStart:idxEnd, 'Trip_Distance(km)'] = velocity
                        df_new.loc[idxEnd, 'Trip_Distance(km)'] = round((velocity * minutes) / 60,2)
                        df_new.loc[idxStart:idxEnd, 'Trip_Consumption(kwh)'] = round((velocity * df_tmp0['Mean_Energy_Consumption(kWh/100km)'])/100,2)
                        df_new.loc[idxEnd, 'Trip_Consumption(kwh)'] = round((df_new.loc[idxEnd, 'Trip_Distance(km)'] *
                                                                         df_tmp0['Mean_Energy_Consumption(kWh/100km)'])/100)
                        startSOC = df_tmp0['Ending_SoC']
                        stepSoc = SoCDiff / tripTime
                        for j in range(idxStart, idxEnd + 1):
                            df_new.loc[j, 'Starting_SoC'] = startSOC
                            df_new.loc[j, 'Ending_SoC'] = round(startSOC - stepSoc, 2)
                            startSOC = df_new.loc[j, 'Ending_SoC']
                        df_new.loc[idxEnd, 'Ending_SoC'] = df_tmp1['Starting_SoC']

                    idx0 = index
                    df_tmp0 = df_new.loc[index]
                    if pd.isna(df_new.loc[idx0+1, 'Starting_SoC']):
                        flag = 1
                    else:
                        flag = 0
        df_new.loc[df_new['Status'].isnull(), 'Status'] = 0
        # Save the .csv to the appropriate path
        filename = "%s%s%s%s" % (pathDriversData, strName1, mycsv, strName2)
        df_new.to_csv(filename, index=False)

    # Merge all files into one
    if (mode=="Strict"):
        merged_files = os.path.join(pathDriversData, "GeneratedData_DriverBehavior_StrictChecks_*.csv")
        filename_merged = "%s%s" % (pathDriverBeh, "/GeneratedData_DriverBehavior_StrictChecks.csv")
    elif (mode=="Looser"):
        merged_files = os.path.join(pathDriversData, "GeneratedData_DriverBehavior_LooserChecks_*.csv")
        filename_merged = "%s%s" % (pathDriverBeh, "/GeneratedData_DriverBehavior_LooserChecks.csv")
    else:
        merged_files = os.path.join(pathDriversData, "GeneratedData_DriverBehavior_MinChecks_*.csv")
        filename_merged = "%s%s" % (pathDriverBeh, "/GeneratedData_DriverBehavior_MinChecks.csv")

    merged_list = glob.glob(merged_files)
    df_merged = pd.concat(map(pd.read_csv, merged_list), ignore_index=True)
    df_merged.to_csv(filename_merged, index=False)

    ############### FrequencyTables for Comparison ####################
    import FrequencyTables_GeneratedData_Creation as freqTab
    freqTab.FrequencyTables_GeneratedData(df_merged, jsonData, pathDriverBeh)
    ######################### Plots ###################################
    # import PlotsMetrics_DriverBehaviorData as plotDrivBeh
    # plotDrivBeh.Plot_DrivBeh_BarPlots(jsonData, pathDriverBeh)
    # plotDrivBeh.Plot_DrivBeh_TimeSeries(jsonData, pathDriverBeh)