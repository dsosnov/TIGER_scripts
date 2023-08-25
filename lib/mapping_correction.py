# naming from conf_GUI.py:455:    def build_scan_matrix(self):
# option 1V/1X for gemrocs 0-3, 2V/2X for gemrocs 4-10, planari for gemrocs 10-...
import pickle
a = pickle.load(open("mapping.pickle", "rb"))

# 1_V and 1_X
for gr in [0]:
  for t in range(0, 4):
    for ch in range(64):
      a[gr][t][ch] = f'V-{(gr*8+t)*64+ch}'
  for t in range(4, 7):
    for ch in range(64):
      a[gr][t][ch] = f'X-{(gr*8+t)*64+ch}'
  for t in range(7, 8): # Disable non-working tiger
    for ch in range(64):
      a[gr][t][ch] = f'NaS'
for gr in [1]:
  for t in range(0, 8):
    for ch in range(64):
      a[gr][t][ch] = 'NaS'
for gr in range(2, 4):
  for t in range(8):
    for ch in range(64):
      a[gr][t][ch] = 'NaS'

# 2_V and 2_X
for gr in range(4, 11):
  for t in range(8):
    for ch in range(64):
      a[gr][t][ch] = 'NaS'

# other
for gr in range(11, 20):
  for t in range(8):
    for ch in range(64):
      a[gr][t][ch] = 'NaS'

with open('test-2.pickle', 'wb') as f1:
  pickle.dump(a,f1)
