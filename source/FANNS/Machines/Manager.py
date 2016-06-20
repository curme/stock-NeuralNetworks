from HSIDailyTrendNN import HSIDailyTrendNNManager

class MachinesManager:

    def __init__(self):

        self.HSIDailyTrendNNSubManager = HSIDailyTrendNNManager()

    def setManager(self, dataManager, machinesStatus):

        self.dataManager = dataManager
        self.HSIDailyTrendNNSubManager.setManager( \
            dataManager = self.dataManager,
            status = machinesStatus['HSIDailyTrendNN'])
