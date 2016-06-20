import sys
import json
from PyQt5.QtWidgets   import QApplication
from Interface.Widgets import MainWindow
from Data.Manager      import DataManager
from Machines.Manager  import MachinesManager

class FANNS:

    def __init__(self):

        #app          = QApplication(sys.argv)

        # system function delegation agent
        self.funcsAgent = self.FunctionAgent()
        self.funcsAgent.setAgent()

        # system interface
        #self.mainWindow = MainWindow()

        #sys.exit(app.exec_())

    class FunctionAgent:

        def __init__(self):

            self.dataManager = DataManager()
            self.machines    = MachinesManager()

        def setAgent(self):

            # read config file
            config = None
            with file('./FANNS/system.config', 'r') as f: config = json.load(f)
            accounts = config['accounts']
            filepath = config['filepath']
            status   = config['status']

            # set data manager
            data_manager_path = filepath['root'] + filepath['data']
            mysql_host = "localhost"
            mysql_localhost_root= accounts['databases']["mysql_localhost_root"]
            self.dataManager.setManager(data_manager_path, mysql_host,
                                        mysql_localhost_root["username"],
                                        mysql_localhost_root["password"])

            # set machine Manager
            self.machines.setManager(self.dataManager, status['machines'])

        def saveConfig(self):

            # save machines config
            with file('./FANNS/system.config', 'r') as f: config = json.load(f)
            config['status']['machines']['HSIDailyTrendNN'] = \
                self.machines.HSIDailyTrendNNSubManager.status
            json.dump(config, file('./FANNS/system.config', 'w+'))
