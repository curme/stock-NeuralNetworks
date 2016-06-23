import os
import json
import pymysql

from IndexesManager import IndexesManager

class DataManager:

    def __init__(self):

        print "Info: ", "Create empty Data Manager"

        self.conn   = None
        self.cursor = None
        self.path   = ""
        self.filepath  = ""
        self.sqlpath   = ""
        self.errStatus = 0
        self.errText   = ""
        self.securities_type = ["Indexes", "Commodities", "Exchanges", "Futures",
                                "Options", "Stocks"]
        self.indexesManager = IndexesManager()

    def setManager(self, path, db_host, db_username, db_password):

        print "Info: ", "Set Data Manager"

        # set data manager path
        self.path = path
        self.filepath = self.path + 'Securities/'
        self.sqlpath  = self.path + 'SQL/'

        try:
            self.conn = pymysql.connect(host=db_host, user=db_username,
                                        password=db_password)
        except:
            self.errStatus = 101
            self.errText   = "Cannot connect to host."
            print self.errText
            print "** Please Retry **"
            return

        self.cursor = self.conn.cursor()

        # and then enable sub manager to connect to database
        self.setSubManager()
        # when connect to database successfully, init database
        self.checkAndInitDatabase()

    def setSubManager(self):

        self.indexesManager.setManager(self.filepath+"Indexes/",
                                       self.sqlpath+"CreateTables/",
                                       self.conn,self.cursor)

    ###########################
    # database check and init #
    ###########################

    # check and init database
    def checkAndInitDatabase(self):

        self.checkDBs()
        self.checkTables()

    # check if all databases are in the host
    def checkDBs(self):

        print "Info: ", "Check Databases"

        if self.cursor == None or not self.errStatus == 0: return

        # get all databases
        self.cursor.execute("show databases;")
        result      = self.cursor.fetchall()
        databases   = [item[0] for item in result]

        # check if some databases missed
        missed_databases = [item for item in self.securities_type if item not in
                            databases]
        if not len(missed_databases) == 0:
            print "Missed databases: " + ', '.join(missed_databases), "."

        # rebuild the missed databases
        for database in missed_databases:
            sql_file = file(self.sqlpath + 'CreateDatabases/%s.sql' % database)
            sql      = sql_file.read().split('\n')[0]
            self.cursor.execute(sql)
            self.conn.commit()
            print "Rebuild database: " + database + "."

    # check if all tables are in the database
    def checkTables(self):

        self.indexesManager.checkTables()

    ##########################
    # Data Manager Interface #
    ##########################
    def indexesHSIDailyLoadStaticFile(self):

        self.indexesManager.loadHSIDailyFromFile()

    def indexesHSIDailyQueryByDate(self, startdate, enddate):

        return self.indexesManager.queryHSIDaily(startdate, enddate)

    def indexesHSIDailyAnaQueryByDate(self, startdate, enddate):

        return self.indexesManager.queryHSIDailyAna(startdate, enddate)

    def indexesHSIDailyAnaStore(self, anaDataFrame):

        self.indexesManager.storeHSIDailyAna(anaDataFrame)

if __name__ == "__main__":

    dm = DataManager()
    config = None
    with file('./FANNS/system.config', 'r') as f: config = json.load(f)
    mysql_host = "localhost"
    mysql_localhost_root = config['accounts']['databases']["mysql_localhost_root"]
    path = config['filepath']['root'] + config['filepath']['data']

    dm.setManager(path, mysql_host,
                  mysql_localhost_root["username"],
                  mysql_localhost_root["password"])

    # load static HSI daily data
    dm.indexesHSIDailyLoadStaticFile()

    #print dm.indexesHSIDailyQueryByDate('2015-01-01', '2015-12-31')
