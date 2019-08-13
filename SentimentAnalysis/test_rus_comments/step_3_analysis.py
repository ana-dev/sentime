from dataio.database import ResultConnection, get_result_dictionary_from_one_file
from dataio.result import Result
import matplotlib.pyplot as plt
import numpy as np
from visualization import draw_experiment_points

experiment_file = './results_lstm_conv/points.db'
emb_times_file = './results_lstm_conv/emb_times.db'

result = Result(get_result_dictionary_from_one_file(experiment_file, emb_times_file))

lsa_names, lsa_accs, lsa_emb_times = result.get_max_val_acc_to_emb_time(filter_modelname='lsa')
w2v_cbow_names, w2v_cbow_accs, w2v_cbow_emb_times = result.get_max_val_acc_to_emb_time(filter_modelname='w2v_cbow')
w2v_skipgram_names, w2v_skipgram_accs, w2v_skipgram_emb_times = result.get_max_val_acc_to_emb_time(filter_modelname='w2v_skipgram')
glove_cbow_names, glove_cbow_accs, glove_cbow_emb_times = result.get_max_val_acc_to_emb_time(filter_modelname='glove')

draw_experiment_points(
    lsa_accs, lsa_emb_times,
    w2v_cbow_accs, w2v_cbow_emb_times,
    w2v_skipgram_accs, w2v_skipgram_emb_times,
    glove_cbow_accs, glove_cbow_emb_times
)

best_model_names, best_max_val_accs, best_max_val_accs_epochs, best_emb_times, best_word_lens, best_sample_nums, best_metrics = result.get_best_models(5)
fig, ax = plt.subplots(1, 1)
x_c = np.arange(len(best_model_names))
x_metric = [x for x in x_c]
ax.barh(x_metric, width=best_metrics, height=0.8)
ax.set_yticks(np.arange(len(best_model_names)))
ax.set_yticklabels(best_model_names)
ax.invert_yaxis()
ax.set_xlabel('distance to ideal')
plt.show()


model_name, epochs, accs, losses, val_accs, val_losses = result.get_training_process(
    best_model_names[0].split()[0],
    best_sample_nums[0],
    int(best_model_names[0].split()[4]),
    best_word_lens[0],
    13000
)
fig, (ax_val, ax_loss) = plt.subplots(2, 1)
fig.suptitle(model_name)
ax_val.set_title('Accurancy')
ax_val.set_xlabel('epoch')
ax_val.set_ylabel('acc')
ax_val.plot(epochs, accs, linestyle='--', marker='o', color='b', label='train')
ax_val.plot(epochs, val_accs, marker='o', color='b', label='validation')
ax_val.legend(loc='upper left')
ax_loss.set_title('Loss')
ax_loss.set_xlabel('epoch')
ax_loss.set_ylabel('loss')
ax_loss.plot(epochs, losses, linestyle='--', marker='o', color='b', label='train')
ax_loss.plot(epochs, val_losses, marker='o', color='b', label='validation')
ax_loss.legend(loc='lower left')
plt.show()

exit(0)

