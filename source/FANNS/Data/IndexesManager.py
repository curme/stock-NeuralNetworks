import os
import pandas

class IndexesManager:

    def __init__(self):
        """
        Create an empty Indexes database manager
        """

        print "Info: ", "Create empty Database Indexes Sub Data Manager"

        self.filepath   = ""
        self.tablepath  = ""
        self.cursor     = None
        self.conn       = None

    def setManager(self, filepath, tablepath, conn, cursor):

        print "Info: ", "Set Database Indexes Sub Data Manager"

        self.filepath   = filepath
        self.tablepath  = tablepath
        self.conn       = conn
        self.cursor     = cursor

    def checkTables(self):

        print "Info: ", "Check tables for database Indexes"

        # build all of the tables
        all_tables = os.listdir(self.tablepath)
        indexes_tables = [t for t in all_tables if t.split('.')[0]=="Indexes"]
        for table in indexes_tables:
            sql_file = file(self.tablepath + table)
            sql      = sql_file.read()
            self.cursor.execute(sql)
            self.conn.commit()

    def loadHSIDailyFromFile(self):

        print "Info: ", "Load HSI Daily Data from static file"

        HSIDaily = None
        with file(self.filepath+'HSIDaily.csv', 'r+') as f:
            HSIDaily = f.read()

        HSIDaily = HSIDaily.split('\n')[1:][::-1][1:]
        convert = lambda item: tuple([item[0]]+[float(i) for i in item[1:]])
        HSIDaily = [convert(item.split(',')) for item in HSIDaily]

        sql = "USE INDEXES; TRUNCATE TABLE HSIDaily; INSERT INTO HSIDaily " + \
              "(date, open, high, low, close, volume, adj_close) VALUES "

        for data in HSIDaily: sql += str(data) + ','
        sql = sql[:-1]+';'

        self.cursor.execute(sql)
        self.conn.commit()

    def queryHSIDaily(self, startdate, enddate):

        startdate  = startdate.strftime('%Y-%m-%d')
        enddate    =   enddate.strftime('%Y-%m-%d')

        print "Info: ", "Query Indexes.HSIDaily data from %s to %s" % (startdate, enddate)

        conditions = "date >= '%s' AND date <= '%s'" % (startdate, enddate)
        result = self.queryInDataFrame("Indexes", "HSIDaily", conditions)
        return result

    def queryHSIDailyAna(self, startdate, enddate):

        startdate  = startdate.strftime('%Y-%m-%d')
        enddate    =   enddate.strftime('%Y-%m-%d')

        print "Info: ", "Query Indexes.HSIDailyAna data from %s to %s" % (startdate, enddate)

        conditions = "date >= '%s' AND date <= '%s'" % (startdate, enddate)
        result = self.queryInDataFrame("Indexes", "HSIDailyAna", conditions)
        return result

    def storeHSIDailyAna(self, dataFrame):

        if dataFrame.empty: return

        datelist = list(dataFrame['date'])
        datelist.sort()
        startdate= datelist[ 0].strftime('%Y-%m-%d')
        enddate  = datelist[-1].strftime('%Y-%m-%d')

        print "Info: ", "Store Indexes.HSIDailyAna data from %s to %s" % (startdate, enddate)

        sql = "DELETE FROM Indexes.HSIDailyAna WHERE date>='%s' and date<='%s';" % (startdate, enddate)
        self.cursor.execute(sql)
        self.conn.commit()

        sql = "INSERT INTO Indexes.HSIDailyAna " + \
              "(date,            close_change_1d, close_change_2d, " + \
              " close_change_3d, close_change_4d, close_change_5d, " + \
              " close_change_6d, close_change_7d, close_change_8d, " + \
              " close_change_9d, close_change_10d,status) VALUES "
        for date in datelist:
            data = dataFrame.loc[dataFrame.date==date]
            tmp  = "('%s',%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'%s')," % \
                    (date.strftime('%Y-%m-%d'), str(float(data['close_change_1d'])), \
                    str(float(data['close_change_2d'])),str(float(data['close_change_3d'])), \
                    str(float(data['close_change_4d'])),str(float(data['close_change_5d'])), \
                    str(float(data['close_change_6d'])),str(float(data['close_change_7d'])), \
                    str(float(data['close_change_8d'])),str(float(data['close_change_9d'])), \
                    str(float(data['close_change_10d'])),data['status'].min())
            sql += tmp
        sql = sql[:-1]+";"
        self.cursor.execute(sql)
        self.conn.commit()

    def queryInDataFrame(self, database, table, conditions=None):

        # get columns
        sql = "SHOW COLUMNS FROM %s.%s;" % (database, table)
        self.cursor.execute(sql)
        columns = self.cursor.fetchall()
        columns = [item[0] for item in columns]

        # query data in table
        sql = "SELECT * FROM %s.%s" % (database, table)
        if not conditions == None: sql += " WHERE %s" % conditions
        sql += ';'
        self.cursor.execute(sql)
        data = self.cursor.fetchall()

        # convert columns and data into dictionary
        result = {}
        for key in columns: result[key] = []
        for row in data:
            for i, item in zip(range(len(row)), row):
                result[columns[i]].append(item)
        result.pop('id')

        # convert dictionary into pandas DF and return
        return pandas.DataFrame.from_dict(result)
