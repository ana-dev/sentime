from keras.callbacks import Callback
import time
from datetime import datetime


class LoggingCallback(Callback):
    def __init__(self):
        Callback.__init__(self)
        self.epoch_acc_dic = {}
        self.epoch_loss_dic = {}
        self.epoch_val_acc_dic = {}
        self.epoch_val_loss_dic = {}
        self.epoch_time_dic = {}
        self.starttime = None

    def on_train_begin(self, logs=None):
        self.starttime = datetime.now()

    def on_epoch_begin(self, epoch, logs=None):
        self.epoch_time_dic[epoch] = time.time()

    def on_epoch_end(self, epoch, logs={}):
        self.epoch_acc_dic[epoch] = logs["acc"]
        self.epoch_loss_dic[epoch] = logs["loss"]
        self.epoch_val_acc_dic[epoch] = logs["val_acc"]
        self.epoch_val_loss_dic[epoch] = logs["val_loss"]
        self.epoch_time_dic[epoch] = int((time.time() - self.epoch_time_dic[epoch])*1000000)

    def save(self, filename):
        with open(filename, mode='w', encoding='utf8') as file:
            for epoch, logs in self.epoch_log_dic.items():
                msg = "Epoch: %i, time: %ss, %s" % (epoch, self.epoch_time_dic[epoch] , ", ".join("%s: %f" % (k, v) for k, v in logs.items()))
                file.write(msg + '\n')
