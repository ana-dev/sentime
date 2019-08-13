from dataio.database import Connection
import corpus.imdb as imdb


(train_samples, train_tags), (test_samples, test_samples) = imdb.get_imdb_corpus()
neg_samples = []
pos_samples = []
for sample, tag in zip(train_samples, train_tags):
    if tag == 1:
        pos_samples.append(sample)
    if tag == 0:
        neg_samples.append(sample)


conn = Connection("./sources/samples_clear_imdb.db")
conn.clear()
conn.save_pos_samples(pos_samples)
conn.save_neg_samples(neg_samples)

exit(0)
