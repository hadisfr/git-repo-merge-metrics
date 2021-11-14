#!/usr/bin/env python3

from sys import argv

import pandas as pd
from matplotlib import rcParams, pyplot as plt
import seaborn as sns
rcParams["svg.fonttype"] = "none"
sns.set_theme()

df = pd.read_csv(argv[1])
df.index = pd.to_datetime(df["timestamp"], unit="s", utc=True).dt.tz_convert("Asia/Tehran")
df = df[["touched_files"]].resample("7D").count().rename({"touched_files": "Merges per Week"}, axis=1)
df.index.name = "Date"
# df = df[df.index >= "2019-06"]

print("%d weeks without merge (out of %d weeks)" % (df[df["Merges per Week"] == 0].size, df.size))

plt.figure(figsize=(8, 4.5))
plt.title("Merges Frequency in %s" % argv[1].replace(".csv", ""))
sns.lineplot(data=df, x=df.index, y="Merges per Week", marker="o")
plt.show()
