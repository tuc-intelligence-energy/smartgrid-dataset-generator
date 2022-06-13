from flask import Flask, render_template, jsonify,request
import glob
import json
import time
import os

app = Flask(__name__)
app.secret_key = "dsyHbaej998jj86wgsu__sdsTs51321bioUC1cal4124"

if __name__ == '__main__':

    @app.route('/', methods=['GET'])
    def home():
        return render_template('client.html')


    @app.route('/api/v1/listInputFolder', methods=['GET'])
    def listInputFolder():
        return jsonify(glob.glob("Output_Data/*"))


    @app.route('/api/v1/runData', methods=['GET','POST'])
    def runData():
        if request.method == 'POST':
            # print(str(request.data))
            resJson = json.loads(request.data)

            with open("InputData.json") as jsonFile:
                originalJson = json.load(jsonFile)
                jsonFile.close()

            originalJson['startDate'] = resJson['startDate']
            originalJson['endDate'] = resJson['endDate']
            originalJson['method'] = resJson['method']
            originalJson['checksMode'] = resJson['checksMode']
            originalJson['numOfDrivers'] = resJson['numOfDrivers']
            originalJson['EVCategory'] = resJson['EVCategory']
            originalJson['ChargerCategory'] = resJson['ChargerCategory']
            originalJson['rollingWindow'] = resJson['rollingWindow']
            originalJson['rollingWindowsTable'] = resJson['rollingWindowsTable']
            originalJson['folderToRead'] = resJson['folderToRead']

            import MyMain
            MyMain.Data_Generation(originalJson)

            return jsonify("Experiment submitted!")

    @app.route('/api/v1/runFigures', methods=['GET','POST'])
    def runFigures():
        if request.method == 'POST':
            resJson = json.loads(request.data)
            split = resJson['folderToReadGeneratedFiguresOnly'].split('\\')
            with open("InputData.json") as jsonFile:
                originalJson = json.load(jsonFile)
                jsonFile.close()
            originalJson['folderToRead'] = resJson['folderToRead']
            originalJson['pathGenerated'] = split[0]
            originalJson['folderToReadGenerated'] = split[0]

            # import MyMain_FiguresOnly
            # MyMain_FiguresOnly.Data_Generation_FiguresOnly(originalJson)

            return jsonify("Experiment submitted!")


    app.run(debug=True, port=5004, threaded=True)
