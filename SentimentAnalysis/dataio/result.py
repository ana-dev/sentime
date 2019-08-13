from helpers.helpers import min_max_norm
from math import sqrt

def get_experiment_name_without_netinfo(experiment, ignore_emb_name=False, ignore_sample_num=False, ignore_word_len=False, ignore_epoch_num=False):
    result = ''
    if not ignore_emb_name:
        result += '%-12s ' % (experiment['emb_name'],)
    if not ignore_sample_num:
        result += '%-5sdocs ' % (experiment['emb_sample_num'],)
    if not ignore_word_len:
        result += '%-3sdim ' % (experiment['word_len'],)
    if not ignore_epoch_num:
        result += '%-2sepoch ' % (experiment['emb_epoch_num'],)
    return result
    return '%s %sdocs %sdim %sepoch' \
           % (experiment['emb_name'], experiment['emb_sample_num'], experiment['word_len'], experiment['emb_epoch_num'])


class Result:
    def __init__(self, dictionary):
        self.results = dictionary

    def delete_experiments_with_train_count(self, net_train_counts):
        for modelname, experiments in self.results.items():
            self.results[modelname] = \
                [experiment for experiment in experiments if experiment['net_train_count'] not in net_train_counts]

    def get_max_val_acc_to_emb_time(self, filter_modelname = None, filter_sample_num = None, filter_word_len = None, filter_emb_epoch_num = None, sort_by=None):
        model_names = []
        max_val_accs = []
        emb_times = []
        for model_name, experiments in self.results.items():
            if filter_modelname is not None and model_name != filter_modelname:
                continue
            for experiment in experiments:
                exp_name = get_experiment_name_without_netinfo(
                    experiment,
                    ignore_emb_name=filter_modelname is not None,
                    ignore_sample_num=filter_sample_num is not None,
                    ignore_word_len=filter_word_len is not None,
                    ignore_epoch_num=filter_emb_epoch_num is not None
                )
                sample_num = experiment['emb_sample_num']
                word_len = experiment['word_len']
                emb_epoch_num = experiment['emb_epoch_num']
                emb_time = experiment['emb_time']
                max_val_acc = max([point['val_acc'] for point in experiment['points']])
                if filter_sample_num is not None and filter_sample_num != sample_num:
                    continue
                if filter_word_len is not None and filter_word_len != word_len:
                    continue
                if filter_emb_epoch_num is not None and filter_emb_epoch_num != emb_epoch_num:
                    continue
                model_names.append(exp_name)
                max_val_accs.append(max_val_acc)
                emb_times.append(emb_time)
        if sort_by == 'acc':
            lines = [(name, acc, time) for name, acc, time in zip(model_names, max_val_accs, emb_times) ]
            lines = sorted(lines, key=lambda x: x[1], reverse=True)
            model_names = [line[0] for line in lines]
            max_val_accs = [line[1] for line in lines]
            emb_times = [line[2] for line in lines]
        if sort_by == 'emb_time':
            lines = [(name, acc, time) for name, acc, time in zip(model_names, max_val_accs, emb_times)]
            sorted(lines, key=lambda x: x[2])
            model_names = [line[0] for line in lines]
            max_val_accs = [line[1] for line in lines]
            emb_times = [line[2] for line in lines]
        return model_names, max_val_accs, emb_times

    def get_best_models(self, count=10, filter_modelname = None, filter_sample_num = None, filter_word_len = None, filter_emb_epoch_num = None, revert=False):
        model_names = []
        max_val_accs = []
        max_val_ecc_epochs = []
        emb_times = []
        word_lens = []
        sample_nums = []
        for model_name, experiments in self.results.items():
            if filter_modelname is not None and model_name != filter_modelname:
                continue
            for experiment in experiments:
                exp_name = get_experiment_name_without_netinfo(
                    experiment,
                    ignore_emb_name=filter_modelname is not None,
                    ignore_sample_num=filter_sample_num is not None,
                    ignore_word_len=filter_word_len is not None,
                    ignore_epoch_num=filter_emb_epoch_num is not None
                )
                sample_num = experiment['emb_sample_num']
                word_len = experiment['word_len']
                emb_epoch_num = experiment['emb_epoch_num']
                emb_time = experiment['emb_time']
                max_val_acc_epoch, max_val_acc = max([(point['epoch_number'],point['val_acc']) for point in experiment['points']], key=lambda x:x[1])

                if filter_sample_num is not None and filter_sample_num != sample_num:
                    continue
                if filter_word_len is not None and filter_word_len != word_len:
                    continue
                if filter_emb_epoch_num is not None and filter_emb_epoch_num != emb_epoch_num:
                    continue
                model_names.append(exp_name)
                max_val_accs.append(max_val_acc)
                emb_times.append(emb_time)
                word_lens.append(word_len)
                sample_nums.append(sample_num)
                max_val_ecc_epochs.append(max_val_acc_epoch)

        norm_max_val_accs = min_max_norm(max_val_accs)
        ideal_max_val_acc = max(norm_max_val_accs)
        norm_emb_times = min_max_norm(emb_times)
        ideal_emb_time = min(norm_emb_times)
        norm_word_lens = min_max_norm(word_lens)
        ideal_word_len = min(norm_word_lens)
        norm_sample_nums = min_max_norm(sample_nums)
        ideal_sample_num = min(norm_sample_nums)
        norm_max_val_ecc_epochs = min_max_norm(max_val_ecc_epochs)
        ideal_max_val_acc_epoch = min(norm_max_val_ecc_epochs)

        metrics = []
        for max_val_acc, emb_time, word_len, sample_num, max_val_acc_epoch in \
                zip(norm_max_val_accs, norm_emb_times, norm_word_lens, norm_sample_nums, norm_max_val_ecc_epochs):
            metric = sqrt(
                (0.290323 * ideal_max_val_acc - 0.290323 * max_val_acc)**2 +
                (0.290323 * ideal_emb_time - 0.290323 * emb_time)**2 +
                (0.290323 * ideal_max_val_acc_epoch - 0.290323 * max_val_acc_epoch)**2 +
                (0.032258 * ideal_sample_num - 0.032258 * sample_num)**2 +
                (0.096774 * ideal_word_len - 0.096774 * word_len)**2
            )
            metrics.append(metric)

        best_model_names = [] #
        best_max_val_accs = []
        best_max_val_accs_epochs = []
        best_emb_times = []
        best_word_lens = [] #
        best_sample_nums = [] #
        best_metrics = []
        for model_name, max_val_acc, emb_time, word_len, sample_num, max_val_acc_epoch, metric \
            in sorted(zip(model_names, max_val_accs, emb_times, word_lens, sample_nums, max_val_ecc_epochs, metrics), key=lambda x:x[6], reverse=revert):
            if len(best_model_names) >= count:
                break
            best_model_names.append(model_name + '\n' + 'emb_time %.2fs, max_acc %.2f on epoch %s' % (emb_time, max_val_acc, max_val_acc_epoch))
            best_max_val_accs.append(max_val_acc)
            best_emb_times.append(emb_time)
            best_word_lens.append(word_len)
            best_sample_nums.append(sample_num)
            best_max_val_accs_epochs.append(max_val_ecc_epochs)
            best_metrics.append(metric)
        return best_model_names, best_max_val_accs, best_max_val_accs_epochs, best_emb_times, best_word_lens, best_sample_nums, best_metrics

    def get_training_process(self, emb_name, emb_sample_num, emb_epoch_num, word_len, net_train_count):
        for model_name, experiments in self.results.items():
            if model_name != emb_name:
                continue
            for experiment in experiments:
                if experiment['emb_sample_num'] == emb_sample_num and  \
                    experiment['emb_epoch_num'] == emb_epoch_num and \
                    experiment['word_len'] == word_len and \
                    experiment['net_train_count'] == net_train_count:
                    points = experiment['points']
                    epochs = [point['epoch_number'] for point in points]
                    accs = [point['acc'] for point in points]
                    losses = [point['loss'] for point in points]
                    val_accs = [point['val_acc'] for point in points]
                    val_losses = [point['val_loss'] for point in points]
                    return get_experiment_name_without_netinfo(experiment), epochs, accs, losses, val_accs, val_losses
        return None
