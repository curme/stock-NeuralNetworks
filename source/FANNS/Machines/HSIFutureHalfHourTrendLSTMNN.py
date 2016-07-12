import math
import talib
import numpy      as np
import pandas     as pd
import tensorflow as tf
from tensorflow.models.rnn import rnn_cell


class HSIFutureHalfHourTrendLSTMNNManager:

    def __init__(self):

        print "Info: ", "Create empty HSI Future Half Hour Trend Predict NN"

        self.name        = "HSI Future Half Hour Trend Predict NN"
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

        print "Info: ", self.name

    def setManager(self, dataManager = None, evaluator = None):

        print "Info: ", "Set %s" % self.name

        if not dataManager == None : self.dataManager = dataManager
        if not evaluator   == None : self.evaluator   = evaluator

    def process(self):

        print "Info: ", "Run %s" % self.name

        self.preprocessData()
        self.trainingModel()

    def preprocessData(self):

        print "Info: ", "%s, pre process data" % self.name

        # rescale close price, calculate SMA
        HSIFuturesHalfHourOHLCV = self.dataManager.futuresHSIHalfHourOHLCVQueryAll()
        closePrices  = HSIFuturesHalfHourOHLCV["close"]
        closePiars   = zip(closePrices[:-1], closePrices[1:])
        changeRates  = [math.log(cp/fp) for (cp, fp) in closePiars]+[None]
        closeMean, closeDiff = np.mean(closePrices), max(closePrices)-min(closePrices)
        closePrices  = [(close -closeMean )/float(closeDiff ) for close  in closePrices]
        volumes      = HSIFuturesHalfHourOHLCV["volume"]
        volumeMean,volumeDiff= np.mean(volumes),     max(volumes)    -min(volumes)
        volumes      = [(volume-volumeMean)/float(volumeDiff) for volume in volumes    ]
        SMA          = talib.SMA(np.array(closePrices), 24)
        data         = pd.DataFrame({"closePrices":closePrices, "volumes":volumes,
                                     "changeRates":changeRates, "SMA"    :SMA})
        data         = data.iloc[23:len(data)-1]

        # divide data sets
        Xtrain, ytrain, Xtest, ytest = [], [], [], []
        testULength, testDLength     = [round(len(data)*0.15)]*2
        sampleLength = 24
        for index in range(sampleLength-1, len(data))[::-1]:
            record = data.iloc[index-sampleLength+1:index+1]
            changeRate = record.iloc[-1]["changeRates"]
            x          = []
            [x.append(np.array(record.iloc[ti][["closePrices", "volumes", "SMA"]])) for ti in range(len(record))]
            x          = np.array(x)
            if changeRate >= 0:
                if testULength >= 0:
                    testULength-= 1
                    Xtest.append(x);  ytest .append([1,0])
                else:
                    Xtrain.append(x); ytrain.append([1,0])
            else:
                if testDLength >= 0:
                    testDLength-= 1
                    Xtest.append(x);  ytest .append([0,1])
                else:
                    Xtrain.append(x); ytrain.append([0,1])
        self.Xtrain = Xtrain
        self.ytrain = ytrain
        self.Xtest  = Xtest
        self.ytest  = ytest

    def trainingModel(self):

        print "Info: ", "%s, training model" % self.name

        with tf.Graph().as_default(), tf.Session() as sess:

            with tf.variable_scope("model", reuse=None):
                trainModel = Model()

            sess.run(tf.initialize_all_variables())

            for (x, y) in zip(self.Xtrain, self.ytrain):
                cross_entropy, _ = sess.run([trainModel.cross_entropy, trainModel.train_step], \
                                            feed_dict={trainModel.inputs:[x], trainModel.targets:[y]})
                print cross_entropy

    def evaluate(self):

        print "Info: ", "%s, evaluate model" % self.name

    def clearModel(self):

        pass

    def predict(self):

        pass

# this code is a vanilla LSTM cell from https://github.com/fomorians/lstm-odyssey/blob/master/variants/vanilla.py
# and it is a good standard sample code for LSTM cell with forget, input and output gate, so I use it now
class LSTMCell(rnn_cell.RNNCell):

    def __init__(self, num_blocks):
        self._num_blocks = num_blocks

    @property
    def input_size(self):
        return self._num_blocks

    @property
    def output_size(self):
        return self._num_blocks

    @property
    def state_size(self):
        return 2 * self._num_blocks

    def __call__(self, inputs, state, scope=None):
        with tf.variable_scope(scope or type(self).__name__):
            initializer = tf.random_uniform_initializer(-0.1, 0.1)

            def get_variable(name, shape):
                return tf.get_variable(name, shape, initializer=initializer, dtype=inputs.dtype)

            c_prev, y_prev = tf.split(1, 2, state)

            W_z = get_variable("W_z", [self.input_size, self._num_blocks])
            W_i = get_variable("W_i", [self.input_size, self._num_blocks])
            W_f = get_variable("W_f", [self.input_size, self._num_blocks])
            W_o = get_variable("W_o", [self.input_size, self._num_blocks])

            R_z = get_variable("R_z", [self._num_blocks, self._num_blocks])
            R_i = get_variable("R_i", [self._num_blocks, self._num_blocks])
            R_f = get_variable("R_f", [self._num_blocks, self._num_blocks])
            R_o = get_variable("R_o", [self._num_blocks, self._num_blocks])

            b_z = get_variable("b_z", [1, self._num_blocks])
            b_i = get_variable("b_i", [1, self._num_blocks])
            b_f = get_variable("b_f", [1, self._num_blocks])
            b_o = get_variable("b_o", [1, self._num_blocks])

            p_i = get_variable("p_i", [self._num_blocks])
            p_f = get_variable("p_f", [self._num_blocks])
            p_o = get_variable("p_o", [self._num_blocks])

            g = h = tf.tanh

            z = g(tf.matmul(inputs, W_z) + tf.matmul(y_prev, R_z) + b_z)
            i = tf.sigmoid(tf.matmul(inputs, W_i) + tf.matmul(y_prev, R_i) + tf.mul(c_prev, p_i) + b_i)
            f = tf.sigmoid(tf.matmul(inputs, W_f) + tf.matmul(y_prev, R_f) + tf.mul(c_prev, p_f) + b_f)
            c = tf.mul(i, z) + tf.mul(f, c_prev)
            o = tf.sigmoid(tf.matmul(inputs, W_o) + tf.matmul(y_prev, R_o) + tf.mul(c, p_o) + b_o)
            y = tf.mul(h(c), o)

            return y, tf.concat(1, [c, y])

class Model(object):

    def __init__(self):

        self.batch_size= batch_size= 1
        self.num_steps = num_steps = 24
        size = 3

        self.inputs  = tf.placeholder(tf.float32, [batch_size, num_steps, size], name="inputs")
        self.targets = tf.placeholder(tf.float32, [batch_size, 2],               name="targets")

        lstm_cell = LSTMCell(size)
        cell = rnn_cell.MultiRNNCell([lstm_cell] * 2)
        self.initial_state = cell.zero_state(batch_size, tf.float32)

        # initializer used for reusable variable initializer (see `get_variable`)
        initializer = tf.random_uniform_initializer(-0.1, 0.1)

        outputs = []
        states  = []
        state   = self.initial_state

        with tf.variable_scope("RNN", initializer=initializer):
            for time_step in range(num_steps):
                if time_step > 0: tf.get_variable_scope().reuse_variables()

                inputs_slice = self.inputs[:,time_step,:]
                (cell_output, state) = cell(inputs_slice, state)

                outputs.append(cell_output)
                states.append(state)

        self.final_state = states[-1]

        output = tf.reshape(tf.concat(1, outputs), [-1, size*24])
        w = tf.get_variable("softmax_w", [size*24, 2], initializer=initializer)
        b = tf.get_variable("softmax_b", [2],          initializer=initializer)

        logits  = tf.nn.xw_plus_b(output, w, b)
        result  = tf.nn.softmax(logits)

        self.cross_entropy  = 0.5*tf.reduce_sum(-(self.targets) * tf.log(result) - (1-self.targets) * tf.log(1-result), reduction_indices=[1])
        self.train_step     = tf.train.AdamOptimizer(0.001).minimize(self.cross_entropy)
