#!/usr/bin/env python3

import pandas as pd
from matplotlib import rcParams, pyplot as plt
import seaborn as sns
rcParams["svg.fonttype"] = "none"
sns.set_theme()


def function(freq, y_axis, start_date, count=True, cummulative=False):
    dfs = {}
    for project in projects:
        df = pd.read_csv("%s.csv" % project)
        df.index = pd.to_datetime(df["timestamp"], unit="s", utc=True).dt.tz_convert("Asia/Tehran")
        df["lines"] = df["added_lines"] + df["removed_lines"]
        df = df[["lines"]].resample(freq)
        if count:
            df = df.count()
        else:
            df = df.sum()
        df = df.rename({"lines": project}, axis=1)
        df.index.name = "Date"
        df = df[df.index >= start_date]
        dfs[project] = df

    merged = dfs[projects[0]]
    for project in projects[1:]:
        merged = merged.merge(dfs[project], left_index=True, right_index=True, how="outer")
    merged = merged.fillna(0).astype(int)
    # print(merged)

    if cummulative:
        for i in range(1, len(projects)):
            merged[projects[i]] += merged[projects[i-1]]
    return merged.reset_index().melt(id_vars="Date", value_name=y_axis, var_name="Project")


projects = []
for count in [True, False]:
    title = "Merges Frequency" if count else "Code Lines Frequency"
    pref = "Merges" if count else "Code Lines"
    for freq, freq_full in [("1M", "Month"), ("7D", "Week")]:
        y_axis = "%s per %s" % (pref, freq_full)

        start_date = "2020-06"
        df = function(freq, y_axis, start_date, count=count, cummulative=False)
        print("Mean")
        print(df.groupby("Project").mean())
        print()
        print("Median")
        print(df.groupby("Project").median())
        print()
        plt.figure()
        plt.title("%s (since %s)" % (title, start_date))
        sns.boxplot(data=df, x="Project", y=y_axis)
        plt.show()

        df = function(freq, y_axis, "2019-06", count=count, cummulative=True)
        fig, ax = plt.subplots(figsize=(10, 4.5))
        plt.title(title)
        ax.fill_between(
            df[df["Project"] == projects[0]]["Date"],
            df[df["Project"] == projects[0]][y_axis],
            alpha=0.5
        )
        for i in range(1, len(projects)):
            ax.fill_between(
                df[df["Project"] == projects[i]]["Date"],
                df[df["Project"] == projects[i]][y_axis],
                df[df["Project"] == projects[i-1]][y_axis],
                alpha=0.5
            )
        sns.lineplot(data=df, x="Date", y=y_axis, hue="Project", marker=".", ax=ax)
        plt.show()
