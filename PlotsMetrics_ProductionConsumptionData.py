import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import ks_2samp
import random
import sys
import os
import json
import time

def Plot_ProdCons_Histograms (jsonData, pathProdCons, folderToSave=None):
    method = jsonData['method']
    df = pd.DataFrame(columns=['Method', 'Lignite_Gen', 'FossilGas_Gen', 'Solar_Gen', 'Wind_Gen', 'Total_Load'])
    if method == "KDE":
        df['Method'] = ['KDE']
        fileName = pathProdCons + '/GeneratedData_ProductionConsumption-KDE.csv'
    elif method == "HIST":
        df['Method'] = ['HIST']
        fileName = pathProdCons + '/GeneratedData_ProductionConsumption-HIST.csv'
    elif method == "TimeGAN":
        df['Method'] = ['TimeGAN']
        fileName = pathProdCons + '/GeneratedData_ProductionConsumption-TimeGAN.csv'
    elif method == "ALL":
        print("\nWARNING: Histogram plots can only be generated individually,\n for each of the methods.")
        return None
    else:
        print("\nERROR: Wrong configuration for variable 'method'\nCheck .json file")
        sys.exit()

    df_gen = pd.read_csv(fileName)
    df_orig = pd.read_csv(jsonData['pathOriginalProdCons'])

    if method == "TimeGAN":
        # Calculate the time horizon, in order to take the appropriate original data for the comparison
        startDate = pd.to_datetime(df_gen['Date']).dt.date.iloc[0]
        endDate = pd.to_datetime(df_gen['Date']).dt.date.iloc[-1]
        timeHorizon = (endDate.year - startDate.year) * 12 + (endDate.month - startDate.month)+1
        if timeHorizon == 12:
            df_orig = pd.read_csv(jsonData['pathOriginalProdCons2020'])
        elif timeHorizon == 48:
            df_orig = pd.read_csv(jsonData['pathOriginalProdCons'])
        else:
            print("\nWARNING: Histogram plots can only be generated\nfor a time horizon of 12 or 48 months.")
            return None

    if (folderToSave == None):
        figuresFolder = pathProdCons + '/' + jsonData['pathFigures']
    else:
        figuresFolder = folderToSave + '/' + jsonData['pathGeneratedProdCons'] + '/' + jsonData['pathFigures']
    # Create the appropriate directory if doesn't exist
    isExist = os.path.exists(figuresFolder)
    if not isExist:
        os.makedirs(figuresFolder)

    ############################################################
    ##################   Lignite_Gen   #########################
    ############################################################
    xtmp_data = df_orig["Lignite_Gen(MW)"]
    x1_data = df_gen["Lignite_Gen(MW)"]

    plt.figure(figsize=(10, 7))
    sns.set(style="darkgrid")
    origData = sns.histplot(df_orig, x=xtmp_data, color="green", label="Original data",stat="density")
    genData = sns.histplot(df_gen, x=x1_data, color="red", label="Generated data",stat="density")
    plt.legend(prop={"size": 17})
    plt.xlabel("Lignite_Gen(MW)", fontsize=18)
    plt.ylabel("Density", fontsize=18)
    if method == "KDE":
        strName1 = '/ProductionConsumption-Lignite-KDE.png'
    elif method == "HIST":
        strName1 = '/ProductionConsumption-Lignite-HIST.png'
        ###################
    elif method == "TimeGAN":
        strName1 = '/ProductionConsumption-Lignite-TimeGAN.png'
    # Save figure to the appropriate path
    figName = "%s%s" % (figuresFolder, strName1)
    plt.savefig(figName, bbox_inches='tight', dpi=300)
    KS_statistic, pValue = ks_2samp(xtmp_data, x1_data)
    df['Lignite_Gen'] = [round(KS_statistic, 3)]
    ############################################################
    ##################   FossilGas_Gen   #########################
    ############################################################
    xtmp_data = df_orig["FossilGas_Gen(MW)"]
    x1_data = df_gen["FossilGas_Gen(MW)"]

    plt.figure(figsize=(10, 7))
    sns.set(style="darkgrid")
    origData = sns.histplot(df_orig, x=xtmp_data, color="green", label="Original data",stat="density")
    genData = sns.histplot(df_gen, x=x1_data, color="red", label="Generated data",stat="density")
    plt.legend(prop={"size": 17})
    plt.xlabel("FossilGas_Gen(MW)", fontsize=18)
    plt.ylabel("Density", fontsize=18)
    if method == "KDE":
        strName1 = '/ProductionConsumption-FossilGas-KDE.png'
    elif method == "HIST":
        strName1 = '/ProductionConsumption-FossilGas-HIST.png'
    elif method == "TimeGAN":
        strName1 = '/ProductionConsumption-FossilGas-TimeGAN.png'
    # Save figure to the appropriate path
    figName = "%s%s" % (figuresFolder, strName1)
    plt.savefig(figName, bbox_inches='tight', dpi=300)
    KS_statistic, pValue = ks_2samp(xtmp_data, x1_data)
    df['FossilGas_Gen'] = [round(KS_statistic, 3)]
    ############################################################
    ####################   Solar_Gen   #########################
    ############################################################
    xtmp_data = df_orig["Solar_Gen(MW)"]
    x1_data = df_gen["Solar_Gen(MW)"]

    plt.figure(figsize=(10, 7))
    sns.set(style="darkgrid")
    origData = sns.histplot(df_orig, x=xtmp_data, color="green", label="Original data",stat="density")
    genData = sns.histplot(df_gen, x=x1_data, color="red", label="Generated data",stat="density")
    plt.legend(prop={"size": 17})
    plt.xlabel("Solar_Gen(MW)", fontsize=18)
    plt.ylabel("Density", fontsize=18)
    if method == "KDE":
        strName1 = '/ProductionConsumption-Solar-KDE.png'
    elif method == "HIST":
        strName1 = '/ProductionConsumption-Solar-HIST.png'
    elif method == "TimeGAN":
        strName1 = '/ProductionConsumption-Solar-TimeGAN.png'
    # Save figure to the appropriate path
    figName = "%s%s" % (figuresFolder, strName1)
    plt.savefig(figName, bbox_inches='tight', dpi=300)
    KS_statistic, pValue = ks_2samp(xtmp_data, x1_data)
    df['Solar_Gen'] = [round(KS_statistic, 3)]
    ############################################################
    #####################   Wind_Gen   #########################
    ############################################################
    xtmp_data = df_orig["Wind_Gen(MW)"]
    x1_data = df_gen["Wind_Gen(MW)"]

    plt.figure(figsize=(10, 7))
    sns.set(style="darkgrid")
    origData = sns.histplot(df_orig, x=xtmp_data, color="green", label="Original data",stat="density")
    genData = sns.histplot(df_gen, x=x1_data, color="red", label="Generated data",stat="density")
    plt.legend(prop={"size": 17})
    plt.xlabel("Wind_Gen(MW)", fontsize=18)
    plt.ylabel("Density", fontsize=18)
    if method == "KDE":
        strName1 = '/ProductionConsumption-Wind-KDE.png'
    elif method == "HIST":
        strName1 = '/ProductionConsumption-Wind-HIST.png'
    elif method == "TimeGAN":
        strName1 = '/ProductionConsumption-Wind-TimeGAN.png'
    # Save figure to the appropriate path
    figName = "%s%s" % (figuresFolder, strName1)
    plt.savefig(figName, bbox_inches='tight', dpi=300)
    KS_statistic, pValue = ks_2samp(xtmp_data, x1_data)
    df['Wind_Gen'] = [round(KS_statistic, 3)]
    ############################################################
    ##################   Total_Load   ##########################
    ############################################################
    xtmp_data = df_orig["Total_Load(MW)"]
    x1_data = df_gen["Total_Load(MW)"]

    plt.figure(figsize=(10, 7))
    sns.set(style="darkgrid")
    origData = sns.histplot(df_orig, x=xtmp_data, color="green", label="Original data",stat="density")
    genData = sns.histplot(df_gen, x=x1_data, color="red", label="Generated data",stat="density")
    plt.legend(prop={"size": 17})
    plt.xlabel("Total_Load(MW)", fontsize=18)
    plt.ylabel("Density", fontsize=18)
    if method == "KDE":
        strName1 = '/ProductionConsumption-TotalLoad-KDE.png'
    elif method == "HIST":
        strName1 = '/ProductionConsumption-TotalLoad-HIST.png'
    elif method == "TimeGAN":
        strName1 = '/ProductionConsumption-TotalLoad-TimeGAN.png'
    # Save figure to the appropriate path
    figName = "%s%s" % (figuresFolder, strName1)
    plt.savefig(figName, bbox_inches='tight', dpi=300)
    KS_statistic, pValue = ks_2samp(xtmp_data, x1_data)
    df['Total_Load'] = [round(KS_statistic, 3)]
    ############################################################
    column_list = list(df)
    column_list.remove('Method')
    ksAVG = df[column_list].mean(axis=1)
    df['Average_KS'] = round(ksAVG, 3)

    if method == "KDE":
        strName1 = '/Metrics-ProductionConsumption-KDE.csv'
    elif method == "HIST":
        strName1 = '/Metrics-ProductionConsumption-HIST.csv'
    elif method == "TimeGAN":
        strName1 = '/Metrics-ProductionConsumption-TimeGAN.csv'

    # Save metrics-file to the appropriate directory
    if (folderToSave == None):
        figName = pathProdCons + strName1
    else:
        figName = folderToSave + '/' + jsonData['pathGeneratedProdCons'] + strName1
    df.to_csv(figName, index=False)
    ############################################################

def Plot_ProdCons_TimeSeries (jsonData, pathProdCons, folderToSave=None):
    method = jsonData['method']
    df = pd.DataFrame(columns=['Method', 'Lignite_Gen', 'FossilGas_Gen', 'Solar_Gen', 'Wind_Gen', 'Total_Load'])
    if method == "KDE":
        fileName = pathProdCons + '/GeneratedData_ProductionConsumption-KDE.csv'
    elif method == "HIST":
        fileName = pathProdCons + '/GeneratedData_ProductionConsumption-HIST.csv'
    elif method == "TimeGAN":
        fileName = pathProdCons + '/GeneratedData_ProductionConsumption-TimeGAN.csv'
    else:
        print("\nERROR: Wrong configuration for variable 'method'\nCheck .json file")
        sys.exit()

    df_gen = pd.read_csv(fileName)
    # Calculate the time horizon
    startDate = pd.to_datetime(df_gen['Date']).dt.date.iloc[0]
    endDate = pd.to_datetime(df_gen['Date']).dt.date.iloc[-1]
    timeHorizon = (endDate.year - startDate.year) * 12 + (endDate.month - startDate.month) + 1
    if timeHorizon < 3:
        print("\nWARNING: TimeSeries plots can only be generated\nfor a time horizon of 3 months or more.")
        return None
    startYear = pd.to_datetime(df_gen['Date']).dt.year.iloc[0]
    endYear = pd.to_datetime(df_gen['Date']).dt.year.iloc[-1]
    df_tmp = df_gen[pd.to_datetime(df_gen['Date']).dt.year == startYear]
    startMonth = pd.to_datetime(df_tmp['Date']).dt.month.iloc[0]
    endMonth = pd.to_datetime(df_tmp['Date']).dt.month.iloc[-1]
    randYear = startYear
    if (endMonth - startMonth < 3):
        df_tmp = df_gen[pd.to_datetime(df_gen['Date']).dt.year == endYear]
        startMonth = pd.to_datetime(df_tmp['Date']).dt.month.iloc[0]
        endMonth = pd.to_datetime(df_tmp['Date']).dt.month.iloc[-1]
        randYear = endYear
    randMonth = random.randrange(startMonth + 1, endMonth, 1)
    mask1 = (df_gen['Day_of_Week'] == 1) & (df_gen['Time_of_Day'] == 1) & (df_gen['Month_of_Year'] == randMonth) & (
                df_gen['Year'] == randYear)
    df_timeSeries1 = df_gen.loc[mask1].reset_index(drop=True)
    day1 = pd.to_datetime(df_timeSeries1['Date']).dt.day.iloc[1]
    day2 = pd.to_datetime(df_timeSeries1['Date']).dt.day.iloc[2]
    mask = (pd.to_datetime(df_gen['Date']).dt.month == randMonth) & \
           (pd.to_datetime(df_gen['Date']).dt.day >= day1) & \
           (pd.to_datetime(df_gen['Date']).dt.day < day2) & \
           (pd.to_datetime(df_gen['Date']).dt.year == randYear)
    df_gen_1week = df_gen.loc[mask].reset_index(drop=True)

    df_orig = pd.read_csv(jsonData['pathOriginalProdCons'])
    mask = (pd.to_datetime(df_orig['Date']).dt.month == randMonth) & \
           (pd.to_datetime(df_orig['Date']).dt.day >= day1) & \
           (pd.to_datetime(df_orig['Date']).dt.day < day2) & \
           (pd.to_datetime(df_orig['Date']).dt.year == 2020)
    df_orig_1week = df_orig.loc[mask].reset_index(drop=True)

    if (folderToSave == None):
        figuresFolder = pathProdCons + '/' + jsonData['pathFigures']
    else:
        figuresFolder = folderToSave + '/' + jsonData['pathGeneratedProdCons'] + '/' + jsonData['pathFigures']
    # Create the appropriate directory if doesn't exist
    isExist = os.path.exists(figuresFolder)
    if not isExist:
        os.makedirs(figuresFolder)
    ############################################################
    ##################   Lignite_Gen   #########################
    ############################################################
    sns.set(style="darkgrid")
    plt.figure(figsize=(11, 5))
    fig = df_orig_1week["Lignite_Gen(MW)"].plot(label='Original Data')
    fig1 = df_gen_1week["Lignite_Gen(MW)"].plot(label='Generated Data')
    fig.set_ylabel('Lignite_Gen (MW)')
    fig.set_xlabel('1 week period')
    if method == "KDE":
        fig.set_title("TimeSeries Lignite Generation-KDE")
        fig.legend()
        strName1 = '/TimeSeries_Lignite-KDE.png'
        figName = "%s%s" % (figuresFolder, strName1)
    elif method == "HIST":
        fig.set_title("TimeSeries Lignite Generation-HIST")
        fig.legend()
        strName1 = '/TimeSeries_Lignite-HIST.png'
        figName = "%s%s" % (figuresFolder, strName1)
    elif method == "TimeGAN":
        fig.set_title("TimeSeries Lignite Generation-TimeGan")
        fig.legend()
        strName1 = '/TimeSeries_Lignite-TimeGAN.png'
        figName = "%s%s" % (figuresFolder, strName1)
    plt.savefig(figName, bbox_inches='tight', dpi=300)
    ############################################################
    ##################   FossilGas_Gen   #######################
    ############################################################
    plt.figure(figsize=(11, 5))
    fig = df_orig_1week["FossilGas_Gen(MW)"].plot(label='Original Data')
    fig1 = df_gen_1week["FossilGas_Gen(MW)"].plot(label='Generated Data')
    fig.set_ylabel('FossilGas_Gen (MW)')
    fig.set_xlabel('1 week period')
    if method == "KDE":
        fig.set_title("TimeSeries Fossil Gas Generation-KDE")
        fig.legend()
        strName1 = '/TimeSeries_FossilGas-KDE.png'
        figName = "%s%s" % (figuresFolder, strName1)
    elif method == "HIST":
        fig.set_title("TimeSeries Fossil Gas Generation-HIST")
        fig.legend()
        strName1 = '/TimeSeries_FossilGas-HIST.png'
        figName = "%s%s" % (figuresFolder, strName1)
    elif method == "TimeGAN":
        fig.set_title("TimeSeries Fossil Gas Generation-TimeGan")
        fig.legend()
        strName1 = '/TimeSeries_FossilGas-TimeGAN.png'
        figName = "%s%s" % (figuresFolder, strName1)
    plt.savefig(figName, bbox_inches='tight', dpi=300)
    ############################################################
    ####################   Solar_Gen   #########################
    ############################################################
    plt.figure(figsize=(11, 5))
    fig = df_orig_1week["Solar_Gen(MW)"].plot(label='Original Data')
    fig1 = df_gen_1week["Solar_Gen(MW)"].plot(label='Generated Data')
    fig.set_ylabel('Solar_Gen (MW)')
    fig.set_xlabel('1 week period')
    if method == "KDE":
        fig.set_title("TimeSeries Solar Generation-KDE")
        fig.legend()
        strName1 = '/TimeSeries_Solar-KDE.png'
        figName = "%s%s" % (figuresFolder, strName1)
    elif method == "HIST":
        fig.set_title("TimeSeries Solar Generation-HIST")
        fig.legend()
        strName1 = '/TimeSeries_Solar-HIST.png'
        figName = "%s%s" % (figuresFolder, strName1)
    elif method == "TimeGAN":
        fig.set_title("TimeSeries Solar Generation-TimeGan")
        fig.legend()
        strName1 = '/TimeSeries_Solar-TimeGAN.png'
        figName = "%s%s" % (figuresFolder, strName1)
    plt.savefig(figName, bbox_inches='tight', dpi=300)
    ############################################################
    #####################   Wind_Gen   #########################
    ############################################################
    plt.figure(figsize=(11, 5))
    fig = df_orig_1week["Wind_Gen(MW)"].plot(label='Original Data')
    fig1 = df_gen_1week["Wind_Gen(MW)"].plot(label='Generated Data')
    fig.set_ylabel('Wind_Gen (MW)')
    fig.set_xlabel('1 week period')
    if method == "KDE":
        fig.set_title("TimeSeries Wind Generation-KDE")
        fig.legend()
        strName1 = '/TimeSeries_Wind-KDE.png'
        figName = "%s%s" % (figuresFolder, strName1)
    elif method == "HIST":
        fig.set_title("TimeSeries Wind Generation-HIST")
        fig.legend()
        strName1 = '/TimeSeries_Wind-HIST.png'
        figName = "%s%s" % (figuresFolder, strName1)
    elif method == "TimeGAN":
        fig.set_title("TimeSeries Wind Generation-TimeGan")
        fig.legend()
        strName1 = '/TimeSeries_Wind-TimeGAN.png'
        figName = "%s%s" % (figuresFolder, strName1)
    plt.savefig(figName, bbox_inches='tight', dpi=300)
    ############################################################
    ##################   Total_Load   ##########################
    ############################################################
    plt.figure(figsize=(11, 5))
    fig = df_orig_1week["Total_Load(MW)"].plot(label='Original Data')
    fig1 = df_gen_1week["Total_Load(MW)"].plot(label='Generated Data')
    fig.set_ylabel('Total_Load (MW)')
    fig.set_xlabel('1 week period')
    if method == "KDE":
        fig.set_title("TimeSeries Total Load Consumption-KDE")
        fig.legend()
        strName1 = '/TimeSeries_TotalLoad-KDE.png'
        figName = "%s%s" % (figuresFolder, strName1)
    elif method == "HIST":
        fig.set_title("TimeSeries Total Load Consumption-HIST")
        fig.legend()
        strName1 = '/TimeSeries_TotalLoad-HIST.png'
        figName = "%s%s" % (figuresFolder, strName1)
    elif method == "TimeGAN":
        fig.set_title("TimeSeries Total Load Consumption-TimeGan")
        fig.legend()
        strName1 = '/TimeSeries_TotalLoad-TimeGAN.png'
        figName = "%s%s" % (figuresFolder, strName1)
    plt.savefig(figName, bbox_inches='tight', dpi=300)


