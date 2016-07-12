import os
import pandas
from datetime import datetime, timedelta, time

class FuturesManager:

    def __init__(self):
        """
        Create an empty Futures database manager
        """

        print "Info: ", "Create empty Database Futures Sub Data Manager"

        self.filepath   = ""
        self.tablepath  = ""
        self.cursor     = None
        self.conn       = None

    def setManager(self, filepath, tablepath, conn, cursor):

        print "Info: ", "Set Database Futures Sub Data Manager"

        self.filepath   = filepath
        self.tablepath  = tablepath
        self.conn       = conn
        self.cursor     = cursor

    def checkTables(self):

        print "Info: ", "Check tables for database Futures"

        # build all of the tables
        all_tables = os.listdir(self.tablepath)
        indexes_tables = [t for t in all_tables if t.split('.')[0]=="Futures"]
        for table in indexes_tables:
            sql_file = file(self.tablepath + table)
            sql      = sql_file.read()
            self.cursor.execute(sql)
            self.conn.commit()

    # read HSI data from raw market data and calculate out the minute OHLCV then store into DB
    def loadHSIMinuteOHLCVFromFiles(self):

        print "Info: ", "Load HSI minute data from static file"

        # count OHLCV for minute level data
        HSIFiles = [f for f in os.listdir(self.filepath) if f.find("HSI") > -1]
        HSIMinute= []
        time_bar, price_list, volume_list = "", [None], [0]
        for HSIFile in HSIFiles:
            with file(self.filepath+HSIFile, 'r+') as f: data = f.read().split('\r\n')
            for line in data:
                line = line.split(',')
                if not line[-1] in ['000', '001', '002']: continue
                if not len(line[6]) == 6: line[6] = '0'+line[6]
                current_time = line[5]+line[6][:-2]+'00'
                if not current_time == time_bar:
                    HSIMinute.append([         time_bar,    str(price_list[ 0]),\
                                      str(max(price_list)), str(min(price_list)),\
                                      str( price_list[-1]), str(sum(volume_list))])
                    time_bar = current_time
                    price_list, volume_list = [], []
                price_list.append( float(line[-3]))
                volume_list.append(float(line[-2]))
        HSIMinute.pop(0)

        # generate SQL
        sql = "USE FUTURES; TRUNCATE TABLE HSIMinute; INSERT INTO HSIMinute " + \
              "(datetime, open, high, low, close, volume) VALUES "
        for record in HSIMinute: sql += '("%s",%s,%s,%s,%s,%s)' % tuple(record) + ','
        sql = sql[:-1]+';'

        # insert data into database
        self.cursor.execute(sql)
        self.conn.commit()

    def calHSIHalfHourOHLCV(self):

        print "Info: ", "Calculate HSI half hour data from DB"

        # read out all minute data from db
        minuteOhlcv = self.queryInDataFrame("FUTURES", "HSIMinute")
        startTime   = minuteOhlcv.iloc[ 0]["datetime"]
        endTime     = minuteOhlcv.iloc[-1]["datetime"]
        timeSlot    = []
        halfHour    = timedelta(minutes = 30)
        oneHour     = timedelta(hours   =  1)
        oneDay      = timedelta(days    =  1)
        marketOpen  = time(hour= 9, minute=15)
        marketMid   = time(hour= 12,minute= 0)
        marketMidC  = time(hour= 13,minute= 0)
        marketClose = time(hour= 16,minute=15)
        timeTmp     = datetime.combine(startTime.date(), marketOpen)

        # get each half hour of the whole time period
        while timeTmp < endTime:

            if   (timeTmp+halfHour).time() >= marketMid and \
                 (timeTmp+halfHour).time() <= marketMidC:
                  timeSlot.append((timeTmp, timeTmp+halfHour+oneHour))
            else: timeSlot.append((timeTmp, timeTmp+halfHour))

            if   (timeTmp+halfHour).time() >= marketClose:
                  timeTmp = datetime.combine(timeTmp.date()+oneDay, marketOpen)
            elif (timeTmp+halfHour).time() >= marketMid and \
                 (timeTmp+halfHour).time() <= marketMidC:
                  timeTmp += halfHour+oneHour
            else: timeTmp += halfHour

        # calculate OHLCV for each half hour
        halfHourOHLCV = []
        for s, e in timeSlot:
            inSlot = minuteOhlcv[minuteOhlcv.datetime>=s].loc[minuteOhlcv.datetime<e]
            if inSlot.empty: continue
            s = s.strftime('%Y-%m-%d %H-%M-%S')
            e = e.strftime('%Y-%m-%d %H-%M-%S')
            o = str(inSlot.iloc[ 0]["open"])
            h = str(max(inSlot["high"]))
            l = str(min(inSlot["low"]))
            c = str(inSlot.iloc[-1]["close"])
            v = str(sum(inSlot["volume"]))
            halfHourOHLCV.append((s, e, o, h, l, c, v))

        # generate sql
        sql = "USE FUTURES; TRUNCATE TABLE HSIHalfhour; INSERT INTO HSIHalfhour " + \
              "(starttime, endtime, open, high, low, close, volume) VALUES "
        for record in halfHourOHLCV: sql += '("%s","%s",%s,%s,%s,%s,%s)' % record + ','
        sql = sql[:-1]+';'

        # insert data into database
        self.cursor.execute(sql)
        self.conn.commit()

    def queryHSIHalfHourOHLCVAll(self):

        return self.queryInDataFrame("Futures", "HSIHalfHour")

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
