import pandas as pd
import numpy as np
import glob
import os

#####################################################################
####### MyElectricAvenue-EVTripData.csv - EV Driver Behavior ########
#####################################################################
# Read in the EVTripData CSV
td = pd.read_csv('InputData/Original_Data/MyElectricAvenue_Data/EVTripData.csv')
td.TripStartDateTime = pd.to_datetime(td.TripStartDateTime)
td.TripStopDateTime = pd.to_datetime(td.TripStopDateTime)
td['TripTime(min)'] = (td['TripStopDateTime'] - td['TripStartDateTime']) / np.timedelta64(1, 'm')
td.drop(td.columns[5], axis = 1, inplace = True)
td.columns = ['ParticipantID','TripStartDateTime','TripStopDateTime', 'TripDistance(m)','PowerConsumption(Wh)','TripTime(min)']

# Removes rows that contain missing data for even just one column.
df = td.dropna()

df_final = pd.DataFrame(columns=['ParticipantID','TripStartMonth','TripStartDay','TripStartHour','TripStopMonth','TripStopDay','TripStopHour','TripTime(min)','TripDistance(m)','PowerConsumption(Wh)'])
df['TripStartDateTime'] = pd.to_datetime(df['TripStartDateTime'],format='%Y-%m-%d %H:%M:%S')
df['TripStopDateTime'] = pd.to_datetime(df['TripStartDateTime'],format='%Y-%m-%d %H:%M:%S')
df_final['ParticipantID'] = df['ParticipantID']
df_final['TripStartMonth'] = df['TripStartDateTime'].dt.month
df_final['TripStartDay'] = df['TripStartDateTime'].dt.day
df_final['TripStartHour'] = df['TripStartDateTime'].dt.hour
df_final['TripStopMonth'] = df['TripStopDateTime'].dt.month
df_final['TripStopDay'] = df['TripStopDateTime'].dt.day
df_final['TripStopHour'] = df['TripStopDateTime'].dt.hour
df_final['TripTime(min)'] = round(df['TripTime(min)'])
df_final['TripDistance(m)'] = df['TripDistance(m)']
df_final['PowerConsumption(Wh)'] = df['PowerConsumption(Wh)']
df_final['Velocity(km/h)'] = round((df['TripDistance(m)']/1000)/(df_final['TripTime(min)']/60))

# Replacing infinite with nan
df_final['Velocity(km/h)'].replace([np.inf, -np.inf], np.nan, inplace=True)
# df_final['Velocity(km/h)'].dropna(inplace=True)
# df_final['Velocity(km/h)'].reset_index(drop=True, inplace=True)
df_final['Velocity(km/h)'] = df_final['Velocity(km/h)'].dropna()
df_final['Velocity(km/h)'] = df_final['Velocity(km/h)'].reset_index(drop=True)

# Write DataFrame to CSV
df_final.to_csv('InputData/PreProcessed_Data/EVTripData_PreProcessed.csv', index=False)

#####################################################################
###### MyElectricAvenue-EVChargeData.csv - EV Driver Behavior #######
#####################################################################
# Read in the EVChargeData CSV
cd = pd.read_csv('InputData/Original_Data/MyElectricAvenue_Data/EVChargeData.csv')
cd.BatteryChargeStartDate = pd.to_datetime(cd.BatteryChargeStartDate)
cd.BatteryChargeStopDate = pd.to_datetime(cd.BatteryChargeStopDate)
cd['SoC_Diff(of 12)'] = cd['Ending SoC (of 12)'] - cd['Starting SoC (of 12)']
cd['ChargingTime(min)'] = (cd['BatteryChargeStopDate'] - cd['BatteryChargeStartDate']) / np.timedelta64(1, 'm')
cd.columns = ['ParticipantID','BatteryChargeStartDate','BatteryChargeStopDate','Starting_SoC(of 12)', 'Ending_SoC(of 12)', 'SoC_Diff(of 12)', 'ChargingTime(min)']

# Removes rows that contain missing data for even just one column.
df = cd.dropna()

scale = np.frompyfunc(lambda x, min, max: (x - min) / (max - min), 3, 1)
data_start = df['Starting_SoC(of 12)']
data_end = df['Ending_SoC(of 12)']
min = 0
max = 12

df_final = pd.DataFrame(columns=['ParticipantID','BatteryChargeStartMonth','BatteryChargeStartDay','BatteryChargeStartHour','BatteryChargeStopMonth','BatteryChargeStopDay','BatteryChargeStopHour','ChargingTime(min)','Starting_SoC','Ending_SoC','SoC_Diff'])
df['BatteryChargeStartDate'] = pd.to_datetime(df['BatteryChargeStartDate'],format='%Y-%m-%d %H:%M:%S')
df['BatteryChargeStopDate'] = pd.to_datetime(df['BatteryChargeStopDate'],format='%Y-%m-%d %H:%M:%S')
df_final['ParticipantID'] = df['ParticipantID']
df_final['BatteryChargeStartMonth'] = df['BatteryChargeStartDate'].dt.month
df_final['BatteryChargeStartDay'] = df['BatteryChargeStartDate'].dt.day
df_final['BatteryChargeStartHour'] = df['BatteryChargeStartDate'].dt.hour
df_final['BatteryChargeStopMonth'] = df['BatteryChargeStopDate'].dt.month
df_final['BatteryChargeStopDay'] = df['BatteryChargeStopDate'].dt.day
df_final['BatteryChargeStopHour'] = df['BatteryChargeStopDate'].dt.hour
df_final['ChargingTime(min)'] = df['ChargingTime(min)']
df_final['Starting_SoC'] = round(scale(data_start, min, max).astype(float),2)
df_final['Ending_SoC'] = round(scale(data_end, min, max).astype(float),2)
df_final['SoC_Diff'] = round(df_final['Ending_SoC'] - df_final['Starting_SoC'],2)

# Write DataFrame to CSV
df_final.to_csv('InputData/PreProcessed_Data/EVChargeData_PreProcessed.csv', index=False)

#####################################################################
################## Mendeley-EV's - EVs Specs ########################
#####################################################################
# Read in the FEV-data-Excel XLSX
df = pd.read_excel('InputData/Original_Data/FEV-data-Excel.xlsx', engine='openpyxl')

# Write DataFrame to CSV
df.to_csv('InputData/Original_Data/EV_specs.csv', index=False)

def apply_category(capacity):
    if 17 <= capacity < 40:
        cat = 1
    elif 40 <= capacity < 70:
        cat = 2
    else:
        cat = 3
    return cat

# Make a smaller csv-only the columns we want.
df = pd.read_csv('InputData/Original_Data/EV_specs.csv', usecols = ['Car full name','Battery capacity [kWh]','Maximum DC charging power [kW]','mean - Energy consumption [kWh/100 km]'])
df.columns = ['CarModel','BatteryCapacity(kWh)','Maximum_DC_Charging_Power(kW)','MeanEnergyConsumption(kWh/100km)']
df.iloc[39,3] = 14.9
df.iloc[40,3] = 16
df.iloc[41,3] = 16.6
df.iloc[42,3] = 19
df.iloc[43,3] = 19.3
df.iloc[44,3] = 22.6
df.iloc[45,3] = 23.6
df = df.dropna()
df = df.reset_index(drop=True)
# df_orig.drop(df_orig.columns[2], axis = 1, inplace = True)
df['Category'] = df.apply(lambda row: apply_category(row['BatteryCapacity(kWh)']),axis=1)
df = df.sort_values(['BatteryCapacity(kWh)', 'MeanEnergyConsumption(kWh/100km)'],ignore_index=True)
# Write DataFrame to CSV
df.to_csv('InputData/PreProcessed_Data/EV_specs_PreProcessed.csv', index=False)

#####################################################################
################ Create the csv with charging types #################
#####################################################################

# initialise data of lists.
data = {'ChargerType': ['Regular electricity socket 13A', 'Single phase 16A', 'Single phase 32A',
                        '3 phase-16A per phase', '3 phase-32A per phase', '3 phase-60A per phase',
                        '3 phase-DC', '3 phase-DC'],
        'ChargerRating': ['Slow','Slow','Fast','Fast','Fast','Rapid','Rapid','Rapid'],
        'AC_DC': ['AC','AC','AC','AC','AC','AC','DC','DC'],
        'Rated_Power(kW)': [3, 3.7, 7.4, 11, 22, 43, 50, 120]}

# Create DataFrame
df = pd.DataFrame(data)
df.to_csv('InputData/PreProcessed_Data/Charging_Specs.csv', index=False)

#####################################################################
############## ENTSOE - Renewable Generation Profiles ###############
#####################################################################
strName1 = 'InputData/Original_Data/Entsoe_Data/Actual_Generation_'
strName2 = 'InputData/Original_Data/Entsoe_Data/Total_Load_'
strName3 = 'InputData/PreProcessed_Data/Entsoe/Entsoe_'
strNameEnd = '.csv'
year = 2017
filename = "%s%s%s" % (strName1, year, strNameEnd)

# Loop to read our 8 original .csv file, 4 for Actual Generation and 4 for Total Load
for i in range(0,4):
    filename = "%s%s%s" % (strName1, year, strNameEnd)
    df = pd.read_csv(filename)

    dfCopy = df.copy()
    dfCopy[['Start_Date','Finish_Date']] = dfCopy['MTU'].apply(lambda x: pd.Series(str(x).split("- ")))
    dfCopy['Start_Date'] = pd.to_datetime(dfCopy['Start_Date'],format='%d.%m.%Y %H:%M ')

    df_final = pd.DataFrame(columns=['Date','Year','Month_of_Year','Day_of_Week','Time_of_Day','Lignite_Gen(MW)','FossilGas_Gen(MW)','Solar_Gen(MW)','Wind_Gen(MW)','Total_Load(MW)','Import_Export(MW)'])
    df_final['Date'] = dfCopy['Start_Date'].dt.date
    df_final['Year'] = dfCopy['Start_Date'].dt.year
    df_final['Month_of_Year'] = dfCopy['Start_Date'].dt.month
    df_final['Day_of_Week'] = dfCopy['Start_Date'].dt.dayofweek + 1
    df_final['Time_of_Day'] = dfCopy['Start_Date'].dt.hour +1
    df_final['Lignite_Gen(MW)'] = dfCopy['Fossil Brown coal/Lignite  - Actual Aggregated [MW]']
    df_final['FossilGas_Gen(MW)'] = dfCopy['Fossil Gas  - Actual Aggregated [MW]']
    df_final['Solar_Gen(MW)'] = dfCopy['Solar  - Actual Aggregated [MW]']
    df_final['Wind_Gen(MW)'] = dfCopy['Wind Onshore  - Actual Aggregated [MW]']

    filename = "%s%s%s" % (strName2, year, strNameEnd)
    df2 = pd.read_csv(filename)
    df_final['Total_Load(MW)'] = df2['Actual Total Load [MW] - Greece (GR)']
    df_final['Import_Export(MW)'] = df_final['Total_Load(MW)'] - (df_final['Lignite_Gen(MW)']+df_final['FossilGas_Gen(MW)']+df_final['Solar_Gen(MW)']+df_final['Wind_Gen(MW)'])

    df_final = df_final.dropna()
    df_final = df_final.reset_index(drop=True)

    filename = "%s%s%s" % (strName3, year, strNameEnd)
    # Write DataFrame to CSV
    df_final.to_csv(filename, index=False)
    year = year+1

# Concat the 4 csv's into the final one
path = "InputData/PreProcessed_Data/Entsoe"
path2 = "InputData/PreProcessed_Data"
merged_files = os.path.join(path, "Entsoe_*.csv")
filename_merged = "%s%s" % (path2, "/Entsoe_PreProcessed.csv")

merged_list = glob.glob(merged_files)
df_merged = pd.concat(map(pd.read_csv, merged_list), ignore_index=True)
df_merged.to_csv(filename_merged, index=False)