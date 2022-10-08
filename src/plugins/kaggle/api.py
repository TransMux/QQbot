from kaggle.api.kaggle_api_extended import KaggleApi
import time
import os
import zipfile
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

api = KaggleApi()
api.authenticate()

competition = "feedback-prize-english-language-learning"

async def 获取Leaderboard():
    api.competition_leaderboard_download(competition, ".")
    # unzip
    with zipfile.ZipFile(competition + ".zip", "r") as zip_ref:
        zip_ref.extractall(".")

    today_file_name = time.strftime("%Y-%m-%d") + ".csv"
    os.rename(competition + "-publicleaderboard.csv", today_file_name)


def 保存今天和昨天的分数计数汇总():
    today_file_name = time.strftime("%Y-%m-%d") + ".csv"
    today = pd.read_csv(today_file_name)
    today = today["Score"].value_counts()
    today = pd.DataFrame(today).reset_index()
    today.insert(0, "date", "today")

    all_df = [today]

    try:
        yesterday_file_name = time.strftime("%Y-%m-%d", time.localtime(time.time() - 86400)) + ".csv"
        yesterday = pd.read_csv(yesterday_file_name)
        yesterday = yesterday["Score"].value_counts()
        yesterday = pd.DataFrame(yesterday).reset_index()
        yesterday.insert(0, "date", "yesterday")
        all_df.append(yesterday)
    except:
        pass

    # concat
    df = pd.concat(all_df, ignore_index=True)

    sns.set(style="whitegrid")

    g = sns.catplot(
        data=df[df["index"] < 0.6], kind="bar",
        x="index", y="Score", hue="date",
        ci="sd", palette="dark", alpha=.6, height=15
    )

    for p in g.ax.patches:
        g.ax.annotate(
            format(p.get_height(), '.0f'),
            (p.get_x() + p.get_width() / 2., p.get_height()),
            ha = 'center', va = 'center',
            xytext = (0, 9), textcoords = 'offset points'
        )

    g.despine(left=True)
    g.set_axis_labels("Score", "Count")
    g.legend.set_title("Date")
    title = competition + " " + time.strftime("%Y-%m-%d")
    g.fig.suptitle(title, fontsize=20)
    plt.savefig(title + ".png")