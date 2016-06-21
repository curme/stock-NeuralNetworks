from HSIDailyTrendNN import HSIDailyTrendNNManager

class MachinesManager:

    def __init__(self):

        self.HSIDailyTrendNNSubManager = HSIDailyTrendNNManager()

    def setManager(self, dataManager, machineConfig):

        self.dataManager = dataManager

        # set HSI Daily Trend Predict NN
        HSIDailyTrendNNConfig = machineConfig['HSIDailyTrendNN']
        self.HSIDailyTrendNNSubManager.setManager( \
            dataManager = self.dataManager, \
            status = HSIDailyTrendNNConfig["status"], \
            Xtrain = HSIDailyTrendNNConfig["Xtrain"], \
            ytrain = HSIDailyTrendNNConfig["ytrain"], \
            Xval   = HSIDailyTrendNNConfig["Xval"],   \
            yval   = HSIDailyTrendNNConfig["yval"],   \
            Xtest  = HSIDailyTrendNNConfig["Xtest"],  \
            ytest  = HSIDailyTrendNNConfig["ytest"])
