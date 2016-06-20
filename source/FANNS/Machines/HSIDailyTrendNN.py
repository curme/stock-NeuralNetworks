import math
from pandas   import DataFrame
from datetime import datetime, timedelta

class HSIDailyTrendNNManager:

    def __init__(self):

        self.model       = None
        self.status      = 0    # 0 for nothing done; 1 for data processed
        self.dataManager = None
        self.Xtrain      = None
        self.ytrain      = None
        self.Xval        = None
        self.yval        = None
        self.Xtest       = None
        self.ytest       = None
        self.modelSDate  = None
        self.modelEDate  = None

    def setManager(self, dataManager = None, modelSDate = None, \
                         modelEDate  = None, status     = None):

        if dataManager: self.dataManager = dataManager
        if modelSDate : self.modelSDate  = modelSDate
        if modelEDate : self.modelEDate  = modelEDate
        if status     : self.status      = status

    def process(self):

        self.processData()
        self.devideDataSet()

    def devideDataSet(self):

        # get ana data
        anaSDate = self.modelSDate
        anaEDate = self.modelEDate
        ana      = self.dataManager.indexesHSIDailyAnaQueryByDate(anaSDate, anaEDate)

        # label data
        X  = zip(list(ana['date']), list(ana['close_change_1d']))
        y  = []
        Xp, Xn = [item[1] for item in X if item[1] > 0], [item[1] for item in X if item[1] < 0]
        Xp.sort(), Xn.sort()
        DU = Xp[int(len(Xp)*0.9)]
        U  = Xp[int(len(Xp)*0.5)]
        D  = Xn[int(len(Xn)*0.5)]
        DD = Xn[int(len(Xn)*0.1)]
        for date, change in X:
            if   change >= DU : y.append('DU')
            elif change >  U  : y.append('U')
            elif change <  D  : y.append('D')
            elif change <= DD : y.append('DD')
            else :              y.append('F')

        print y

    def processData(self):

        # if the data has been processed, skip processing
        if not self.status == 0: return

        # get raw price data
        tDelta   = timedelta(days=21)
        rawSDate = self.modelSDate-tDelta
        rawEDate = self.modelEDate
        raw      = self.dataManager.indexesHSIDailyQueryByDate(rawSDate, rawEDate)

        # get ana data
        anaSDate = self.modelSDate
        anaEDate = self.modelEDate
        ana      = self.dataManager.indexesHSIDailyAnaQueryByDate(anaSDate, anaEDate)

        # calculate changes for each day
        oneDay = timedelta(days=1)
        for stretch in xrange((anaEDate-anaSDate).days+1):

            date = anaSDate + oneDay*stretch

            # if not trading day, skip it
            if raw[raw.date == date.date()].empty: continue

            # if ana database hasn't contain this day, add it
            if ana[ana.date == date.date()].empty:
                # [DATE, NONE, ..., NONE, STATUS]
                dfTmp = DataFrame([[None]*12], columns=list(ana.columns))
                dfTmp.loc[0, 'date'], dfTmp.loc[0, 'status'] = date.date(), '0'*10
                ana = ana.append(dfTmp)
            if ana.loc[ana.date == date.date()]['status'].min() == '1'*10:
                ana = ana[ana.date != date.date()]; continue;
            flags= list(ana.loc[ana.date == date.date()]['status'].min())

            # check every status flag
            rawSlice, i = [raw.loc[raw.date==date.date()]], 1
            while len(rawSlice) <= 10:
                row = raw.loc[raw.date==(date-oneDay*i).date()]
                if not row.empty: rawSlice.append(row)
                i += 1
            for fi, flag in [p for p in zip(range(len(flags)), flags) if p[1]=='0']:
                column = "close_change_%sd" % str(fi+1)
                cp = float(rawSlice[   0]['close'])
                bp = float(rawSlice[fi+1]['close'])
                ana.loc[ana.date==date.date(), column] = math.log(cp/bp)
                flags[fi] = '1'

            ana.loc[ana.date==date.date(), 'status'] = ''.join(flags)

        self.dataManager.indexesHSIDailyAnaStore(ana)
        self.status = 1

    def trainingModel(self, X, y, Xval, yval):

        pass

    def clearModel(self):

        pass

    def predict(self):

        pass
