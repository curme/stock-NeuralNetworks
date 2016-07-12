import numpy as np

class Evaluator:

    def __init__(self):

        print "Info: ", "Create Evaluator"
        self.labelToClass = lambda label: int(sum(np.array(range(1,len(label)+1))*np.array(label))-1)
        self.floatToStr   = lambda f , l: str(f)[:l]

    def eval(self, predict, correct, labels, dataSet = "default"):

        acc = self.accuracy(predict, correct)
        rec = self.recall  (predict, correct)
        pre = self.precise (predict, correct)
        cou = self.counts  (correct)

        print "Info: ", "Evaluate on %s data set" % dataSet
        print "Info: ", "Accuracy:\t%s" % acc
        print "Info: ", "Classes :"+"\t%s"*len(labels) % tuple(labels)
        print "Info: ", "Recall  :"+"\t%s"*len(labels) % tuple(rec)
        print "Info: ", "Precise :"+"\t%s"*len(labels) % tuple(pre)
        print "Info: ", "Counts  :"+"\t%s"*len(labels) % tuple(cou)

        return acc, rec, pre

    def accuracy(self, predict, correct):

        correct_predict = 0
        sample_count    = len(correct)
        if sample_count== 0: return None

        for pitem, citem in zip(predict, correct):
            if list(pitem) == list(citem):
                correct_predict += 1

        return self.floatToStr(correct_predict/float(sample_count), 5)

    def recall(self, predict, correct):

        class_count     = len(correct[0])
        correct_count   = [0] * class_count
        correct_predict = [0] * class_count
        if class_count ==  0: return None

        # statistic
        for pitem, citem in zip(predict, correct):
            correct_class_no = self.labelToClass(citem)
            if correct_class_no < 0 or correct_class_no >= class_count: continue
            correct_count[correct_class_no] += 1
            if list(pitem) == list(citem): correct_predict[correct_class_no] += 1

        # calculate recall
        recalls = []
        for pi, ci in zip(correct_predict, correct_count):
            if ci == 0: recalls.append(None)
            else:       recalls.append(pi/float(ci))

        return self.processResult(recalls)

    def precise(self, predict, correct):

        class_count     = len(correct[0])
        predict_count   = [0] * class_count
        correct_predict = [0] * class_count
        if class_count ==  0: return None

        # statistic
        for pitem, citem in zip(predict, correct):
            predict_class_no = self.labelToClass(pitem)
            if predict_class_no < 0 or predict_class_no >= class_count: continue
            predict_count[predict_class_no] += 1
            if list(pitem) == list(citem): correct_predict[predict_class_no] += 1

        # calculate precise
        precises = []
        for ci, pi in zip(correct_predict, predict_count):
            if pi == 0: precises.append(None)
            else:       precises.append(ci/float(pi))

        return self.processResult(precises)

    def counts(self, correct):

        class_count     = len(correct[0])
        samples_count   = [0]*class_count
        if class_count ==  0: return None

        # statistic
        for citem in correct:
            correct_class_no = self.labelToClass(citem)
            if correct_class_no < 0 or correct_class_no >= class_count: continue
            samples_count[correct_class_no] += 1

        return self.processResult(samples_count)

    def processResult(self, result):

        for index in range(len(result)):
            if not result[index] == None:
                result[index] = self.floatToStr(result[index], 5)

        return result
