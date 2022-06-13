import pandas as pd
import numpy as np
from sklearn.neighbors import KernelDensity
from sklearn.model_selection import GridSearchCV
from datetime import datetime
import sys
import time
import json
import os
##############################
from pickle import load
from ydata_synthetic.synthesizers import ModelParameters
from ydata_synthetic.synthesizers.timeseries import TimeGAN
from ydata_synthetic.preprocessing.timeseries.utils import real_data_loading

def GenerateData_KDE (data,colname):
    # Fit KDE (with cross-validation on bandwidth used)
    tmp = data.to_numpy()
    data2 = tmp[:, np.newaxis]
    bandwidth = np.arange(0.05, 1, .9)
    kde = KernelDensity(kernel='gaussian')
    grid = GridSearchCV(kde, {'bandwidth': bandwidth})
    grid.fit(data2)
    kde = grid.best_estimator_
    # Resample
    N_POINTS_RESAMPLE = 1
    resampled = kde.sample(N_POINTS_RESAMPLE)
    # In solar generation we want only positive values, or zeros (at night)
    if colname=='Solar_Gen(MW)':
        if (resampled<=7):
            resampled = 0
    re_resampled = np.reshape(resampled, -1)
    fin_data = np.round(re_resampled)
    return fin_data

def GenerateData_HIST (data,colname):
    numOfSamples = 1
    # print(len(data))
    if ((colname == 'Wind_Gen(MW)') or (colname == 'Lignite_Gen(MW)')):
        bins = 450
        hist, bins = np.histogram(data, bins=bins)
    elif colname == 'Total_Load(MW)':
        bins = 5
        hist, bins = np.histogram(data, bins=bins)
    else:
        bins = 20
        hist, bins = np.histogram(data, bins=bins)
    bin_midpoints = (bins[:-1] + bins[1:]) / 2
    cdf = np.cumsum(hist)
    cdf = cdf / cdf[-1]
    values = np.random.rand(numOfSamples)
    value_bins = np.searchsorted(cdf, values)
    sample_cdf = bin_midpoints[value_bins]
    if colname=='Solar_Gen(MW)':
        if (sample_cdf<=7):
            sample_cdf = 0
    return np.round(sample_cdf)

def Pre_Smoothing (jsonData, df_gen, myCol):
    df_orig = pd.read_csv(jsonData['pathOriginalProdCons2020'])
    df_smooth = pd.DataFrame(columns=[myCol])
    limitIdx = df_gen.tail(12).index.values.astype(int)[0]
    lastIdx = df_gen.tail(1).index.values.astype(int)[0]
    for index, row in df_gen.iterrows():
        if(index<12):
            idxStartGen = 12-(12-index)
            idxEndGen = idxStartGen+23
        elif(index>limitIdx):
            idxStartGen = index-(24-(lastIdx-index))
            idxEndGen = lastIdx
        else:
            idxStartGen = index-12
            idxEndGen = index+11
        df_orig_tmp = df_orig[(df_orig.Month_of_Year == row['Month_of_Year']) &
                          (df_orig.Day_of_Week == row['Day_of_Week']) & (df_orig.Time_of_Day == row['Time_of_Day'])]
        randInterval = df_orig_tmp.sample(n=1)
        idxStart = randInterval.index.values.astype(int)[0]-12
        idxEnd = randInterval.index.values.astype(int)[0]+11
        myDayOrig = df_orig.loc[idxStart:idxEnd].reset_index(drop=True)
        myDayGen = df_gen.loc[idxStartGen:idxEndGen].reset_index(drop=True)
        origMean = round(myDayOrig[myCol].mean())
        genMean = round(myDayGen[myCol].mean())
        meanDiff = abs(origMean - genMean)
        if (origMean > genMean):
            df_smooth.loc[index, myCol] = row[myCol] + round(meanDiff)
        else:
            df_smooth.loc[index, myCol] = row[myCol] - round(meanDiff)
    df_smooth[df_smooth < 0] = 0
    return df_smooth

def Smoothing (jsonData, df_gen):
    df_gen_roll = pd.DataFrame(
        columns=['Date', 'Year', 'Month_of_Year', 'Day_of_Week', 'Time_of_Day', 'Lignite_Gen(MW)',
                 'FossilGas_Gen(MW)', 'Solar_Gen(MW)', 'Wind_Gen(MW)', 'Total_Load(MW)'])
    rollingTable = jsonData['rollingWindowsTable']
    df_gen_roll['Date'] = df_gen['Date']
    df_gen_roll['Year'] = df_gen['Year']
    df_gen_roll['Month_of_Year'] = df_gen['Month_of_Year']
    df_gen_roll['Day_of_Week'] = df_gen['Day_of_Week']
    df_gen_roll['Time_of_Day'] = df_gen['Time_of_Day']

    df_roll_new = pd.DataFrame(
        columns=['Date', 'Year', 'Month_of_Year', 'Day_of_Week', 'Time_of_Day', 'Lignite_Gen(MW)',
                 'FossilGas_Gen(MW)', 'Solar_Gen(MW)', 'Wind_Gen(MW)', 'Total_Load(MW)', 'Import_Export(MW)'])
    df_roll_new['Date'] = df_gen_roll['Date']
    df_roll_new['Year'] = df_gen['Year']
    df_roll_new['Month_of_Year'] = df_gen_roll['Month_of_Year']
    df_roll_new['Day_of_Week'] = df_gen_roll['Day_of_Week']
    df_roll_new['Time_of_Day'] = df_gen_roll['Time_of_Day']

    if rollingTable[0] == 0:
        df_gen_roll['Lignite_Gen(MW)'] = df_gen['Lignite_Gen(MW)']
        df_roll_new['Lignite_Gen(MW)'] = df_gen['Lignite_Gen(MW)']
    else:
        df_gen_roll['Lignite_Gen(MW)'] = Pre_Smoothing(jsonData, df_gen, 'Lignite_Gen(MW)')
        df_roll_new['Lignite_Gen(MW)'] = round(df_gen_roll['Lignite_Gen(MW)'].rolling(window=rollingTable[0], min_periods=1).mean())
    if rollingTable[1] == 0:
        df_gen_roll['FossilGas_Gen(MW)'] = df_gen['FossilGas_Gen(MW)']
        df_roll_new['FossilGas_Gen(MW)'] = df_gen['FossilGas_Gen(MW)']
    else:
        df_gen_roll['FossilGas_Gen(MW)'] = Pre_Smoothing(jsonData, df_gen, 'FossilGas_Gen(MW)')
        df_roll_new['FossilGas_Gen(MW)'] = round(df_gen_roll['FossilGas_Gen(MW)'].rolling(window=rollingTable[1], min_periods=1).mean())
    if rollingTable[2] == 0:
        df_gen_roll['Solar_Gen(MW)'] = df_gen['Solar_Gen(MW)']
        df_roll_new['Solar_Gen(MW)'] = df_gen['Solar_Gen(MW)']
    else:
        df_gen_roll['Solar_Gen(MW)'] = Pre_Smoothing(jsonData, df_gen, 'Solar_Gen(MW)')
        df_roll_new['Solar_Gen(MW)'] = round(df_gen_roll['Solar_Gen(MW)'].rolling(window=rollingTable[2], min_periods=1).mean())
    if rollingTable[3] == 0:
        df_gen_roll['Wind_Gen(MW)'] = df_gen['Wind_Gen(MW)']
        df_roll_new['Wind_Gen(MW)'] = df_gen['Wind_Gen(MW)']
    else:
        df_gen_roll['Wind_Gen(MW)'] = Pre_Smoothing(jsonData, df_gen, 'Wind_Gen(MW)')
        df_roll_new['Wind_Gen(MW)'] = round(df_gen_roll['Wind_Gen(MW)'].rolling(window=rollingTable[3], min_periods=1).mean())
    if rollingTable[4] == 0:
        df_gen_roll['Total_Load(MW)'] = df_gen['Total_Load(MW)']
        df_roll_new['Total_Load(MW)'] = df_gen['Total_Load(MW)']
    else:
        df_gen_roll['Total_Load(MW)'] = Pre_Smoothing(jsonData, df_gen, 'Total_Load(MW)')
        df_roll_new['Total_Load(MW)'] = round(df_gen_roll['Total_Load(MW)'].rolling(window=rollingTable[4], min_periods=1).mean())
    df_gen_roll.drop(df_gen_roll.tail(1).index, inplace=True)
    df_roll_new.drop(df_roll_new.tail(1).index, inplace=True)
    df_roll_new['Import_Export(MW)'] = df_roll_new['Total_Load(MW)'] - (
                df_roll_new['Lignite_Gen(MW)'] + df_roll_new['FossilGas_Gen(MW)'] +
                df_roll_new['Solar_Gen(MW)'] + df_roll_new['Wind_Gen(MW)'])
    return df_roll_new

def Generate_ProdConsData (jsonData,dirName):

    pathProdCons = dirName+'/'+jsonData['pathGeneratedProdCons']
    # Create the appropriate output directory
    isExist = os.path.exists(pathProdCons)
    if not isExist:
        os.makedirs(pathProdCons)

    startDate = jsonData['startDate']
    endDate = jsonData['endDate']
    startDate = datetime.strptime(startDate, '%Y-%m-%d')
    endDate = datetime.strptime(endDate, '%Y-%m-%d')
    df_gen = pd.DataFrame(columns=['Date', 'Year', 'Month_of_Year', 'Day_of_Week', 'Time_of_Day', 'Lignite_Gen(MW)', 'FossilGas_Gen(MW)', 'Solar_Gen(MW)', 'Wind_Gen(MW)', 'Total_Load(MW)', 'Import_Export(MW)'])
    df_gen['Date'] = pd.date_range(start = startDate, end = endDate, freq ='H')
    df_gen['Year'] = df_gen['Date'].dt.year
    df_gen['Month_of_Year'] = df_gen['Date'].dt.month
    df_gen['Day_of_Week'] = df_gen['Date'].dt.dayofweek + 1
    df_gen['Time_of_Day'] = df_gen['Date'].dt.hour + 1
    df_gen['Date'] = df_gen['Date'].dt.date

    method = jsonData['method']
    path = jsonData['pathOriginalProdCons']

    df_orig = pd.read_csv(path)

    if method=="KDE":
        fileName = "/GeneratedData_ProductionConsumption-KDE.csv"
        for i, row in enumerate(df_gen.itertuples(index=False)):
            df_data = df_orig[(df_orig.Month_of_Year == row[df_gen.columns.get_loc('Month_of_Year')]) &
                              (df_orig.Day_of_Week == row[df_gen.columns.get_loc('Day_of_Week')]) &
                              (df_orig.Time_of_Day == row[df_gen.columns.get_loc('Time_of_Day')])]
            df_data_NoDay= df_orig[(df_orig.Month_of_Year == row[df_gen.columns.get_loc('Month_of_Year')]) &
                                   (df_orig.Time_of_Day == row[df_gen.columns.get_loc('Time_of_Day')])]
            df_data_NoTime = df_orig[(df_orig.Month_of_Year == row[df_gen.columns.get_loc('Month_of_Year')]) &
                                     (df_orig.Day_of_Week == row[df_gen.columns.get_loc('Day_of_Week')])]
            df_data_NoDayNoTime = df_orig[(df_orig.Month_of_Year == row[df_gen.columns.get_loc('Month_of_Year')])]

            df_gen.loc[i, 'Lignite_Gen(MW)'] = GenerateData_KDE(df_data_NoDayNoTime['Lignite_Gen(MW)'], 'Lignite_Gen(MW)')
            df_gen.loc[i, 'FossilGas_Gen(MW)'] = GenerateData_KDE(df_data_NoDay['FossilGas_Gen(MW)'], 'FossilGas_Gen(MW)')
            df_gen.loc[i, 'Solar_Gen(MW)'] = GenerateData_KDE(df_data_NoDay['Solar_Gen(MW)'], 'Solar_Gen(MW)')
            df_gen.loc[i, 'Wind_Gen(MW)'] = GenerateData_KDE(df_data_NoDayNoTime['Wind_Gen(MW)'], 'Wind_Gen(MW)')
            df_gen.loc[i, 'Total_Load(MW)'] = GenerateData_KDE(df_data['Total_Load(MW)'], 'Total_Load(MW)')
        df_gen['Import_Export(MW)'] = df_gen['Total_Load(MW)'] - (df_gen['Lignite_Gen(MW)'] + df_gen['FossilGas_Gen(MW)'] +
                                                                  df_gen['Solar_Gen(MW)'] + df_gen['Wind_Gen(MW)'])
        df_gen.drop(df_gen.tail(1).index, inplace=True)

    elif method=="HIST":
        fileName = "/GeneratedData_ProductionConsumption-HIST.csv"
        for i, row in enumerate(df_gen.itertuples(index=False)):
            df_data = df_orig[(df_orig.Month_of_Year == row[df_gen.columns.get_loc('Month_of_Year')]) &
                              (df_orig.Day_of_Week == row[df_gen.columns.get_loc('Day_of_Week')]) &
                              (df_orig.Time_of_Day == row[df_gen.columns.get_loc('Time_of_Day')])]
            df_data_NoDay= df_orig[(df_orig.Month_of_Year == row[df_gen.columns.get_loc('Month_of_Year')]) &
                                   (df_orig.Time_of_Day == row[df_gen.columns.get_loc('Time_of_Day')])]
            df_data_NoTime = df_orig[(df_orig.Month_of_Year == row[df_gen.columns.get_loc('Month_of_Year')]) &
                                     (df_orig.Day_of_Week == row[df_gen.columns.get_loc('Day_of_Week')])]
            df_data_NoDayNoTime = df_orig[(df_orig.Month_of_Year == row[df_gen.columns.get_loc('Month_of_Year')])]

            df_gen.loc[i, 'Lignite_Gen(MW)'] = GenerateData_HIST(df_data_NoDayNoTime['Lignite_Gen(MW)'], 'Lignite_Gen(MW)')
            df_gen.loc[i, 'FossilGas_Gen(MW)'] = GenerateData_HIST(df_data_NoDay['FossilGas_Gen(MW)'], 'FossilGas_Gen(MW)')
            df_gen.loc[i, 'Solar_Gen(MW)'] = GenerateData_HIST(df_data_NoDay['Solar_Gen(MW)'], 'Solar_Gen(MW)')
            df_gen.loc[i, 'Wind_Gen(MW)'] = GenerateData_HIST(df_data_NoDayNoTime['Wind_Gen(MW)'], 'Wind_Gen(MW)')
            df_gen.loc[i, 'Total_Load(MW)'] = GenerateData_HIST(df_data['Total_Load(MW)'], 'Total_Load(MW)')
        df_gen['Import_Export(MW)'] = df_gen['Total_Load(MW)'] - (df_gen['Lignite_Gen(MW)'] + df_gen['FossilGas_Gen(MW)'] +
                                                                  df_gen['Solar_Gen(MW)'] + df_gen['Wind_Gen(MW)'])
        df_gen.drop(df_gen.tail(1).index, inplace=True)

    elif method=="TimeGAN":
        # Specific to TimeGANs
        seq_len = 24
        n_seq = 6
        gamma = 1
        noise_dim = 32
        dim = 128
        log_step = 100
        learning_rate = 5e-4
        # should be optimized
        hidden_dim = 48
        batch_size = 88
        iterations = 10000

        gan_args = ModelParameters(batch_size=batch_size,
                                   lr=learning_rate,
                                   noise_dim=noise_dim,
                                   layers_dim=dim)

        fileName = "/GeneratedData_ProductionConsumption-TimeGAN.csv"
        df_gen.drop(df_gen.tail(1).index, inplace=True)
        # Calculate the time horizon, in order to take the appropriate original data for the comparison
        timeHorizon = (endDate.year - startDate.year) * 12 + (endDate.month - startDate.month)
        if timeHorizon==12:
            ori_data = np.loadtxt(jsonData['pathOriginalProdCons2020'], delimiter=",", skiprows=1,usecols=(5, 6, 7, 8, 9, 10))
            path_synth = 'synthesizer_timegan_488810000.pkl'
        elif timeHorizon==48:
            ori_data = np.loadtxt(jsonData['pathOriginalProdCons'], delimiter=",", skiprows=1,usecols=(5, 6, 7, 8, 9, 10))
            path_synth = 'synthesizer_timegan4years_487510000.pkl'
            print(timeHorizon)
        else:
            print("\nERROR: Invalid time horizon.\nTime horizon for TimeGAN method must be either 12 or 48 months.")
            sys.exit()

        # Data transformations to be applied prior to be used with the synthesizer model
        processed_data = real_data_loading(ori_data, seq_len=seq_len)
        isExist = os.path.exists(path_synth)
        if isExist:
            synth = TimeGAN.load(path_synth)
        else:
            synth = TimeGAN(model_parameters=gan_args, hidden_dim=24, seq_len=seq_len, n_seq=n_seq, gamma=1)
            synth.train(processed_data, train_steps=iterations)
            synth.save(path_synth)
        synth_data = synth.sample(len(df_gen))

        ############  Data Recovery  ##############
        # load the scaler
        scaler = load(open('scaler.pkl', 'rb'))
        tmp = []
        for i in range(0, len(synth_data)):
            _y = synth_data[i][0][:]
            tmp.append(_y)
        for i in range(0, seq_len):
            _z = synth_data[-1][i][:]
            tmp.append(_z)
        # converting list to array
        tmp_arr = np.asarray(tmp)
        recovered_data = np.round(scaler.inverse_transform(tmp_arr))
        rowsToDelete = len(recovered_data)-len(df_gen)
        recovered_data = recovered_data[:-rowsToDelete]
        df_recovered = pd.DataFrame(recovered_data,
                                    columns=['Lignite_Gen(MW)', 'FossilGas_Gen(MW)', 'Solar_Gen(MW)', 'Wind_Gen(MW)',
                                             'Total_Load(MW)', 'Import_Export(MW)'])

        df_gen['Lignite_Gen(MW)'] = df_recovered['Lignite_Gen(MW)']
        df_gen['FossilGas_Gen(MW)'] = df_recovered['FossilGas_Gen(MW)']
        df_gen['Solar_Gen(MW)'] = df_recovered['Solar_Gen(MW)']
        df_gen['Wind_Gen(MW)'] = df_recovered['Wind_Gen(MW)']
        df_gen['Total_Load(MW)'] = df_recovered['Total_Load(MW)']

        df_gen['Import_Export(MW)'] = df_gen['Total_Load(MW)'] - (
                    df_gen['Lignite_Gen(MW)'] + df_gen['FossilGas_Gen(MW)'] + df_gen['Solar_Gen(MW)'] + df_gen[
                'Wind_Gen(MW)'])
    else:
        print("\nERROR: Wrong configuration for variable 'method'\nCheck .json file")
        sys.exit()

    # Write DataFrame to CSV
    saveFile = pathProdCons+fileName
    df_gen.to_csv(saveFile, index=False)

    # For additional data smoothing
    if jsonData['rollingWindow'] == 1:
        df_Smoothed = Smoothing(jsonData,df_gen)
        pathForSmoothed = pathProdCons+'/'+jsonData['pathSmoothedData']
        # Create the appropriate output directory
        isExist = os.path.exists(pathForSmoothed)
        if not isExist:
            os.makedirs(pathForSmoothed)
        saveFile2 = pathForSmoothed + fileName
        df_Smoothed.to_csv(saveFile2, index=False)
        import PlotsMetrics_ProductionConsumptionData as plotProdCons
        plotProdCons.Plot_ProdCons_Histograms(jsonData, pathForSmoothed)
        plotProdCons.Plot_ProdCons_TimeSeries(jsonData, pathForSmoothed)


    import PlotsMetrics_ProductionConsumptionData as plotProdCons
    plotProdCons.Plot_ProdCons_Histograms(jsonData,pathProdCons)
    plotProdCons.Plot_ProdCons_TimeSeries(jsonData,pathProdCons)


