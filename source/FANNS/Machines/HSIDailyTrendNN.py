import math
import random
import tensorflow as tf
import numpy      as np
from   pandas   import DataFrame
from   datetime import datetime, timedelta

class HSIDailyTrendNNManager:

    def __init__(self):

        print "Info: ", "Create empty HSI Daily Predict NN"

        self.name        = "HSI Daily Trend Predict NN"
        self.model       = {}
        self.status      = 0    # 0 for nothing done; 1 for data processed
        self.dataManager = None
        self.evaluator   = None
        self.labels      = None
        self.Xtrain      = None
        self.ytrain      = None
        self.ytrainPre   = None
        self.Xval        = None
        self.yval        = None
        self.yvalPre     = None
        self.Xtest       = None
        self.ytest       = None
        self.ytestPre    = None
        self.modelSDate  = None
        self.modelEDate  = None

        print "Info: ", self.name

    def setManager(self, dataManager = None, evaluator  = None, \
                         modelSDate  = None, modelEDate = None, \
                         status      = None, Xtrain     = None, \
                         ytrain      = None, Xval       = None, \
                         yval        = None, Xtest      = None, \
                         ytest       = None, model      = None, \
                         labels      = None):

        print "Info: ", "Set %s" % self.name

        ltoa = lambda llist : np.array(llist)
        stod = lambda string: datetime.strptime(string , '%Y-%m-%d')
        dtos = lambda date  : date.strftime('%Y-%m-%d')

        if not dataManager == None : self.dataManager = dataManager
        if not evaluator   == None : self.evaluator   = evaluator
        if not status      == None : self.status      = status
        if not labels      == None : self.labels      = labels
        if not Xtrain      == None : self.Xtrain      = ltoa(Xtrain)
        if not ytrain      == None : self.ytrain      = ltoa(ytrain)
        if not Xval        == None : self.Xval        = ltoa(Xval)
        if not yval        == None : self.yval        = ltoa(yval)
        if not Xtest       == None : self.Xtest       = ltoa(Xtest)
        if not ytest       == None : self.ytest       = ltoa(ytest)
        if not model       == None : self.model       = model

        if not modelSDate  == None and not self.modelSDate:
            self.modelSDate = stod(modelSDate)
        if not modelEDate  == None and not self.modelEDate:
            self.modelEDate = stod(modelEDate)
        if not modelSDate  == None and not stod(modelSDate) == self.modelSDate:
            self.status, self.modelSDate = 0, stod(modelSDate)
        if not modelEDate  == None and not stod(modelEDate) == self.modelEDate:
            self.status, self.modelEDate = 0, stod(modelEDate)

        print "Info: ", "Status level %s" % str(self.status)

    def process(self):

        print "Info: ", "Run %s" % self.name

        self.preprocessData()
        self.divideDataSet()
        self.trainingModel()
        self.evaluate()

    # data processing
    def preprocessData(self):

        print "Info: ", "%s, pre process data" % self.name

        # if the data has been processed, skip processing
        if self.status > 0: print "Info: ", "Pre-processing has been done"; return

        # get raw price data
        oneDay   = timedelta(days=1)
        tDelta   = oneDay * 35
        rawSDate = self.modelSDate
        rawEDate = self.modelEDate+tDelta
        raw      = self.dataManager.indexesHSIDailyQueryByDate(rawSDate, rawEDate)

        # get ana data
        anaSDate = self.modelSDate
        anaEDate = self.modelEDate
        ana      = self.dataManager.indexesHSIDailyAnaQueryByDate(anaSDate, anaEDate)

        # calculate changes for each day
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
                row = raw.loc[raw.date==(date+oneDay*i).date()]
                if not row.empty: rawSlice.append(row)
                i += 1
            for fi, flag in [p for p in zip(range(len(flags)), flags) if p[1]=='0']:
                column = "close_change_%sd" % str(fi+1)
                cp = float(rawSlice[   0]['close'])
                fp = float(rawSlice[fi+1]['close'])
                ana.loc[ana.date==date.date(), column] = math.log(fp/cp)
                flags[fi] = '1'

            ana.loc[ana.date==date.date(), 'status'] = ''.join(flags)

        self.dataManager.indexesHSIDailyAnaStore(ana)

        # set status level 1, pre precessing done
        self.status = 1

    # divide data sets
    def divideDataSet(self):

        print "Info: ", "%s, divide data sets" % self.name

        if self.status < 1: print "Info: ", "Pre-processing doesn't been done"; return
        if self.status > 1: print "Info: ", "Data sets dividing has been done"; return

        # get raw price data
        oneDay   = timedelta(days=1)
        tDelta   = oneDay*35
        rawSDate = self.modelSDate-tDelta
        rawEDate = self.modelEDate
        raw      = self.dataManager.indexesHSIDailyQueryByDate(rawSDate, rawEDate)

        # get ana data
        anaSDate = self.modelSDate
        anaEDate = self.modelEDate
        ana      = self.dataManager.indexesHSIDailyAnaQueryByDate(anaSDate, anaEDate)

        # label data
        self.labels = ['U', 'F', 'D']
        CC1 = zip(list(ana['date']), list(ana['close_change_1d']))
        CCp = [item[1] for item in CC1 if item[1] > 0]; CCp.sort();
        CCn = [item[1] for item in CC1 if item[1] < 0]; CCn.sort();
        U   = CCp[int(len(CCp)*0.33)]
        D   = CCn[int(len(CCn)*0.66)]
        X,y = [], []

        for date, change in CC1:
            Xitem, i = [], 1
            while len(Xitem) < 15*1:
                row, i  =  raw.loc[raw.date==(date-oneDay*i)], i+1
                # if not row.empty: Xitem+=list(row[['open','high','low','close','volume']].min())
                if not row.empty: Xitem+=list(row[['close']].min())
            X.append(Xitem)
            if   change >  U  : y.append([1.0,0.0,0.0])   # for U
            elif change <  D  : y.append([0.0,0.0,1.0])   # for D
            else :              y.append([0.0,1.0,0.0])   # for F

        # range input data into [-1,1]
        X       = np.array(X)
        hl      = [(max(list(X[:,i])), min(list(X[:,i]))) for i in range(len(X[0]))]
        for row in X:
            for i in range(len(row)):
                row[i] = (row[i]-hl[i][1])/(hl[i][0]-hl[i][1])*2-1
        X       = list([list(row) for row in X])

        # divide data into training data, cross validation data and test data
        dataLength  = len(y)
        XvalLength  = int(dataLength*0)
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

    def trainingModel(self):

        print "Info: ", "%s, training model" % self.name

        if self.status < 2: print "Info: ", "[E]Data Set dividing doesn't been done"; return
        if self.status > 2: print "Info: ", "Model training has been done"; return

        # parameters
        inputNeurons    = len(self.Xtrain[0])
        outputNeurons   = len(self.ytrain[0])
        hiddenNeurons   = 50
        learningRate    = 0.01
        learningTimes   = int(raw_input("Input: Learning times: "))

        # data placeholder
        X       = tf.placeholder(tf.float32, [None, inputNeurons ])
        y_      = tf.placeholder(tf.float32, [None, outputNeurons])

        # hidden layer 1
        weights0= tf.Variable(tf.random_normal([inputNeurons, hiddenNeurons]))
        bias0   = tf.Variable(tf.random_normal([hiddenNeurons]))
        a1      = tf.nn.sigmoid(tf.add(tf.matmul(X,  weights0), bias0))

        # hidden layer 2
        weights1= tf.Variable(tf.random_normal([hiddenNeurons, hiddenNeurons]))
        bias1   = tf.Variable(tf.random_normal([hiddenNeurons]))
        a2      = tf.nn.sigmoid(tf.add(tf.matmul(a1, weights1), bias1))

        # output layer
        weights2= tf.Variable(tf.random_normal([hiddenNeurons, outputNeurons]))
        bias2   = tf.Variable(tf.random_normal([outputNeurons]))
        y       = tf.nn.softmax(tf.add(tf.matmul(a2, weights2), bias2))

        cross_entropy = tf.reduce_mean(tf.reduce_sum(-(y_) * tf.log(y) - (1-y_) * tf.log(1-y), reduction_indices=[1]))
        train_step    = tf.train.AdamOptimizer(learningRate).minimize(cross_entropy)

        init    = tf.initialize_all_variables()
        sess    = tf.Session()
        sess.run(init)

        # training
        for _ in range(learningTimes): sess.run(train_step, feed_dict={X: self.Xtrain, y_: self.ytrain})

        # do predict after train
        getLabel = lambda classNumber: [0.0]*classNumber + [1.0] + [0.0]*(outputNeurons-classNumber-1)
        self.ytrainPre = [getLabel(item) for item in sess.run(tf.argmax(y,1), feed_dict={X: self.Xtrain})]
        # self.yvalPre   = [getLabel(item) for item in sess.run(tf.argmax(y,1), feed_dict={X: self.Xval  })]
        self.ytestPre  = [getLabel(item) for item in sess.run(tf.argmax(y,1), feed_dict={X: self.Xtest })]

        # close session
        sess.close()

        # set status level 3, trained
        self.status = 3

    def evaluate(self):

        print "Info: ", "%s, evaluate model" % self.name

        if self.status < 3: print "Info: ", "[E]Model training doesn't been done"; return

        trainAccuracy, trainRecall, trainPrecise  = self.evaluator.eval(predict = self.ytrainPre, correct = self.ytrain, labels=self.labels, dataSet="train")
        # valAccuracy  , valRecall  , valPrecise    = self.evaluator.eval(predict = self.yvalPre  , correct = self.yval  , labels=self.labels, dataSet="cross validation")
        testAccuracy , testRecall , testPrecise   = self.evaluator.eval(predict = self.ytestPre , correct = self.ytest , labels=self.labels, dataSet="test")


    def clearModel(self):

        pass

    def predict(self):

        pass
