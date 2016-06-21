import math
import random
import tensorflow as tf
import numpy      as np
from   pandas   import DataFrame
from   datetime import datetime, timedelta

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
                         modelEDate  = None, status     = None, \
                         Xtrain      = None, ytrain     = None, \
                         Xval        = None, yval       = None, \
                         Xtest       = None, ytest      = None):

        ltoa = lambda llist: np.array(llist)

        if dataManager: self.dataManager = dataManager
        if modelSDate : self.modelSDate  = modelSDate
        if modelEDate : self.modelEDate  = modelEDate
        if status     : self.status      = status
        if Xtrain     : self.Xtrain      = ltoa(Xtrain)
        if ytrain     : self.ytrain      = ltoa(ytrain)
        if Xval       : self.Xval        = ltoa(Xval)
        if yval       : self.yval        = ltoa(yval)
        if Xtest      : self.Xtest       = ltoa(Xtest)
        if ytest      : self.ytest       = ltoa(ytest)

    def process(self):

        self.preprocessData()
        self.divideDataSet()
        self.trainingModel()

    def trainingModel(self):

        X       = tf.placeholder(tf.float32, [None, 75])
        y_      = tf.placeholder(tf.float32, [None, 5 ])
        weights = tf.Variable(tf.zeros([75, 5]))
        bias    = tf.Variable(tf.zeros([5]))
        y       = tf.nn.softmax(tf.matmul(X, weights) + bias)
        cross_entropy = tf.reduce_mean(-tf.reduce_sum(y_ * tf.log(y),reduction_indices=[1]))
        train_step    = tf.train.GradientDescentOptimizer(0.5).minimize(cross_entropy)

        init    = tf.initialize_all_variables()
        sess    = tf.Session()
        sess.run(init)

        print "Model training..."

        sess.run(train_step, feed_dict={X: self.Xtrain, y_: self.ytrain})

        correct_prediction = tf.equal(tf.argmax(y,1), tf.argmax(y_,1))
        accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
        print sess.run(accuracy, feed_dict={X: self.Xval, y_: self.yval})
        print sess.run(accuracy, feed_dict={X: self.Xtest, y_: self.ytest})

    # data processing
    def preprocessData(self):

        # if the data has been processed, skip processing
        if self.status > 0: return "Pre-processing has been done."

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

        # set status level 1, pre precessing done
        self.status = 1

    # divide data sets
    def divideDataSet(self):

        if self.status < 1: return "Pre-processing doesn't been done."
        if self.status > 1: return "Data sets dividing has been done."

        # get raw price data
        tDelta   = timedelta(days=35)
        rawSDate = self.modelSDate-tDelta
        rawEDate = self.modelEDate
        raw      = self.dataManager.indexesHSIDailyQueryByDate(rawSDate, rawEDate)

        # get ana data
        anaSDate = self.modelSDate
        anaEDate = self.modelEDate
        ana      = self.dataManager.indexesHSIDailyAnaQueryByDate(anaSDate, anaEDate)

        # label data
        oneDay = timedelta(days=1)
        CC1 = zip(list(ana['date']), list(ana['close_change_1d']))
        CCp = [item[1] for item in CC1 if item[1] > 0]; CCp.sort();
        CCn = [item[1] for item in CC1 if item[1] < 0]; CCn.sort();
        DU  = CCp[int(len(CCp)*0.9)]
        U   = CCp[int(len(CCp)*0.5)]
        D   = CCn[int(len(CCn)*0.5)]
        DD  = CCn[int(len(CCn)*0.1)]
        X,y = [], []

        for date, change in CC1:
            Xitem, i = [], 1
            while len(Xitem) < 15*5:
                row, i  =  raw.loc[raw.date==(date-oneDay*i)], i+1
                if not row.empty: Xitem+=list(row[['open','high','low','close','volume']].min())
            X.append(Xitem)
            if   change >= DU : y.append([1.0,0.0,0.0,0.0,0.0])   # for DU
            elif change >  U  : y.append([0.0,1.0,0.0,0.0,0.0])   # for U
            elif change <  D  : y.append([0.0,0.0,0.0,1.0,0.0])   # for D
            elif change <= DD : y.append([0.0,0.0,0.0,0.0,1.0])   # for DD
            else :              y.append([0.0,0.0,1.0,0.0,0.0])   # for F

        # divide data into training data, cross validation data and test data
        dataLength  = len(y)
        XvalLength  = int(dataLength*0.2)
        XtestLength = int(dataLength*0.2)
        XtrainLength= dataLength-XvalLength-XtestLength
        Xtrain, Xval, Xtest = [], [], []
        ytrain, yval, ytest = [], [], []

        while len(Xval) < XvalLength:
            index = random.randint(0, len(X)-1)
            Xval.append(X.pop(index))
            yval.append(y.pop(index))
        while len(Xtest)< XtestLength:
            index = random.randint(0, len(X)-1)
            Xtest.append(X.pop(index))
            ytest.append(y.pop(index))
        Xtrain, ytrain = X, y

        # convert list into ndarray
        self.Xtrain, self.ytrain = np.array(Xtrain), np.array(ytrain)
        self.Xval  , self.yval   = np.array(Xval)  , np.array(yval)
        self.Xtest , self.ytest  = np.array(Xtest) , np.array(ytest)

        # set status level 2, data set divided
        self.status = 2

    def clearModel(self):

        pass

    def predict(self):

        pass
