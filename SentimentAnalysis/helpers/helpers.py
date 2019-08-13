from random import shuffle
import numpy as np


def min_max_norm(x):
    min_x = min(x)
    max_x = max(x)
    return [(xi-min_x)/(max_x-min_x) for xi in x]


def split_by_groups(tagged_list, get_tag_function, get_item_function=None):
    grouped = {}
    for item in tagged_list:
        item_tag = get_tag_function(item)
        item_item = get_item_function(item)
        if item_tag not in grouped:
            grouped[item_tag] = [item_item]
        else:
            grouped[item_tag].append(item_item)
    return grouped


def shuffle_and_get_parts(samples, tags, parts=None):
    samples_tags = [(sample, tag) for sample, tag in zip(samples, tags)]
    shuffle(samples_tags)

    # half of pos and neg
    if parts is None:
        parts = [int(len(samples)/2)]
    else:
        parts = [int(part/2) for part in parts]

    # for each part neg and pos sets with samples and tags
    parts_sets = [[[[], []], [[], []]] for part in parts]

    neg_part_i = 0
    pos_part_i = 0
    for i, (sample, tag) in enumerate(samples_tags):
        if tag == 0 and neg_part_i < len(parts):
            if len(parts_sets[neg_part_i][0][0]) >= parts[neg_part_i]:
                neg_part_i += 1
            if neg_part_i >= len(parts):
                continue
            parts_sets[neg_part_i][0][0].append(sample)
            parts_sets[neg_part_i][0][1].append(tag)
        elif tag == 1 and pos_part_i < len(parts):
            if len(parts_sets[pos_part_i][1][0]) >= parts[pos_part_i]:
                pos_part_i += 1
            if pos_part_i >= len(parts):
                continue
            parts_sets[pos_part_i][1][0].append(sample)
            parts_sets[pos_part_i][1][1].append(tag)

    for i in range(0, len(parts_sets)):
        part_set = parts_sets[i]
        min_count = min(len(part_set[0][0]), len(part_set[1][0]))
        tmp = (
            part_set[0][0][0:min_count] + part_set[1][0][0:min_count],
            part_set[0][1][0:min_count] + part_set[1][1][0:min_count]
        )
        samples_tags = [(sample, tag) for sample, tag in zip(tmp[0], tmp[1])]
        shuffle(samples_tags)
        parts_sets[i] = [[sample for sample, tag in samples_tags], [tag for sample, tag in samples_tags]]

    return parts_sets


def get_embedding_matrix_by_dictionary(embedding_dictionary, word_to_index):
    embedding_dim = len(embedding_dictionary.values()[0])
    embedding_matrix = np.zeros((len(word_to_index) + 1, embedding_dim))
    for word, i in word_to_index.items():
        embedding_vector = embedding_dictionary.get(word, None)
        if embedding_vector is not None:
            # words not found in embedding index will be all-zeros.
            embedding_matrix[i] = embedding_vector
    return embedding_matrix


def get_emb_dic_filename(emb_name, sample_num, word_len, emb_epoch):
    return '%s_dic_samples%s_dim%s_epo%s.txt' % (emb_name, sample_num, word_len, emb_epoch)


def get_emb_w2i_filename(emb_name, sample_num, word_len, emb_epoch):
    return '%s_w2i_samples%s_dim%s_epo%s.txt' % (emb_name, sample_num, word_len, emb_epoch)
