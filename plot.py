import argparse
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("log_file", type=str)
    parser.add_argument("out_fig", type=str)
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    df = pd.read_csv(args.log_file, header=None)
    df_simple = pd.DataFrame({
        "Module": df[3].str.replace(".pkl", ""),
        "Method": df[0].str.replace("_(.*)", "", regex=True),
        "Peak memory (MiB)": df[1].str.replace(" MiB", "").astype(int),
        "Time (sec)": df[2].str.replace(" sec", "").astype(float),
        "File size (MiB)": df[4].str.replace(" MiB", "").astype(int)
    })
    df_group = df_simple.groupby("Module").sum()
    time_order = df_group.sort_values("Time (sec)").index
    memory_order = df_group.sort_values("Peak memory (MiB)").index
    filesize_order = df_group.sort_values("File size (MiB)").index
    fig, axs = plt.subplots(figsize=(15, 5), ncols=3)

    sns.barplot(x="Time (sec)", y="Module", data=df_simple, order=time_order, hue="Method", ax=axs[0])
    sns.barplot(x="Peak memory (MiB)", y="Module", data=df_simple, order=memory_order, hue="Method", ax=axs[1])
    sns.barplot(x="File size (MiB)", y="Module", data=df_simple, order=filesize_order, color=sns.color_palette()[2], ax=axs[2])
    plt.tight_layout()
    plt.savefig(args.out_fig, dpi=300)

