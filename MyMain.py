import time
import json
import os

def Data_Generation (inputJasonFile=None):
    if (inputJasonFile==None):
        with open("InputData.json") as jsonFile:
            inputJasonFile = json.load(jsonFile)
            jsonFile.close()

    # Create the appropriate output directory
    path = inputJasonFile['pathGenerated']
    isExist = os.path.exists(path)
    if not isExist:
        os.makedirs(path)
    folderName = 'OutputData-' + time.strftime("%Y_%m_%d_%H_%M_%S")
    dirName = path+'/'+folderName
    os.makedirs(dirName)

    if (inputJasonFile['folderToRead'] != 'InputData'):
        inputJasonFile['pathOriginalProdCons'] = inputJasonFile['pathOriginalProdCons'].replace("InputData",inputJasonFile['folderToRead'])
        inputJasonFile['pathOriginalProdCons2020'] = inputJasonFile['pathOriginalProdCons2020'].replace("InputData",inputJasonFile['folderToRead'])
        inputJasonFile['pathEVSpecs'] = inputJasonFile['pathEVSpecs'].replace("InputData",inputJasonFile['folderToRead'])
        inputJasonFile['pathChargerSpecs'] = inputJasonFile['pathChargerSpecs'].replace("InputData",inputJasonFile['folderToRead'])
        inputJasonFile['pathEVChargeDataPreProcessed'] = inputJasonFile['pathEVChargeDataPreProcessed'].replace("InputData",inputJasonFile['folderToRead'])
        inputJasonFile['pathEVTripDataPreProcessed'] = inputJasonFile['pathEVTripDataPreProcessed'].replace("InputData",inputJasonFile['folderToRead'])
        inputJasonFile['pathFreqTableDailyChargeWdays'] = inputJasonFile['pathFreqTableDailyChargeWdays'].replace("InputData",inputJasonFile['folderToRead'])
        inputJasonFile['pathFreqTableDailyChargeWend'] = inputJasonFile['pathFreqTableDailyChargeWend'].replace("InputData",inputJasonFile['folderToRead'])
        inputJasonFile['pathFreqTableChargeStartHourWdays'] = inputJasonFile['pathFreqTableChargeStartHourWdays'].replace("InputData",inputJasonFile['folderToRead'])
        inputJasonFile['pathFreqTableChargeStartHourWend'] = inputJasonFile['pathFreqTableChargeStartHourWend'].replace("InputData",inputJasonFile['folderToRead'])
        inputJasonFile['pathFreqTableStartingSoCWdays'] = inputJasonFile['pathFreqTableStartingSoCWdays'].replace("InputData",inputJasonFile['folderToRead'])
        inputJasonFile['pathFreqTableStartingSoCWend'] = inputJasonFile['pathFreqTableStartingSoCWend'].replace("InputData",inputJasonFile['folderToRead'])
        inputJasonFile['pathFreqTableEndingSoCWdays'] = inputJasonFile['pathFreqTableEndingSoCWdays'].replace("InputData",inputJasonFile['folderToRead'])
        inputJasonFile['pathFreqTableEndingSoCWend'] = inputJasonFile['pathFreqTableEndingSoCWend'].replace("InputData",inputJasonFile['folderToRead'])
        inputJasonFile['pathFreqTableDailyTripsWdays'] = inputJasonFile['pathFreqTableDailyTripsWdays'].replace("InputData",inputJasonFile['folderToRead'])
        inputJasonFile['pathFreqTableDailyTripsWend'] = inputJasonFile['pathFreqTableDailyTripsWend'].replace("InputData",inputJasonFile['folderToRead'])
        inputJasonFile['pathFreqTableTripStartHourWdays'] = inputJasonFile['pathFreqTableTripStartHourWdays'].replace("InputData",inputJasonFile['folderToRead'])
        inputJasonFile['pathFreqTableTripStartHourWend'] = inputJasonFile['pathFreqTableTripStartHourWend'].replace("InputData",inputJasonFile['folderToRead'])
        inputJasonFile['pathFreqTableVelocityWdays'] = inputJasonFile['pathFreqTableVelocityWdays'].replace("InputData",inputJasonFile['folderToRead'])
        inputJasonFile['pathFreqTableVelocityWend'] = inputJasonFile['pathFreqTableVelocityWend'].replace("InputData",inputJasonFile['folderToRead'])

    newJsonPath = dirName + '/New_InputData.json'
    with open(newJsonPath, 'w') as f:
        json.dump(inputJasonFile, f,indent="")
        f.close()

    with open(newJsonPath) as jsonFile:
        inputJasonFile = json.load(jsonFile)
        jsonFile.close()

    import Generate_ProductionConsumptionData as genProdCons
    genProdCons.Generate_ProdConsData(inputJasonFile,dirName)

    # import Generate_DriverBehaviorData as genDriverBeh
    # genDriverBeh.Generate_DriverData(inputJasonFile,dirName)

if __name__ == '__main__':
    start_time = time.time()

    Data_Generation()

    total_elapsed_time = round(time.time() - start_time, 2)
    print("Done in {} seconds".format(total_elapsed_time))