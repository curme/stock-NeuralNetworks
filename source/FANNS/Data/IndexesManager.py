import os

class IndexesManager:

    def __init__(self):
        """
        Create an empty Indexes database manager
        """

        self.filepath   = ""
        self.tablepath  = ""
        self.cursor     = None
        self.comm       = None

    def setManager(self, filepath, tablepath, conn, cursor):

        self.filepath   = filepath
        self.tablepath  = tablepath
        self.conn       = conn
        self.cursor     = cursor

    def checkTables(self):

        # build all of the tables
        all_tables = os.listdir(self.tablepath)
        indexes_tables = [t for t in all_tables if t.split('_')[0]=="Indexes"]
        for table in indexes_tables:
            sql_file = file(self.tablepath + table)
            sql      = sql_file.read()
            self.cursor.execute(sql)
            self.conn.commit()

    def loadHSIDailyFromFile(self):

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

    def readHSIDaily(self):

        pass

    def storeHSIDailyLabels(self):

        pass


