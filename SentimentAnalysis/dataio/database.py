import sqlite3
import re
from datetime import datetime


def get_result_dictionary_from_one_file(filename, times_filename):
    times = EmbTimeConnection(times_filename).get_times()
    dic = {}
    conn = ResultConnection(filename)
    experiments = conn.get_experiments_with_point()

    for experiment in experiments:
        name = experiment['emb_name']
        experiment['emb_time'] = \
            times[(name, experiment['emb_sample_num'], experiment['word_len'], experiment['emb_epoch_num'])] \
            if (name, experiment['emb_sample_num'], experiment['word_len'], experiment['emb_epoch_num']) in times \
            else 0.
        if  name in dic:
            dic[name].append(experiment)
        else:
            dic[name] = [experiment]
    return dic


def get_result_dictionary(filename_name, times_filename):
    times = EmbTimeConnection(times_filename).get_times()
    dic = {}
    for filename, name in filename_name.items():
        conn = ResultConnection(filename)
        dic[name] = conn.get_experiments_with_point(name)
        for experiment in dic[name]:
            experiment['emb_time'] = \
                times[(name, experiment['emb_sample_num'], experiment['word_len'], experiment['emb_epoch_num'])] \
                if (name, experiment['emb_sample_num'], experiment['word_len'], experiment['emb_epoch_num']) in times \
                else 0.
    return dic


class EmbTimeConnection:
    def __init__(self, filename):
        self.conn = sqlite3.connect(filename)

    def save_time(self, emb_name, emb_sample_num, word_len, emb_epoch_num, emb_time):
        cursor = self.conn.cursor()
        command = '''
            INSERT INTO times (emb_name, emb_sample_num, word_len, emb_epoch_num, emb_time)
            VALUES (?, ?, ?, ?, ?)
        '''
        cursor.execute(command, (emb_name, emb_sample_num, word_len, emb_epoch_num, emb_time))
        self.conn.commit()

    def get_times(self):
        cursor = self.conn.cursor()
        command = '''
            SELECT 
                id, 
                emb_name,
                emb_sample_num,
                word_len,
                emb_epoch_num,
                avg(emb_time)
             FROM times
             GROUP BY emb_name, emb_sample_num, word_len, emb_epoch_num
        '''
        cursor.execute(command)
        rows = cursor.fetchall()
        return {
            (row[1], row[2], row[3], row[4]): row[5]
            for row in rows
        }

    def __del__(self):
        self.conn.close()


class ResultConnection:
    def __init__(self, filename):
        self.conn = sqlite3.connect(filename)

    def get_experiments(self, rename_emd=None):
        cursor = self.conn.cursor()
        command = '''
            SELECT 
                id, 
                datetime, 
                emb_sample_num,
                emb_word_num,
                emb_epoch_num,
                word_len,
                net_doc_len,
                net_word_num,
                net_lstm_out,
                net_drop_persent,
                net_train_count,
                net_test_count,
                emb_name,
                emb_time
            FROM experiment
        '''
        cursor.execute(command)
        rows = cursor.fetchall()
        return {
            row[0]: {
                    'id': int(row[0]),
                    'emb_name': rename_emd if rename_emd is not None else row[12],
                    'emb_time': row[13] if row[13] is not None else None,
                    'net_test_count': int(row[11]) if row[11] is not None else None,
                    'net_train_count': int(row[10]) if row[10] is not None else None,
                    'net_drop_persent': float(row[9]) if row[9] is not None else None,
                    'net_lstm_out': int(row[8]) if row[8] is not None else None,
                    'net_word_num': int(row[7]) if row[7] is not None else None,
                    'net_doc_len': int(row[6]) if row[6] is not None else None,
                    'word_len': int(row[5]) if row[5] is not None else None,
                    'emb_epoch_num': int(row[4]) if row[4] is not None else None,
                    'emb_word_num': int(row[3]) if row[3] is not None else None,
                    'emb_sample_num': int(row[2]) if row[2] is not None else None,
                    'datetime': datetime.strptime(row[1], '%d/%m/%y %H:%M:%S.%f'),
                    'points': []
            }
            for row in rows
        }

    def get_points(self):
        cursor = self.conn.cursor()
        command = '''
            SELECT 
                id, 
                experiment_id,
                epoch_number,
                seconds,
                acc,
                val_acc,
                loss,
                val_loss,
                realneg_predneg,
                realneg_predpos,
                realpos_predpos,
                realpos_predneg
             FROM epoch_value
        '''
        cursor.execute(command)
        rows = cursor.fetchall()
        return [
            {
                'id': row[0],
                'experiment_id': row[1],
                'epoch_number': row[2],
                'seconds': row[3],
                'acc': row[4],
                'val_acc': row[5],
                'loss': row[6],
                'val_loss': row[7],
                'realneg_predneg': row[8],
                'realneg_predpos': row[9],
                'reaspos_predpos': row[10],
                'realpos_predneg': row[11]
            }
            for row in rows
        ]

    def get_experiments_with_point(self, rename_emd=None):
        experiments = self.get_experiments(rename_emd)
        points = self.get_points()
        for point in points:
            experiment_id = point['experiment_id']
            experiment = experiments[experiment_id]
            experiment['points'].append(point)
        return [experiment for experiment_id, experiment in experiments.items()]

    def save_experiment(self, datetime,
                        emb_sample_num,
                        emb_word_num,
                        emb_epoch_num,
                        emb_time,
                        word_len,
                        net_doc_len,
                        net_word_num,
                        net_lstm_out,
                        net_drop_persent,
                        net_train_count,
                        net_test_count,
                        emb_name):
        db_formated = (
                datetime.strftime('%d/%m/%y %H:%M:%S.%f'),
                emb_sample_num,
                emb_word_num,
                emb_epoch_num,
                word_len,
                net_doc_len,
                net_word_num,
                net_lstm_out,
                net_drop_persent,
                net_train_count,
                net_test_count,
                emb_name,
                emb_time
            )

        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO experiment 
            (
                datetime, 
                emb_sample_num, 
                emb_word_num, 
                emb_epoch_num, 
                word_len, 
                net_doc_len, 
                net_word_num, 
                net_lstm_out, 
                net_drop_persent,
                net_train_count,
                net_test_count,
                emb_name,
                emb_time
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', db_formated)
        self.conn.commit()
        return cursor.lastrowid

    def save_points(self, experiment_id, log_callback):
        db_formated = [
            (
                experiment_id,
                epoch,
                log_callback.epoch_time_dic[epoch],
                log['acc'],
                log['val_acc'],
                log['loss'],
                log['val_loss'],
                None,
                None,
                None,
                None
            )
            for epoch, log in log_callback.epoch_log_dic.items()
        ]
        cursor = self.conn.cursor()
        cursor.executemany('''
            INSERT INTO epoch_value 
            (
                experiment_id,
                epoch_number,
                seconds,
                acc,
                val_acc,
                loss,
                val_loss,
                realneg_predneg,
                realneg_predpos,
                realpos_predpos,
                realpos_predneg
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', db_formated)
        self.conn.commit()

    def __del__(self):
        self.conn.close()


class Connection:
    def __init__(self, filename):
        self.conn = sqlite3.connect(filename)

    def save_samples(self, table, samples):
        db_formated_samples = (
            ('\t'.join([re.sub(r"\s+", ' ', token) for token in tokens]),)
            for tokens in samples
        )
        cursor = self.conn.cursor()
        cursor.executemany('''
            INSERT INTO {0} (info) 
            VALUES (?)
        '''.format(table), db_formated_samples)
        self.conn.commit()

    def save_neg_samples(self, samples):
        self.save_samples("neg_samples", samples)

    def save_pos_samples(self, samples):
        self.save_samples("pos_samples", samples)

    def get_samples(self, table, count=None):
        cursor = self.conn.cursor()
        last_id = 0
        received = 0
        while True:
            command = '''
                SELECT id, info
                FROM %s
                WHERE id > %s
                ORDER BY id
                LIMIT 1000
            ''' % (table, last_id)
            cursor.execute(command)
            rows_returned = False
            while True:
                if count is not None and received >= count:
                    break
                row = cursor.fetchone()
                if row:
                    rows_returned = True
                    last_id = row[0]
                    yield row[1].split('\t')
                    received = received + 1
                else:
                    break
            if not rows_returned:
                break

    def get_neg_samples(self, count=None):
        return self.get_samples("neg_samples", count)

    def get_pos_samples(self, count=None):
        return self.get_samples("pos_samples", count)

    def clear(self):
        cursor = self.conn.cursor()
        cursor.executescript('''
            DELETE FROM neg_samples;
            DELETE FROM pos_samples;
        ''')
        self.conn.commit()

    def create(self):
        cursor = self.conn.cursor()
        cursor.executescript('''
            CREATE TABLE "neg_samples" ( 
                `id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, 
                `info` TEXT NOT NULL 
            );
            CREATE TABLE "pos_samples" ( 
                `id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, 
                `info` TEXT NOT NULL 
            );
        ''')
        self.conn.commit()

    def __del__(self):
        self.conn.close()
