from datetime import datetime, date, timedelta
from FANNS.fanns import FANNS

if __name__ == "__main__":

    app = FANNS()

    modelSDate = datetime.strptime('2015-05-01' , '%Y-%m-%d')
    modelEDate = datetime.strptime('2016-04-30' , '%Y-%m-%d')
    #app.funcsAgent.dataManager.indexesHSIDailyLoadStaticFile()
    #app.funcsAgent.dataManager.indexesHSIDailyQueryByDate(modelSDate, modelEDate)

    app.funcsAgent.machines.HSIDailyTrendNNSubManager.setManager(modelSDate=modelSDate, modelEDate=modelEDate)
    app.funcsAgent.machines.HSIDailyTrendNNSubManager.process()

    app.funcsAgent.saveConfig()
