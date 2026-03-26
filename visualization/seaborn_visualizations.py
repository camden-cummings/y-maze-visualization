import matplotlib.pyplot as plt
import seaborn as sns

## VISUALIZATION
def binned_tet_over_time(df, plot_title, ylim=60, num_of_10m_bins=-1, save_fn="", sep_by_age=True, palette='viridis', legendin=True):
    plt.figure(figsize=(12, 8))

    # Plotting alternation strategy based on genotype
    if sep_by_age:
        sns.lineplot(data=df, x='time_bin', y='alternation_percent', hue='genotype', estimator='mean', errorbar='se', palette=palette)
    else:
        sns.lineplot(data=df, x='time_bin', y='alternation_percent', estimator='mean', errorbar='se', palette=palette)

    plt.xlabel("Time Bin (10-min intervals)")
    plt.ylabel("% LRLR/RLRL Tetragrams")
    #plt.title(plot_title)
    if legendin:
        plt.legend(title='Genotype', loc='upper left')
    else:
        plt.legend(title='Genotype', bbox_to_anchor=(1.05, 1), loc='upper left')

    ax = plt.gca()
    ax.set_xticks(range(num_of_10m_bins))
    ax.set_xticklabels([f'10*{i}' for i in range(num_of_10m_bins)])
    plt.xlim([0, num_of_10m_bins-1])
    plt.ylim([0, ylim])
    plt.hlines([12.5], xmin=0, xmax=6, colors=['r'], linestyles=['--'])

    plt.tight_layout()
    if save_fn != "":
        plt.savefig(save_fn)
        #plt.close()
    else:
        plt.show()

def lineplot(sep_by_age, df, y, palette, divbyline=False):
    if sep_by_age:
        if divbyline:
            sns.lineplot(data=df, x='time_bin', y=y, hue='genotype', style='genotype', estimator='mean', errorbar='se', palette=palette)
        else:
            sns.lineplot(data=df, x='time_bin', y=y, hue='genotype', estimator='mean', errorbar='se', palette=palette)
    else:
        sns.lineplot(data=df, x='time_bin', y=y, estimator='mean', errorbar='se', palette=palette)


def variable_over_time(df, y_var, plot_title, num_of_10m_bins=-1, save_fn="", sep_by_age=True, palette='viridis', legendin=True, legend=True, divbyline=False):
    plt.figure(figsize=(12, 8))

    lineplot(sep_by_age, df, y_var, palette, divbyline)

    if legend:
        if legendin:
            plt.legend(title='Genotype', loc='upper left')
        else:
            plt.legend(title='Genotype', bbox_to_anchor=(1.05, 1), loc='upper left')

    ax = plt.gca()
    ax.set_xticks(range(num_of_10m_bins))
    ax.set_xticklabels([f'10*{i}' for i in range(num_of_10m_bins)])
    plt.xlim([0, num_of_10m_bins-1])
    plt.ylim([0, ylim])

    plt.xlabel("Time Bin (10-min intervals)")
    plt.ylabel(y_var)
    #plt.title(plot_title)

    plt.tight_layout()
    if save_fn != "":
        plt.savefig(save_fn)
        #plt.close()
    else:
        plt.show()


def attr_plot(attrs, palette='viridis'):
    sns.scatterplot(attrs, x='alt_percent', y='age', hue='age', palette=palette)
    plt.show()

    sns.lineplot(attrs, x='time_bin', y='nanpercent_binned', hue='age', estimator='mean', errorbar='se', palette=palette)
    plt.show()
