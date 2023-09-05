from collections import Counter

import pandas as pd


row1 = Counter({64: 2, 65: 2, 66: 2, 67: 2, 68: 2, 61: 1, 69: 1, 60: 1, 62: 1, 63: 1})



print(row1)

df = pd.DataFrame(index=range(1, 256))


df.loc[:, 5] = row1


for row in df.values:
    print(row)


df.to_excel('map.xlsx')