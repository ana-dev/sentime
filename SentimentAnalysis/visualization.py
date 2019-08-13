import matplotlib.pyplot as plt


def draw_experiment_points_on_ax(ax, title, emb_times, accs, color, marker, time_lim):
    ax.scatter(emb_times, accs, color=color, marker=marker)
    ax.set_title(title)
    ax.set_xlabel('emb_time (seconds)')
    ax.set_ylabel('max_valid_accurancy')
    ax.set_xlim(0, time_lim)
    ax.set_ylim(0, 1)


def draw_experiment_points(lsa_accs, lsa_emb_times, w2v_cbow_accs, w2v_cbow_emb_times, w2v_skipgram_accs,
                           w2v_skipgram_emb_times, glove_cbow_accs, glove_cbow_emb_times):
    fig, ((lsa_ax, w2v_cbow_ax), (glove_ax, w2v_skipgram_ax)) = plt.subplots(2, 2)
    time_lim = max(lsa_emb_times + glove_cbow_emb_times + w2v_skipgram_emb_times + w2v_cbow_emb_times) + 10
    draw_experiment_points_on_ax(lsa_ax, 'LSA', lsa_emb_times, lsa_accs, 'red', '.', time_lim)
    draw_experiment_points_on_ax(w2v_cbow_ax, 'Word2Vec CBOW', w2v_cbow_emb_times, w2v_cbow_accs, 'green', '.',
                                 time_lim)
    draw_experiment_points_on_ax(w2v_skipgram_ax, 'Word2Vec Skip-Gram', w2v_skipgram_emb_times, w2v_skipgram_accs,
                                 'blue', '.', time_lim)
    draw_experiment_points_on_ax(glove_ax, 'GloVe', glove_cbow_emb_times, glove_cbow_accs, 'black', '.', time_lim)
    fig.tight_layout()
    plt.show()
