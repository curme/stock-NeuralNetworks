from datetime import datetime, date, timedelta
from FANNS.fanns import FANNS

if __name__ == "__main__":

    app = FANNS()

    modelSDate = '2015-05-11'
    modelEDate = '2016-05-10'
    #app.funcsAgent.dataManager.indexesHSIDailyLoadStaticFile()
    #app.funcsAgent.dataManager.indexesHSIDailyQueryByDate(modelSDate, modelEDate)

    '''
    for _ in range(20):
        input_status = raw_input("Input: Main.py set status level: ")
        if input_status not in [str(i) for i in range(4)] : input_status = 2
        app.funcsAgent.machines.HSIDailyTrendNNSubManager.setManager(modelSDate=modelSDate, modelEDate=modelEDate, status=int(input_status))
        app.funcsAgent.machines.HSIDailyTrendNNSubManager.process()'''

    app.funcsAgent.machines.HSIFutureHalfHourTrendLSTMNNSubManager.process()

    app.funcsAgent.saveConfig()
