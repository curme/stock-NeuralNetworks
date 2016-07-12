from . import Evaluator
from HSIDailyTrendNN                import HSIDailyTrendNNManager
from HSIFutureHalfHourTrendLSTMNN   import HSIFutureHalfHourTrendLSTMNNManager

class MachinesManager:

    def __init__(self):

        print "Info: ", "Create empty Machines manager"

        self.dataManager = None
        self.evaluator   = Evaluator()
        self.HSIDailyTrendNNSubManager = HSIDailyTrendNNManager()
        self.HSIFutureHalfHourTrendLSTMNNSubManager = HSIFutureHalfHourTrendLSTMNNManager()

    def setManager(self, dataManager, machineConfig):

        print "Info: ", "Set Machines Manager"

        self.dataManager = dataManager

        # set HSI Daily Trend Predict NN
        HSIDailyTrendNNConfig = machineConfig['HSIDailyTrendNN']
        self.HSIDailyTrendNNSubManager.setManager( \
            dataManager = self.dataManager, \
            evaluator   = self.evaluator,   \
            labels      = HSIDailyTrendNNConfig["labels"],     \
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

        # set HSI Futures Half Hour Trend Predict LSTM NN
        self.HSIFutureHalfHourTrendLSTMNNSubManager.setManager(\
            dataManager = self.dataManager, \
            evaluator   = self.evaluator)
