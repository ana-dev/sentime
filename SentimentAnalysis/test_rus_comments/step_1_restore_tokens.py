from dataio.csv import read_samples
from tokenizing import tokenize, stem_ru, remove_stop_words, remove_stopwords_from_text
from dataio.database import Connection

neg_samples_tags, tmp = read_samples('./sources/negative.csv', ';', 4, '-1', '1', 3)
tmp, pos_samples_tags = read_samples('./sources/positive.csv', ';', 4, '-1', '1', 3)
tmp = None

neg_samples = [sample for sample, tag in neg_samples_tags]
pos_samples = [sample for sample, tag in pos_samples_tags]
neg_samples = [stem_ru(remove_stop_words(tokenize(remove_stopwords_from_text(line)))) for line in neg_samples]
pos_samples = [stem_ru(remove_stop_words(tokenize(remove_stopwords_from_text(line)))) for line in pos_samples]

conn = Connection("./sources/samples_clear.db")
conn.clear()
conn.save_neg_samples(neg_samples)
conn.save_pos_samples(pos_samples)

exit(0)
