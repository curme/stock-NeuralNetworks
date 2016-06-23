import sys
import json
import numpy as np
from PyQt5.QtWidgets   import QApplication
from Interface.Widgets import MainWindow
from Data.Manager      import DataManager
from Machines.Manager  import MachinesManager

class FANNS:

    def __init__(self):

        print "Info: ", "Create FANNS"

        #app          = QApplication(sys.argv)

        # system function delegation agent
        self.funcsAgent = self.FunctionAgent()
        self.funcsAgent.setAgent()

        # system interface
        #self.mainWindow = MainWindow()

        #sys.exit(app.exec_())

    class FunctionAgent:

        def __init__(self):

            print "Info: ", "Create empty function agent"

            self.dataManager = DataManager()
            self.machines    = MachinesManager()

        def setAgent(self):

            print "Info: ", "Set function agent from configure file"

            # read config file
            config = None
            with file('./FANNS/system.config', 'r') as f: config = json.load(f)
            accounts = config['accounts']
            filepath = config['filepath']
            stash    = config['stash'   ]

            # set data manager
            data_manager_path = filepath['root'] + filepath['data']
            mysql_host = "localhost"
            mysql_localhost_root= accounts['databases']["mysql_localhost_root"]
            self.dataManager.setManager(data_manager_path, mysql_host,
                                        mysql_localhost_root["username"],
                                        mysql_localhost_root["password"])

            # set machine Manager
            self.machines.setManager(self.dataManager, stash['machines'])

        def saveConfig(self):

            print "Info: ", "Save function agent configure file"

            with file('./FANNS/system.config', 'r') as f: config = json.load(f)

            # save machines config
            atol = lambda array: list([list(item) for item in array])
            dtos = lambda date : date.strftime('%Y-%m-%d')
            # save HSIDailyTrendNN config
            config["stash"]["machines"]["HSIDailyTrendNN"]["status"] = \
                self.machines.HSIDailyTrendNNSubManager.status
            config["stash"]["machines"]["HSIDailyTrendNN"]["Xtrain"] = \
                atol(self.machines.HSIDailyTrendNNSubManager.Xtrain)
            config["stash"]["machines"]["HSIDailyTrendNN"]["ytrain"] = \
                atol(self.machines.HSIDailyTrendNNSubManager.ytrain)
            config["stash"]["machines"]["HSIDailyTrendNN"]["Xval"]   = \
                atol(self.machines.HSIDailyTrendNNSubManager.Xval)
            config["stash"]["machines"]["HSIDailyTrendNN"]["yval"]   = \
                atol(self.machines.HSIDailyTrendNNSubManager.yval)
            config["stash"]["machines"]["HSIDailyTrendNN"]["Xtest"]  = \
                atol(self.machines.HSIDailyTrendNNSubManager.Xtest)
            config["stash"]["machines"]["HSIDailyTrendNN"]["ytest"]  = \
                atol(self.machines.HSIDailyTrendNNSubManager.ytest)
            config["stash"]["machines"]["HSIDailyTrendNN"]["model"]  = \
                self.machines.HSIDailyTrendNNSubManager.model
            config["stash"]["machines"]["HSIDailyTrendNN"]["modelSDate"]  = \
                dtos(self.machines.HSIDailyTrendNNSubManager.modelSDate)
            config["stash"]["machines"]["HSIDailyTrendNN"]["modelEDate"]  = \
                dtos(self.machines.HSIDailyTrendNNSubManager.modelEDate)

            json.dump(config, file('./FANNS/system.config', 'w+'))
