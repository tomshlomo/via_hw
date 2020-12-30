import pandas as pd
import numpy as np


def load(requests_file='requests.csv', durations_file='durations.csv'):
    req = pd.read_csv(requests_file)
    dur_mat = np.genfromtxt(durations_file, delimiter=',')
    dur_mat = dur_mat[1:, 1:]

    req['duration'] = dur_mat[req['pickup'], req['dropoff']]
    req['t_start'] = req['ts'] - req['ts'].min()
    req['t_end'] = req['t_start'] + req['duration']
    return req, dur_mat
