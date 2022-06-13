import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import sys
import glob
import os
import json

def Difference_Calculation (df_1,df_2):
    dictOri = dict(zip(df_1['Values'], df_1['Weights']))
    keyList = df_1['Values'].tolist()
    dictGen = {key: 0 for key in keyList}
    for index, row in df_1.iterrows():
        df1Value = df_1.loc[index,'Values']
        if df_2['Values'].isin([df1Value]).any():
            tmp = df_2[df_2['Values'] == df_1.loc[index,'Values']]
            dictGen[df1Value] = tmp['Weights'].values[0]
    dictSub = {key: dictOri[key] - dictGen.get(key, 0) for key in dictOri.keys()}
    sub = list(map(abs, dictSub.values()))
    # print(sub)
    sumSub = sum(sub)
    return sub, sumSub

def Plot_DrivBeh_BarPlots (jsonData, pathDriverBeh, folderToSave=None):
    mode = jsonData['checksMode']
    if mode == "Strict":
        df = pd.DataFrame(index=np.arange(1), columns=['Mode', 'DailyCharges', 'ChargeStartHour', 'Starting_SoC',
                                                       'Ending_SoC', 'DailyTrips', 'TripStartHour', 'Average_Diff'])
        df.loc[0, 'Mode'] = 'StrictChecks'
    elif mode == "Looser":
        df = pd.DataFrame(index=np.arange(1), columns=['Mode', 'DailyCharges', 'ChargeStartHour', 'Starting_SoC',
                                                       'Ending_SoC', 'DailyTrips', 'TripStartHour', 'Average_Diff'])
        df.loc[0, 'Mode'] = 'LooserChecks'
    elif mode == "Min":
        df = pd.DataFrame(index=np.arange(1), columns=['Mode', 'DailyCharges', 'ChargeStartHour', 'Starting_SoC',
                                                       'Ending_SoC', 'DailyTrips', 'TripStartHour', 'Average_Diff'])
        df.loc[2, 'Mode'] = 'MinChecks'
    elif mode == "ALL":
        df = pd.DataFrame(index=np.arange(3), columns=['Mode', 'DailyCharges', 'ChargeStartHour', 'Starting_SoC',
                                                       'Ending_SoC', 'DailyTrips', 'TripStartHour', 'Average_Diff'])
        df.loc[0, 'Mode'] = 'StrictChecks'
        df.loc[1, 'Mode'] = 'LooserChecks'
        df.loc[2, 'Mode'] = 'MinChecks'
    else:
        print("\nERROR: Wrong configuration for variable 'checksMode'\nCheck .json file")
        sys.exit()

    if (folderToSave == None):
        figuresFolder = pathDriverBeh + '/' + jsonData['pathFigures']
    else:
        figuresFolder = folderToSave + '/' + jsonData['pathGeneratedDriversData'] + '/' + jsonData['pathFigures']
    # Create the appropriate directory if doesn't exist
    isExist = os.path.exists(figuresFolder)
    if not isExist:
        os.makedirs(figuresFolder)

    totalDiff1 = 0
    totalDiff2 = 0
    totalDiff3 = 0
    path = pathDriverBeh+'/'+jsonData['pathFreqTableComparison']
    ############################################################
    ####################  DailyCharges   #######################
    ############################################################
    fileName1 = path+'/'+jsonData['pathFreqTableCompDailyChargeOrig']
    df1 = pd.read_csv(fileName1)
    df1["Category"] = "Original Data"
    if mode == "Strict":
        fileName2 = path + '/' + jsonData['pathFreqTableCompDailyChargeStrict']
        df2 = pd.read_csv(fileName2)
        df2["Category"] = "Generated Data-StrictChecks"
        df_concat = pd.concat([df1, df2], axis=0).reset_index()
        diff1, sumDiff1 = Difference_Calculation(df1, df2)
        totalDiff1 = totalDiff1 + sumDiff1
        df.loc[0, 'DailyCharges'] = round(sumDiff1, 3)
        strName1 = '/DriversBehavior_DailyCharges-StrictChecks.png'
    elif mode == "Looser":
        fileName3 = path + '/' + jsonData['pathFreqTableCompDailyChargeLooser']
        df3 = pd.read_csv(fileName3)
        df3["Category"] = "Generated Data-LooserChecks"
        df_concat = pd.concat([df1, df3], axis=0).reset_index()
        diff2, sumDiff2 = Difference_Calculation(df1, df3)
        totalDiff2 = totalDiff2 + sumDiff2
        df.loc[0, 'DailyCharges'] = round(sumDiff2, 3)
        strName1 = '/DriversBehavior_DailyCharges-LooserChecks.png'
    elif mode == "Min":
        fileName4 = path + '/' + jsonData['pathFreqTableCompDailyChargeMin']
        df4 = pd.read_csv(fileName4)
        df4["Category"] = "Generated Data-MinChecks"
        df_concat = pd.concat([df1, df4], axis=0).reset_index()
        diff3, sumDiff3 = Difference_Calculation(df1, df4)
        totalDiff3 = totalDiff3 + sumDiff3
        df.loc[0, 'DailyCharges'] = round(sumDiff3, 3)
        strName1 = '/DriversBehavior_DailyCharges-MinChecks.png'
    else:
        fileName2 = path + '/' + jsonData['pathFreqTableCompDailyChargeStrict']
        fileName3 = path + '/' + jsonData['pathFreqTableCompDailyChargeLooser']
        fileName4 = path + '/' + jsonData['pathFreqTableCompDailyChargeMin']
        df2 = pd.read_csv(fileName2)
        df3 = pd.read_csv(fileName3)
        df4 = pd.read_csv(fileName4)
        df2["Category"] = "Generated Data-StrictChecks"
        df3["Category"] = "Generated Data-LooserChecks"
        df4["Category"] = "Generated Data-MinChecks"
        df_concat = pd.concat([df1, df2, df3, df4], axis=0).reset_index()
        diff1, sumDiff1 = Difference_Calculation(df1, df2)
        diff2, sumDiff2 = Difference_Calculation(df1, df3)
        diff3, sumDiff3 = Difference_Calculation(df1, df4)
        totalDiff1 = totalDiff1 + sumDiff1
        totalDiff2 = totalDiff2 + sumDiff2
        totalDiff3 = totalDiff3 + sumDiff3
        df.loc[0, 'DailyCharges'] = round(sumDiff1, 3)
        df.loc[1, 'DailyCharges'] = round(sumDiff2, 3)
        df.loc[2, 'DailyCharges'] = round(sumDiff3, 3)
        strName1 = '/DriversBehavior_DailyCharges-ALL.png'
    # Save figure to the appropriate path
    figName = "%s%s" % (figuresFolder, strName1)
    sns.set(style="darkgrid")
    plt.figure(figsize=(10, 7))
    sns.barplot(data=df_concat, x="Values", y="Weights", hue="Category")
    plt.legend(loc='upper right', prop={"size": 17})
    plt.xlabel("Number of Daily Charges", fontsize=21)
    plt.ylabel("Relative Frequency Distribution", fontsize=21)
    plt.savefig(figName, bbox_inches='tight', dpi=300)
    # plt.savefig(figName, bbox_inches='tight',dpi=300)

    ############################################################
    ##################  ChargeStartHour   ######################
    ############################################################
    fileName1 = path+'/'+jsonData['pathFreqTableCompChargeStartHourOrig']
    df1 = pd.read_csv(fileName1)
    df1["Category"] = "Original Data"
    if mode == "Strict":
        fileName2 = path + '/' + jsonData['pathFreqTableCompChargeStartHourStrict']
        df2 = pd.read_csv(fileName2)
        df2["Category"] = "Generated Data-StrictChecks"
        df_concat = pd.concat([df1, df2], axis=0).reset_index()
        diff1, sumDiff1 = Difference_Calculation(df1, df2)
        totalDiff1 = totalDiff1 + sumDiff1
        df.loc[0, 'ChargeStartHour'] = round(sumDiff1, 3)
        strName1 = '/DriversBehavior_ChargeStartHour-StrictChecks.png'
    elif mode == "Looser":
        fileName3 = path + '/' + jsonData['pathFreqTableCompChargeStartHourLooser']
        df3 = pd.read_csv(fileName3)
        df3["Category"] = "Generated Data-LooserChecks"
        df_concat = pd.concat([df1, df3], axis=0).reset_index()
        diff2, sumDiff2 = Difference_Calculation(df1, df3)
        totalDiff2 = totalDiff2 + sumDiff2
        df.loc[0, 'ChargeStartHour'] = round(sumDiff2, 3)
        strName1 = '/DriversBehavior_ChargeStartHour-LooserChecks.png'
    elif mode == "Min":
        fileName4 = path + '/' + jsonData['pathFreqTableCompChargeStartHourMin']
        df4 = pd.read_csv(fileName4)
        df4["Category"] = "Generated Data-MinChecks"
        df_concat = pd.concat([df1, df4], axis=0).reset_index()
        diff3, sumDiff3 = Difference_Calculation(df1, df4)
        totalDiff3 = totalDiff3 + sumDiff3
        df.loc[0, 'ChargeStartHour'] = round(sumDiff3, 3)
        strName1 = '/DriversBehavior_ChargeStartHour-MinChecks.png'
    else:
        fileName2 = path + '/' + jsonData['pathFreqTableCompChargeStartHourStrict']
        fileName3 = path + '/' + jsonData['pathFreqTableCompChargeStartHourLooser']
        fileName4 = path + '/' + jsonData['pathFreqTableCompChargeStartHourMin']
        df2 = pd.read_csv(fileName2)
        df3 = pd.read_csv(fileName3)
        df4 = pd.read_csv(fileName4)
        df2["Category"] = "Generated Data-StrictChecks"
        df3["Category"] = "Generated Data-LooserChecks"
        df4["Category"] = "Generated Data-MinChecks"
        df_concat = pd.concat([df1, df2, df3, df4], axis=0).reset_index()
        diff1, sumDiff1 = Difference_Calculation(df1, df2)
        diff2, sumDiff2 = Difference_Calculation(df1, df3)
        diff3, sumDiff3 = Difference_Calculation(df1, df4)
        totalDiff1 = totalDiff1 + sumDiff1
        totalDiff2 = totalDiff2 + sumDiff2
        totalDiff3 = totalDiff3 + sumDiff3
        df.loc[0, 'ChargeStartHour'] = round(sumDiff1, 3)
        df.loc[1, 'ChargeStartHour'] = round(sumDiff2, 3)
        df.loc[2, 'ChargeStartHour'] = round(sumDiff3, 3)
        strName1 = '/DriversBehavior_ChargeStartHour-ALL.png'
    # Save figure to the appropriate path
    figName = "%s%s" % (figuresFolder, strName1)
    sns.set(style="darkgrid")
    plt.figure(figsize=(10, 7))
    sns.barplot(data=df_concat, x="Values", y="Weights", hue="Category")
    plt.legend(loc='upper left', prop={"size": 17})
    plt.xlabel("Charging Start Hour", fontsize=21)
    plt.ylabel("Relative Frequency Distribution", fontsize=21)
    plt.savefig(figName, bbox_inches='tight', dpi=300)
    # plt.savefig(figName, bbox_inches='tight',dpi=300)

    ############################################################
    ####################  Starting_SoC   #######################
    ############################################################
    fileName1 = path+'/'+jsonData['pathFreqTableCompStartingSoCOrig']
    df1 = pd.read_csv(fileName1)
    df1["Category"] = "Original Data"
    if mode == "Strict":
        fileName2 = path + '/' + jsonData['pathFreqTableCompStartingSoCStrict']
        df2 = pd.read_csv(fileName2)
        df2["Category"] = "Generated Data-StrictChecks"
        df_concat = pd.concat([df1, df2], axis=0).reset_index()
        diff1, sumDiff1 = Difference_Calculation(df1, df2)
        totalDiff1 = totalDiff1 + sumDiff1
        df.loc[0, 'Starting_SoC'] = round(sumDiff1, 3)
        strName1 = '/DriversBehavior_Starting_SoC-StrictChecks.png'
    elif mode == "Looser":
        fileName3 = path + '/' + jsonData['pathFreqTableCompStartingSoCLooser']
        df3 = pd.read_csv(fileName3)
        df3["Category"] = "Generated Data-LooserChecks"
        df_concat = pd.concat([df1, df3], axis=0).reset_index()
        diff2, sumDiff2 = Difference_Calculation(df1, df3)
        totalDiff2 = totalDiff2 + sumDiff2
        df.loc[0, 'Starting_SoC'] = round(sumDiff2, 3)
        strName1 = '/DriversBehavior_Starting_SoC-LooserChecks.png'
    elif mode == "Min":
        fileName4 = path + '/' + jsonData['pathFreqTableCompStartingSoCMin']
        df4 = pd.read_csv(fileName4)
        df4["Category"] = "Generated Data-MinChecks"
        df_concat = pd.concat([df1, df4], axis=0).reset_index()
        diff3, sumDiff3 = Difference_Calculation(df1, df4)
        totalDiff3 = totalDiff3 + sumDiff3
        df.loc[0, 'Starting_SoC'] = round(sumDiff3, 3)
        strName1 = '/DriversBehavior_Starting_SoC-MinChecks.png'
    else:
        fileName2 = path + '/' + jsonData['pathFreqTableCompStartingSoCStrict']
        fileName3 = path + '/' + jsonData['pathFreqTableCompStartingSoCLooser']
        fileName4 = path + '/' + jsonData['pathFreqTableCompStartingSoCMin']
        df2 = pd.read_csv(fileName2)
        df3 = pd.read_csv(fileName3)
        df4 = pd.read_csv(fileName4)
        df1["Category"] = "Original Data"
        df2["Category"] = "Generated Data-StrictChecks"
        df3["Category"] = "Generated Data-LooserChecks"
        df_concat = pd.concat([df1, df2, df3, df4], axis=0).reset_index()
        diff1, sumDiff1 = Difference_Calculation(df1, df2)
        diff2, sumDiff2 = Difference_Calculation(df1, df3)
        diff3, sumDiff3 = Difference_Calculation(df1, df4)
        totalDiff1 = totalDiff1 + sumDiff1
        totalDiff2 = totalDiff2 + sumDiff2
        totalDiff3 = totalDiff3 + sumDiff3
        df.loc[0, 'Starting_SoC'] = round(sumDiff1, 3)
        df.loc[1, 'Starting_SoC'] = round(sumDiff2, 3)
        df.loc[2, 'Starting_SoC'] = round(sumDiff3, 3)
        strName1 = '/DriversBehavior_Starting_SoC-ALL.png'
    # Save figure to the appropriate path
    figName = "%s%s" % (figuresFolder, strName1)
    sns.set(style="darkgrid")
    plt.figure(figsize=(10, 7))
    sns.barplot(data=df_concat, x="Values", y="Weights", hue="Category")
    plt.legend(loc='upper left', prop={"size": 17})
    plt.xlabel("Starting SoC", fontsize=21)
    plt.ylabel("Relative Frequency Distribution", fontsize=21)
    plt.savefig(figName, bbox_inches='tight', dpi=300)
    # plt.savefig(figName, bbox_inches='tight',dpi=300)

    ############################################################
    ######################  Ending_SoC   #######################
    ############################################################
    fileName1 = path+'/'+jsonData['pathFreqTableCompEndingSoCOrig']
    df1 = pd.read_csv(fileName1)
    df1["Category"] = "Original Data"
    if mode == "Strict":
        fileName2 = path + '/' + jsonData['pathFreqTableCompEndingSoCStrict']
        df2 = pd.read_csv(fileName2)
        df2["Category"] = "Generated Data-StrictChecks"
        df_concat = pd.concat([df1, df2], axis=0).reset_index()
        diff1, sumDiff1 = Difference_Calculation(df1, df2)
        totalDiff1 = totalDiff1 + sumDiff1
        df.loc[0, 'Ending_SoC'] = round(sumDiff1, 3)
        strName1 = '/DriversBehavior_Ending_SoC-StrictChecks.png'
    elif mode == "Looser":
        fileName3 = path + '/' + jsonData['pathFreqTableCompEndingSoCLooser']
        df3 = pd.read_csv(fileName3)
        df3["Category"] = "Generated Data-LooserChecks"
        df_concat = pd.concat([df1, df3], axis=0).reset_index()
        diff2, sumDiff2 = Difference_Calculation(df1, df3)
        totalDiff2 = totalDiff2 + sumDiff2
        df.loc[0, 'Ending_SoC'] = round(sumDiff2, 3)
        strName1 = '/DriversBehavior_Ending_SoC-LooserChecks.png'
    elif mode == "Min":
        fileName4 = path + '/' + jsonData['pathFreqTableCompEndingSoCMin']
        df4 = pd.read_csv(fileName4)
        df4["Category"] = "Generated Data-MinChecks"
        df_concat = pd.concat([df1, df4], axis=0).reset_index()
        diff3, sumDiff3 = Difference_Calculation(df1, df4)
        totalDiff3 = totalDiff3 + sumDiff3
        df.loc[0, 'Ending_SoC'] = round(sumDiff3, 3)
        strName1 = '/DriversBehavior_Ending_SoC-MinChecks.png'
    else:
        fileName2 = path + '/' + jsonData['pathFreqTableCompEndingSoCStrict']
        fileName3 = path + '/' + jsonData['pathFreqTableCompEndingSoCLooser']
        fileName4 = path + '/' + jsonData['pathFreqTableCompEndingSoCMin']
        df2 = pd.read_csv(fileName2)
        df3 = pd.read_csv(fileName3)
        df4 = pd.read_csv(fileName4)
        df2["Category"] = "Generated Data-StrictChecks"
        df3["Category"] = "Generated Data-LooserChecks"
        df4["Category"] = "Generated Data-MinChecks"
        df_concat = pd.concat([df1, df2, df3, df4], axis=0).reset_index()
        diff1, sumDiff1 = Difference_Calculation(df1, df2)
        diff2, sumDiff2 = Difference_Calculation(df1, df3)
        diff3, sumDiff3 = Difference_Calculation(df1, df4)
        totalDiff1 = totalDiff1 + sumDiff1
        totalDiff2 = totalDiff2 + sumDiff2
        totalDiff3 = totalDiff3 + sumDiff3
        df.loc[0, 'Ending_SoC'] = round(sumDiff1, 3)
        df.loc[1, 'Ending_SoC'] = round(sumDiff2, 3)
        df.loc[2, 'Ending_SoC'] = round(sumDiff3, 3)
        strName1 = '/DriversBehavior_Ending_SoC-ALL.png'
    # Save figure to the appropriate path
    figName = "%s%s" % (figuresFolder, strName1)
    sns.set(style="darkgrid")
    plt.figure(figsize=(10, 7))
    sns.barplot(data=df_concat, x="Values", y="Weights", hue="Category")
    plt.legend(loc='upper left', prop={"size": 17})
    plt.xlabel("Ending SoC", fontsize=21)
    plt.ylabel("Relative Frequency Distribution", fontsize=21)
    plt.savefig(figName, bbox_inches='tight', dpi=300)
    # plt.savefig(figName, bbox_inches='tight',dpi=300)

    ############################################################
    ######################  DailyTrips   #######################
    ############################################################
    fileName1 = path+'/'+jsonData['pathFreqTableCompDailyTripsOrig']
    df1 = pd.read_csv(fileName1)
    df1["Category"] = "Original Data"
    if mode == "Strict":
        fileName2 = path + '/' + jsonData['pathFreqTableCompDailyTripsStrict']
        df2 = pd.read_csv(fileName2)
        df2["Category"] = "Generated Data-StrictChecks"
        df_concat = pd.concat([df1, df2], axis=0).reset_index()
        diff1, sumDiff1 = Difference_Calculation(df1, df2)
        totalDiff1 = totalDiff1 + sumDiff1
        df.loc[0, 'DailyTrips'] = round(sumDiff1, 3)
        strName1 = '/DriversBehavior_DailyTrips-StrictChecks.png'
    elif mode == "Looser":
        fileName3 = path + '/' + jsonData['pathFreqTableCompDailyTripsLooser']
        df3 = pd.read_csv(fileName3)
        df3["Category"] = "Generated Data-LooserChecks"
        df_concat = pd.concat([df1, df3], axis=0).reset_index()
        diff2, sumDiff2 = Difference_Calculation(df1, df3)
        totalDiff2 = totalDiff2 + sumDiff2
        df.loc[0, 'DailyTrips'] = round(sumDiff2, 3)
        strName1 = '/DriversBehavior_DailyTrips-LooserChecks.png'
    elif mode == "Min":
        fileName4 = path + '/' + jsonData['pathFreqTableCompDailyTripsMin']
        df4 = pd.read_csv(fileName4)
        df4["Category"] = "Generated Data-MinChecks"
        df_concat = pd.concat([df1, df4], axis=0).reset_index()
        diff3, sumDiff3 = Difference_Calculation(df1, df4)
        totalDiff3 = totalDiff3 + sumDiff3
        df.loc[0, 'DailyTrips'] = round(sumDiff3, 3)
        strName1 = '/DriversBehavior_DailyTrips-MinChecks.png'
    else:
        fileName2 = path + '/' + jsonData['pathFreqTableCompDailyTripsStrict']
        fileName3 = path + '/' + jsonData['pathFreqTableCompDailyTripsLooser']
        fileName4 = path + '/' + jsonData['pathFreqTableCompDailyTripsMin']
        df2 = pd.read_csv(fileName2)
        df3 = pd.read_csv(fileName3)
        df4 = pd.read_csv(fileName4)
        df2["Category"] = "Generated Data-StrictChecks"
        df3["Category"] = "Generated Data-LooserChecks"
        df4["Category"] = "Generated Data-MinChecks"
        df_concat = pd.concat([df1, df2, df3, df4], axis=0).reset_index()
        diff1, sumDiff1 = Difference_Calculation(df1, df2)
        diff2, sumDiff2 = Difference_Calculation(df1, df3)
        diff3, sumDiff3 = Difference_Calculation(df1, df4)
        totalDiff1 = totalDiff1 + sumDiff1
        totalDiff2 = totalDiff2 + sumDiff2
        totalDiff3 = totalDiff3 + sumDiff3
        df.loc[0, 'DailyTrips'] = round(sumDiff1, 3)
        df.loc[1, 'DailyTrips'] = round(sumDiff2, 3)
        df.loc[2, 'DailyTrips'] = round(sumDiff3, 3)
        strName1 = '/DriversBehavior_DailyTrips-ALL.png'
    # Save figure to the appropriate path
    figName = "%s%s" % (figuresFolder, strName1)
    sns.set(style="darkgrid")
    plt.figure(figsize=(10, 7))
    bplot = sns.barplot(data=df_concat, x="Values", y="Weights", hue="Category")
    plt.legend(loc='upper right', prop={"size": 17})
    plt.xlabel("Number of Daily Trips", fontsize=21)
    plt.ylabel("Relative Frequency Distribution", fontsize=21)
    plt.savefig(figName, bbox_inches='tight', dpi=300)
    # plt.savefig(figName, bbox_inches='tight',dpi=300)

    ############################################################
    #####################  TripStartHour   #####################
    ############################################################
    fileName1 = path+'/'+jsonData['pathFreqTableCompTripStartHourOrig']
    df1 = pd.read_csv(fileName1)
    df1["Category"] = "Original Data"
    if mode == "Strict":
        fileName2 = path + '/' + jsonData['pathFreqTableCompTripStartHourStrict']
        df2 = pd.read_csv(fileName2)
        df2["Category"] = "Generated Data-StrictChecks"
        df_concat = pd.concat([df1, df2], axis=0).reset_index()
        diff1, sumDiff1 = Difference_Calculation(df1, df2)
        totalDiff1 = totalDiff1 + sumDiff1
        df.loc[0, 'TripStartHour'] = round(sumDiff1, 3)
        strName1 = '/DriversBehavior_TripStartHour-StrictChecks.png'
    elif mode == "Looser":
        fileName3 = path + '/' + jsonData['pathFreqTableCompTripStartHourLooser']
        df3 = pd.read_csv(fileName3)
        df3["Category"] = "Generated Data-LooserChecks"
        df_concat = pd.concat([df1, df3], axis=0).reset_index()
        diff2, sumDiff2 = Difference_Calculation(df1, df3)
        totalDiff2 = totalDiff2 + sumDiff2
        df.loc[0, 'TripStartHour'] = round(sumDiff2, 3)
        strName1 = '/DriversBehavior_TripStartHour-LooserChecks.png'
    elif mode == "Min":
        fileName4 = path + '/' + jsonData['pathFreqTableCompTripStartHourMin']
        df4 = pd.read_csv(fileName4)
        df4["Category"] = "Generated Data-MinChecks"
        df_concat = pd.concat([df1, df4], axis=0).reset_index()
        diff3, sumDiff3 = Difference_Calculation(df1, df4)
        totalDiff3 = totalDiff3 + sumDiff3
        df.loc[0, 'TripStartHour'] = round(sumDiff3, 3)
        strName1 = '/DriversBehavior_TripStartHour-MinChecks.png'
    else:
        fileName2 = path + '/' + jsonData['pathFreqTableCompTripStartHourStrict']
        fileName3 = path + '/' + jsonData['pathFreqTableCompTripStartHourLooser']
        fileName4 = path + '/' + jsonData['pathFreqTableCompTripStartHourMin']
        df2 = pd.read_csv(fileName2)
        df3 = pd.read_csv(fileName3)
        df4 = pd.read_csv(fileName4)
        df2["Category"] = "Generated Data-StrictChecks"
        df3["Category"] = "Generated Data-LooserChecks"
        df4["Category"] = "Generated Data-MinChecks"
        df_concat = pd.concat([df1, df2, df3, df4], axis=0).reset_index()
        diff1, sumDiff1 = Difference_Calculation(df1, df2)
        diff2, sumDiff2 = Difference_Calculation(df1, df3)
        diff3, sumDiff3 = Difference_Calculation(df1, df4)
        totalDiff1 = totalDiff1 + sumDiff1
        totalDiff2 = totalDiff2 + sumDiff2
        totalDiff3 = totalDiff3 + sumDiff3
        df.loc[0, 'TripStartHour'] = round(sumDiff1, 3)
        df.loc[1, 'TripStartHour'] = round(sumDiff2, 3)
        df.loc[2, 'TripStartHour'] = round(sumDiff3, 3)
        strName1 = '/DriversBehavior_TripStartHour-ALL.png'
    # Save figure to the appropriate path
    figName = "%s%s" % (figuresFolder, strName1)
    sns.set(style="darkgrid")
    plt.figure(figsize=(10, 7))
    bplot = sns.barplot(data=df_concat, x="Values", y="Weights", hue="Category")
    plt.legend(loc='upper left', prop={"size": 17})
    plt.xlabel("Trip Start Hour", fontsize=21)
    plt.ylabel("Relative Frequency Distribution", fontsize=21)
    plt.savefig(figName, bbox_inches='tight', dpi=300)
    # plt.savefig(figName, bbox_inches='tight',dpi=300)

    ############################################################
    if mode == "Strict":
        df.loc[0, 'Average_Diff'] = round(totalDiff1 / 6, 3)
        strName1 = '/Metrics-DriversBehavior-StrictChecks.csv'
    elif mode == "Looser":
        df.loc[0, 'Average_Diff'] = round(totalDiff2 / 6, 3)
        strName1 = '/Metrics-DriversBehavior-LooserChecks.csv'
    elif mode == "Min":
        df.loc[0, 'Average_Diff'] = round(totalDiff3 / 6, 3)
        strName1 = '/Metrics-DriversBehavior-MinChecks.csv'
    else:
        df.loc[0, 'Average_Diff'] = round(totalDiff1 / 6, 3)
        df.loc[1, 'Average_Diff'] = round(totalDiff2 / 6, 3)
        df.loc[2, 'Average_Diff'] = round(totalDiff3 / 6, 3)
        strName1 = '/Metrics-DriversBehavior-ALL.csv'

    # Save metrics-file to the appropriate directory
    if (folderToSave == None):
        figName = pathDriverBeh + strName1
    else:
        figName = folderToSave + '/' + jsonData['pathGeneratedDriversData'] + strName1
    df.to_csv(figName, index=False)

def Plot_DrivBeh_TimeSeries (jsonData, pathDriverBeh, folderToSave=None):
    if (folderToSave == None):
        figuresFolder = pathDriverBeh + '/' + jsonData['pathFigures']
    else:
        figuresFolder = folderToSave + '/' + jsonData['pathGeneratedDriversData'] + '/' + jsonData['pathFigures']
    # Create the appropriate directory if doesn't exist
    isExist = os.path.exists(figuresFolder)
    if not isExist:
        os.makedirs(figuresFolder)

    folder_path = pathDriverBeh + '/' + jsonData['pathDriversData']
    # Checking if the list is empty or not
    dir = os.listdir(folder_path)
    if len(dir) == 0:
        print("\nERROR: Directory", folder_path,"is empty")
        sys.exit()
    file_list = glob.glob(folder_path + "/*.csv")
    for i in range(1, len(file_list)):
        df_gen = pd.read_csv(file_list[i])
        if i == 1:
            df_Cons = pd.DataFrame(index=np.arange(len(df_gen)),
                                   columns=['Date', 'Year', 'Month_of_Year', 'Day_of_Week', 'Time_of_Day',
                                            'Charging_Consumption(kWh)', 'Trip_Consumption(kWh)'])
            df_Cons['Date'] = df_gen['Date']
            df_Cons['Year'] = df_gen['Year']
            df_Cons['Month_of_Year'] = df_gen['Month_of_Year']
            df_Cons['Day_of_Week'] = df_gen['Day_of_Week']
            df_Cons['Time_of_Day'] = df_gen['Time_of_Day']
            df_Cons['Charging_Consumption(kWh)'] = df_Cons['Charging_Consumption(kWh)'].fillna(0)
            df_Cons['Trip_Consumption(kWh)'] = df_Cons['Trip_Consumption(kWh)'].fillna(0)
        sum_charge = df_Cons['Charging_Consumption(kWh)'] + df_gen['Consumption_Charging(kW)'].fillna(0)
        sum_trip = df_Cons['Trip_Consumption(kWh)'] + df_gen['Trip_Consumption(kwh)'].fillna(0)
        df_Cons['Charging_Consumption(kWh)'] = round(sum_charge, 2)
        df_Cons['Trip_Consumption(kWh)'] = round(sum_trip, 2)
    mask1 = (df_Cons['Day_of_Week'] == 1) & (df_Cons['Time_of_Day'] == 1)
    df_timeSeries1 = df_Cons.loc[mask1].reset_index(drop=True)
    df_timeSeries1 = df_timeSeries1.iloc[:-2]
    date1 = df_timeSeries1["Date"].sample(n=1)
    idx = date1.index.values.astype(int)[0]
    date2 = df_timeSeries1.loc[idx + 1, "Date"]
    date1 = date1.values[0]
    mask = (df_Cons['Date'] >= date1) & (df_Cons['Date'] < date2)
    df_timeSeries = df_Cons.loc[mask]

    mode = jsonData['checksMode']
    if mode == "Strict":
        strName1 = '/EVsConsumptions-StrictChecks.png'
        plt.figure(figsize=(11, 5))
        x_ticks = np.arange(1, 7, 1)
        plt.xticks(x_ticks)
        fig = df_timeSeries['Charging_Consumption(kWh)'].plot(label='Charging Consumption')
        fig2 = df_timeSeries['Trip_Consumption(kWh)'].plot(label='Trip Consumption')
        fig.set_title("Consumptions of EVs - StrictChecks")
        fig.set_ylabel('Energy Consumption (kWh)', fontsize=18)
        fig.set_xlabel('Days of Week', fontsize=18)
        fig.legend(prop={"size": 17})
        # Save figure to the appropriate path
        figName = "%s%s" % (figuresFolder, strName1)
        plt.savefig(figName, bbox_inches='tight', dpi=300)
        # plt.savefig(figName, bbox_inches='tight',dpi=300)
    elif mode == "Looser":
        strName1 = '/EVsConsumptions-LooserChecks.png'
        plt.figure(figsize=(11, 5))
        x_ticks = np.arange(1, 7, 1)
        plt.xticks(x_ticks)
        fig = df_timeSeries['Charging_Consumption(kWh)'].plot(label='Charging Consumption')
        fig2 = df_timeSeries['Trip_Consumption(kWh)'].plot(label='Trip Consumption')
        fig.set_title("Consumptions of EVs - LooserChecks")
        fig.set_ylabel('Energy Consumption (kWh)', fontsize=18)
        fig.set_xlabel('Days of Week', fontsize=18)
        fig.legend(prop={"size": 17})
        # Save figure to the appropriate path
        figName = "%s%s" % (figuresFolder, strName1)
        plt.savefig(figName, bbox_inches='tight', dpi=300)
        # plt.savefig(figName, bbox_inches='tight',dpi=300)
    elif mode == "Min":
        strName1 = '/EVsConsumptions-MinChecks.png'
        plt.figure(figsize=(11, 5))
        x_ticks = np.arange(1, 7, 1)
        plt.xticks(x_ticks)
        fig = df_timeSeries['Charging_Consumption(kWh)'].plot(label='Charging Consumption')
        fig2 = df_timeSeries['Trip_Consumption(kWh)'].plot(label='Trip Consumption')
        fig.set_title("Consumptions of EVs - MinChecks")
        fig.set_ylabel('Energy Consumption (kWh)', fontsize=18)
        fig.set_xlabel('Days of Week', fontsize=18)
        fig.legend(prop={"size": 17})
        # Save figure to the appropriate path
        figName = "%s%s" % (figuresFolder, strName1)
        plt.savefig(figName, bbox_inches='tight', dpi=300)
        # plt.savefig(figName, bbox_inches='tight',dpi=300)
    elif mode == "ALL":
        # strName1 = '/EVsConsumptions-StrictChecks.png'
        # folder_path = jdata['pathGeneratedStrict']
        # # Checking if the list is empty or not
        # dir = os.listdir(folder_path)
        # if len(dir) == 0:
        #     print("\nERROR: Directory", folder_path,"is empty")
        #     sys.exit()
        # file_list = glob.glob(folder_path + "/*.csv")
        # for i in range(1, len(file_list)):
        #     df_gen = pd.read_csv(file_list[i])
        #     if i == 1:
        #         df_Cons = pd.DataFrame(index=np.arange(len(df_gen)),
        #                                columns=['Date', 'Year', 'Month_of_Year', 'Day_of_Week', 'Time_of_Day',
        #                                         'Charging_Consumption(kWh)', 'Trip_Consumption(kWh)'])
        #         df_Cons['Date'] = df_gen['Date']
        #         df_Cons['Year'] = df_gen['Year']
        #         df_Cons['Month_of_Year'] = df_gen['Month_of_Year']
        #         df_Cons['Day_of_Week'] = df_gen['Day_of_Week']
        #         df_Cons['Time_of_Day'] = df_gen['Time_of_Day']
        #         df_Cons['Charging_Consumption(kWh)'] = df_Cons['Charging_Consumption(kWh)'].fillna(0)
        #         df_Cons['Trip_Consumption(kWh)'] = df_Cons['Trip_Consumption(kWh)'].fillna(0)
        #     sum_charge = df_Cons['Charging_Consumption(kWh)'] + df_gen['Consumption_Charging(kW)'].fillna(0)
        #     sum_trip = df_Cons['Trip_Consumption(kWh)'] + df_gen['Trip_Consumption(kwh)'].fillna(0)
        #     df_Cons['Charging_Consumption(kWh)'] = round(sum_charge, 2)
        #     df_Cons['Trip_Consumption(kWh)'] = round(sum_trip, 2)
        #
        # mask1 = (df_Cons['Day_of_Week'] == 1) & (df_Cons['Time_of_Day'] == 1)
        # df_timeSeries1 = df_Cons.loc[mask1].reset_index(drop=True)
        # df_timeSeries1 = df_timeSeries1.iloc[:-2]
        # date1 = df_timeSeries1["Date"].sample(n=1)
        # idx = date1.index.values.astype(int)[0]
        # date2 = df_timeSeries1.loc[idx + 1, "Date"]
        # date1 = date1.values[0]
        # mask = (df_Cons['Date'] >= date1) & (df_Cons['Date'] < date2)
        # df_timeSeries = df_Cons.loc[mask]
        #
        # plt.figure(figsize=(11, 5))
        # x_ticks = np.arange(1, 7, 1)
        # plt.xticks(x_ticks)
        # fig = df_timeSeries['Charging_Consumption(kWh)'].plot(label='Charging Consumption')
        # fig2 = df_timeSeries['Trip_Consumption(kWh)'].plot(label='Trip Consumption')
        # fig.set_title("Consumptions of EVs - StrictChecks")
        # fig.set_ylabel('Energy Consumption (kWh)', fontsize=18)
        # fig.set_xlabel('Days of Week', fontsize=18)
        # fig.legend(prop={"size": 17})
        # # Save figure to the appropriate path
        # figName = "%s%s" % (strName0, strName1)
        # plt.savefig(figName, bbox_inches='tight', dpi=300)
        # # plt.savefig(figName, bbox_inches='tight',dpi=300)
        # #####################################################################################
        # strName1 = '/EVsConsumptions-LooserChecks.png'
        # folder_path = jdata['pathGeneratedLooser']
        # # Checking if the list is empty or not
        # dir = os.listdir(folder_path)
        # if len(dir) == 0:
        #     print("\nERROR: Directory", folder_path,"is empty")
        #     sys.exit()
        # file_list = glob.glob(folder_path + "/*.csv")
        # for i in range(1, len(file_list)):
        #     df_gen = pd.read_csv(file_list[i])
        #     if i == 1:
        #         df_Cons = pd.DataFrame(index=np.arange(len(df_gen)),
        #                                columns=['Date', 'Year', 'Month_of_Year', 'Day_of_Week', 'Time_of_Day',
        #                                         'Charging_Consumption(kWh)', 'Trip_Consumption(kWh)'])
        #         df_Cons['Date'] = df_gen['Date']
        #         df_Cons['Year'] = df_gen['Year']
        #         df_Cons['Month_of_Year'] = df_gen['Month_of_Year']
        #         df_Cons['Day_of_Week'] = df_gen['Day_of_Week']
        #         df_Cons['Time_of_Day'] = df_gen['Time_of_Day']
        #         df_Cons['Charging_Consumption(kWh)'] = df_Cons['Charging_Consumption(kWh)'].fillna(0)
        #         df_Cons['Trip_Consumption(kWh)'] = df_Cons['Trip_Consumption(kWh)'].fillna(0)
        #     sum_charge = df_Cons['Charging_Consumption(kWh)'] + df_gen['Consumption_Charging(kW)'].fillna(0)
        #     sum_trip = df_Cons['Trip_Consumption(kWh)'] + df_gen['Trip_Consumption(kwh)'].fillna(0)
        #     df_Cons['Charging_Consumption(kWh)'] = round(sum_charge, 2)
        #     df_Cons['Trip_Consumption(kWh)'] = round(sum_trip, 2)
        #
        # df_timeSeries = df_Cons.loc[mask]
        #
        # plt.figure(figsize=(11, 5))
        # x_ticks = np.arange(1, 7, 1)
        # plt.xticks(x_ticks)
        # fig = df_timeSeries['Charging_Consumption(kWh)'].plot(label='Charging Consumption')
        # fig2 = df_timeSeries['Trip_Consumption(kWh)'].plot(label='Trip Consumption')
        # # fig.set_title("Consumptions of EVs - LooserChecks")
        # fig.set_ylabel('Energy Consumption (kWh)', fontsize=18)
        # fig.set_xlabel('Days of Week', fontsize=18)
        # fig.legend(prop={"size": 17})
        # # Save figure to the appropriate path
        # figName = "%s%s" % (strName0, strName1)
        # plt.savefig(figName, bbox_inches='tight', dpi=300)
        # # plt.savefig(figName, bbox_inches='tight',dpi=300)
        # #####################################################################################
        # strName1 = '/EVsConsumptions-MinChecks.png'
        # folder_path = jdata['pathGeneratedMin']
        # # Checking if the list is empty or not
        # dir = os.listdir(folder_path)
        # if len(dir) == 0:
        #     print("\nERROR: Directory", folder_path,"is empty")
        #     sys.exit()
        # file_list = glob.glob(folder_path + "/*.csv")
        # for i in range(1, len(file_list)):
        #     df_gen = pd.read_csv(file_list[i])
        #     if i == 1:
        #         df_Cons = pd.DataFrame(index=np.arange(len(df_gen)),
        #                                columns=['Date', 'Year', 'Month_of_Year', 'Day_of_Week', 'Time_of_Day',
        #                                         'Charging_Consumption(kWh)', 'Trip_Consumption(kWh)'])
        #         df_Cons['Date'] = df_gen['Date']
        #         df_Cons['Year'] = df_gen['Year']
        #         df_Cons['Month_of_Year'] = df_gen['Month_of_Year']
        #         df_Cons['Day_of_Week'] = df_gen['Day_of_Week']
        #         df_Cons['Time_of_Day'] = df_gen['Time_of_Day']
        #         df_Cons['Charging_Consumption(kWh)'] = df_Cons['Charging_Consumption(kWh)'].fillna(0)
        #         df_Cons['Trip_Consumption(kWh)'] = df_Cons['Trip_Consumption(kWh)'].fillna(0)
        #     sum_charge = df_Cons['Charging_Consumption(kWh)'] + df_gen['Consumption_Charging(kW)'].fillna(0)
        #     sum_trip = df_Cons['Trip_Consumption(kWh)'] + df_gen['Trip_Consumption(kwh)'].fillna(0)
        #     df_Cons['Charging_Consumption(kWh)'] = round(sum_charge, 2)
        #     df_Cons['Trip_Consumption(kWh)'] = round(sum_trip, 2)
        #
        # df_timeSeries = df_Cons.loc[mask]
        #
        # plt.figure(figsize=(11, 5))
        # x_ticks = np.arange(1, 7, 1)
        # plt.xticks(x_ticks)
        # fig = df_timeSeries['Charging_Consumption(kWh)'].plot(label='Charging Consumption')
        # fig2 = df_timeSeries['Trip_Consumption(kWh)'].plot(label='Trip Consumption')
        # fig.set_title("Consumptions of EVs - StrictChecks")
        # fig.set_ylabel('Energy Consumption (kWh)', fontsize=18)
        # fig.set_xlabel('Days of Week', fontsize=18)
        # fig.legend(prop={"size": 17})
        # # Save figure to the appropriate path
        # figName = "%s%s" % (strName0, strName1)
        # plt.savefig(figName, bbox_inches='tight', dpi=300)
        # # plt.savefig(figName, bbox_inches='tight',dpi=300)
        print("mporei kai oxi")
    else:
        print("\nERROR: Wrong configuration for variable 'checksMode'\nCheck .json file")
        sys.exit()


