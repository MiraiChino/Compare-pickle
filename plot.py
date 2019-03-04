import argparse

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("log_file", type=str)
    return parser.parse_args()

def save_barplot(filename, **kwargs):
    fig, ax = plt.subplots()
    sns.barplot(**kwargs, ax=ax)
    fig.tight_layout()
    fig.savefig(filename, dpi=300)

if __name__ == "__main__":
    args = parse_args()
    df = pd.read_csv(args.log_file, header=None)
    df = pd.DataFrame({
        "Module": df[3].str.replace(".pkl", ""),
        "Method": df[0].str.replace("_(.*)", "", regex=True),
        "Peak memory (MiB)": df[1].str.replace(" MiB", "").astype(int),
        "Time (sec)": df[2].str.replace(" sec", "").astype(float),
        "File size (MiB)": df[4].str.replace(" MiB", "").astype(int)
    })

    standard = df[df.Module.str.match("(?!.*_).*")]
    fast = df[df.Module.str.match("(?!.*_gen).*_fast")]
    opt = df[df.Module.str.match("(?!.*_gen).*_opt")]
    gen = df[df.Module.str.match(".*_gen$")]
    gen_fast = df[df.Module.str.match(".*_gen_fast$")]
    gen_opt = df[df.Module.str.match(".*_gen_opt$")]
    df_aligned = pd.concat([standard, fast, opt, gen, gen_fast, gen_opt])

    save_barplot("memory_aligned.png", x="Time (sec)", y="Module", data=df_aligned, hue="Method")
    save_barplot("size_aligned.png", x="File size (MiB)", y="Module", data=df_aligned, color=sns.color_palette()[2])
    save_barplot("time_aligned.png", x="Time (sec)", y="Module", data=df_aligned, hue="Method")

    fig, axs = plt.subplots(figsize=(15, 5), ncols=3)
    sns.barplot(x="Time (sec)", y="Module", data=df_aligned, hue="Method", ax=axs[0])
    sns.barplot(x="Peak memory (MiB)", y="Module", data=df_aligned, hue="Method", ax=axs[1])
    sns.barplot(x="File size (MiB)", y="Module", data=df_aligned, color=sns.color_palette()[2], ax=axs[2])
    plt.tight_layout()
    plt.savefig("all_aligned.png", dpi=300)

    df_group = df.groupby("Module").sum()
    time_order = df_group.sort_values("Time (sec)").index
    memory_order = df_group.sort_values("Peak memory (MiB)").index
    filesize_order = df_group.sort_values("File size (MiB)").index
    
    fig, axs = plt.subplots(figsize=(15, 5), ncols=3)
    sns.barplot(x="Time (sec)", y="Module", data=df, order=time_order, hue="Method", ax=axs[0])
    sns.barplot(x="Peak memory (MiB)", y="Module", data=df, order=memory_order, hue="Method", ax=axs[1])
    sns.barplot(x="File size (MiB)", y="Module", data=df, order=filesize_order, color=sns.color_palette()[2], ax=axs[2])
    plt.tight_layout()
    plt.savefig("all_sorted.png", dpi=300)
