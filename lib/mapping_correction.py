import pickle
a = pickle.load(open("mapping.pickle", "rb"))

for gr in [0]:
  for t in [0, 1]:
    for ch in range(64):
      a[gr][t][ch] = f'V-{(gr*8+t)*64+ch}'
  for t in range(2, 8):
    for ch in range(64):
      a[gr][t][ch] = 'NaS'
for gr in [1]:
  for t in range(8):
    for ch in range(64):
      a[gr][t][ch] = f'V-{(gr*8+t)*64+ch}'
for gr in range(2, 20):
  for t in range(8):
    for ch in range(64):
      a[gr][t][ch] = 'NaS'

with open('test-2.pickle', 'wb') as f1:
  pickle.dump(a,f1)
