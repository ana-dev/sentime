from keras.callbacks import Callback


class ValidationCallback(Callback):

    def __init__(self):
        super(ValidationCallback, self).__init__()
        self.epoch_targets = {}
        self.epoch_outputs = {}

    def on_epoch_end(self, epoch, logs={}):
        self.epoch_targets[epoch] = self.validation_data[1].argmax(axis=-1)
        self.epoch_outputs[epoch] = self.model.predict_classes(self.validation_data[0], verbose=0)
        return

