import numpy as np


def read_texts_from_file(file, quoted_fields=True, separator=",", text_col=1):
    with open(file, "r", encoding="utf-8", errors="ignore") as filestream:
        return read_texts_from_filestream(filestream, quoted_fields, separator, text_col);


def read_texts_from_filestream(file, quoted_fields=True, separator=",", text_col=1):
    texts = []
    for line in file:
        new_line = line[1:-2] if quoted_fields else line
        values = new_line.split('"' + separator + '"') if quoted_fields else new_line.split(separator)
        text = values[text_col-1]
        texts.append(text)
    return texts


def read_samples(filename, delimeter, tag_col, neg_tag, pos_tag, text_col, pos_count=20000, neg_count=20000):
    pos_samples = []
    neg_samples = []

    with open(filename, 'r', encoding='UTF-8', errors='ignore') as f:
        i = 0
        try:
            for line in f:
                if len(pos_samples) >= pos_count and len(neg_samples) >= neg_count:
                    break
                values = line[1:-2].split('"' + delimeter + '"')
                tag = {
                    neg_tag: -1,
                    pos_tag: 1
                }[values[tag_col]] if values[tag_col] == neg_tag or values[tag_col] == pos_tag else None
                if tag is None: continue
                text = values[text_col]
                if tag == -1 and len(neg_samples) < neg_count:
                    neg_samples.append((text, tag))
                if tag == 1 and len(pos_samples) < pos_count:
                    pos_samples.append((text, tag))
                i = i + 1
        except:
            a = 1
    return neg_samples, pos_samples


def save_embedding_matrix(file_name, embedding_matrix, delimeter='\t'):
    with open(file_name, mode='w', encoding='utf8') as f:
        for i, vector in enumerate(embedding_matrix):
            f.write(str(i) + delimeter + delimeter.join([str(val) for val in vector]) + '\n')


def read_embedding_matrix(file_name, delimeter='\t'):
    embedding_matrix = []
    with open(file_name, mode='r', encoding='utf8') as f:
        for line in f:
            values = line.split(delimeter)
            i = int(values[0])
            coefs = np.asarray(values[1:], dtype='float32')
            embedding_matrix.append(coefs)
    return np.asarray(embedding_matrix), len(coefs)


def save_embedding_dictionary(file_name, embedding_dictionary, delimeter='\t'):
    with open(file_name, mode='w', encoding='utf8') as f:
        for word, vector in embedding_dictionary.items():
            f.write(word + delimeter + delimeter.join([str(val) for val in vector]) + '\n')


def read_embedding_dictionary(file_name, delimeter='\t'):
    embedding_dictionary = {}
    with open(file_name, mode='r', encoding='utf8') as f:
        for line in f:
            values = line.split(delimeter)
            word = values[0]
            coefs = np.asarray(values[1:], dtype='float32')
            embedding_dictionary[word] = coefs
    return embedding_dictionary, len(coefs)


def save_word_to_index(file_name, word_to_index, delimeter='\t'):
    with open(file_name, mode='w', encoding='utf8') as f:
        for word, i in word_to_index.items():
            f.write(str(i) + delimeter + word + '\n')


def read_word_to_index(file_name, delimeter='\t'):
    word_to_index = {}
    with open(file_name, mode='r', encoding='utf8') as f:
        for line in f:
            values = line.split(delimeter)
            i = int(values[0])
            word = values[1][:-1]
            word_to_index[word] = i
    return word_to_index




