from HSIDailyTrendNN import HSIDailyTrendNNManager

class MachinesManager:

    def __init__(self):

        print "Info: ", "Create empty Machines manager"

        self.HSIDailyTrendNNSubManager = HSIDailyTrendNNManager()

    def setManager(self, dataManager, machineConfig):

        print "Info: ", "Set Machines Manager"

        self.dataManager = dataManager

        # set HSI Daily Trend Predict NN
        HSIDailyTrendNNConfig = machineConfig['HSIDailyTrendNN']
        self.HSIDailyTrendNNSubManager.setManager( \
            dataManager = self.dataManager, \
            modelSDate  = HSIDailyTrendNNConfig["modelSDate"], \
            modelEDate  = HSIDailyTrendNNConfig["modelEDate"], \
            status = HSIDailyTrendNNConfig["status"], \
            Xtrain = HSIDailyTrendNNConfig["Xtrain"], \
            ytrain = HSIDailyTrendNNConfig["ytrain"], \
            Xval   = HSIDailyTrendNNConfig["Xval"],   \
            yval   = HSIDailyTrendNNConfig["yval"],   \
            Xtest  = HSIDailyTrendNNConfig["Xtest"],  \
            ytest  = HSIDailyTrendNNConfig["ytest"],  \
            model  = HSIDailyTrendNNConfig["model"])
