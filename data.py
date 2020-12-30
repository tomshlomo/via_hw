import pandas as pd
import numpy as np


req = pd.read_csv('requests.csv')
dur = pd.read_csv('durations.csv')
# dur_mat = np.loadtxt('durations.csv', delimiter=',', skiprows=1)
dur_mat = np.genfromtxt('durations.csv', delimiter=',')
dur_mat = dur_mat[1:, 1:]


req['duration'] = dur_mat[req['pickup'], req['dropoff']]
req['t_start'] = req['ts'] - req['ts'].min()
req['t_end'] = req['t_start'] + req['duration']

pass