from dataio.database import Connection, ResultConnection, EmbTimeConnection
from embeddings.word2vec_embedding import Word2VecEmbedding
from embeddings.lsa_embedding import LSAEmbedding
from embeddings.glove_embedding import GloveEmbedding
from network.lstm_categorical_new import LSTMCategorical
from network.pure_lstm import PureLSTM
from dataio.csv import save_embedding_dictionary, save_word_to_index
from helpers.helpers import shuffle_and_get_parts, get_emb_dic_filename, get_emb_w2i_filename
import os.path as path
import random

random.seed(7)

# не забыть переименовать эксперименты
conn = Connection("./sources/samples_clear.db")
samples = [(sample, 0) for sample in conn.get_neg_samples()] + [(sample, 1) for sample in conn.get_pos_samples()]
samples_tokens = [sample for sample, tag in samples]
samples_tags = [tag for sample, tag in samples]

emb_names = ['w2v_cbow', 'w2v_skipgram', 'glove', 'lsa']
sample_nums = [25000, 10000, 1000]  # [25000, 19000, 14000, 10000, 5000, 3000, 1000]
word_lens = [300, 150, 50]  # [500, 300, 150, 50, 10]
emb_epochs = [15, 8, 2]  # [15, 13, 11, 9, 7, 5, 3, 1]
train_test_counts = [[13000, 3250]]  # [[20000, 5000], [13000, 5000], [7000, 5000], [4000, 5000], [1000, 5000]]
embeddings_dir = './results_lstm_conv/embeddings/'
results_file = './results_lstm_conv/points.db'
embeddings_time_file = './results_lstm_conv/emb_times.db'

doc_len = max([len(tokens) for tokens in samples_tokens])
lstm_out = 100
batch_size = 32
net_epochs = 10


for sample_num in sample_nums:
    random_emd_samples_part = shuffle_and_get_parts(samples_tokens, samples_tags, [sample_num])[0]
    emb_samples_tokens = random_emd_samples_part[0]
    for word_len in word_lens:
        for emb_epoch in emb_epochs:
            for emb_name in emb_names:
                emb_dic_file = embeddings_dir + get_emb_dic_filename(emb_name, sample_num, word_len, emb_epoch)
                emb_w2i_file = embeddings_dir + get_emb_w2i_filename(emb_name, sample_num, word_len, emb_epoch)
                generated = path.isfile(emb_dic_file) and path.isfile(emb_w2i_file)

                if emb_name == 'lsa' and generated:
                    embedding_model = LSAEmbedding(emb_dic_file, emb_w2i_file, None, doc_len, None, None)
                elif emb_name == 'lsa':
                    embedding_model = LSAEmbedding(None, None, emb_samples_tokens, doc_len, word_len, emb_epoch)
                if emb_name == 'w2v_cbow' and generated:
                    embedding_model = Word2VecEmbedding(emb_dic_file, emb_w2i_file, None, doc_len, None, None, True)
                elif emb_name == 'w2v_cbow':
                    embedding_model = Word2VecEmbedding(None, None, emb_samples_tokens, doc_len, word_len, emb_epoch, True)
                if emb_name == 'w2v_skipgram' and generated:
                    embedding_model = Word2VecEmbedding(emb_dic_file, emb_w2i_file, None, doc_len, None, None, False)
                elif emb_name == 'w2v_skipgram':
                    embedding_model = Word2VecEmbedding(None, None, emb_samples_tokens, doc_len, word_len, emb_epoch, False)
                if emb_name == 'glove' and generated:
                    embedding_model = GloveEmbedding(emb_dic_file, emb_w2i_file, None, doc_len, None, None)
                elif emb_name == 'glove':
                    embedding_model = GloveEmbedding(None, None, emb_samples_tokens, doc_len, word_len, emb_epoch)

                embedding_matrix = embedding_model.embedding_matrix
                embedding_dictionary = embedding_model.embedding_dictionary
                word_to_index = embedding_model.word_to_index


                if not generated:
                    save_embedding_dictionary(emb_dic_file, embedding_dictionary)
                    save_word_to_index(emb_w2i_file, word_to_index)
                    emb_time = embedding_model.time
                    emb_time_conn = EmbTimeConnection(embeddings_time_file)\
                        .save_time(emb_name, sample_num, word_len, emb_epoch, emb_time)

                emb_time = 0.
                for [train_count, test_count] in train_test_counts:
                    [train_set, test_set] = shuffle_and_get_parts(samples_tokens, samples_tags, [train_count, test_count])
                    train_samples_tokens = train_set[0]
                    train_samples_tags = train_set[1]
                    test_samples_tokens = test_set[0]
                    test_samples_tags = test_set[1]

                    train_sequences = embedding_model.get_docs_sequences(train_samples_tokens)
                    test_sequences = embedding_model.get_docs_sequences(test_samples_tokens)

                    # net = PureLSTM(lstm_out, doc_len, embedding_matrix = embedding_matrix)
                    net = LSTMCategorical(lstm_out, doc_len, embedding_matrix=embedding_matrix)
                    sequences = net.train_by_sequences(train_sequences, train_samples_tags, test_sequences,
                                                       test_samples_tags, batch_size=batch_size, epochs=net_epochs)

                    conn = ResultConnection(results_file)
                    exp_id = conn.save_experiment(net.epochLogger.starttime, sample_num, len(word_to_index), emb_epoch, emb_time, word_len,
                                         doc_len, len(word_to_index), lstm_out, net.dropout, train_count, test_count, emb_name)
                    conn.save_points(exp_id, net.epochLogger)
exit(0)
