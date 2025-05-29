"""Visualizes."""
import re
from collections import Counter

import pandas as pd
from matplotlib import pyplot as plt
import numpy as np

import seaborn as sns

class Visualization:
    """Visualizes."""

    def __init__(self, labels, all_16_labels, number_of_divisions, age_list, cmap_name):
        self.labels = labels
        self.all_16_labels = all_16_labels
        self.NUMBER_OF_DIVISIONS = number_of_divisions
        self.colours = self.defn_colours(age_list, cmap_name)

    def defn_colours(self, strs_to_be_given_colours: list[str], cmap_name: str) -> dict:
        """Take in a list of keys, and defines a colour for each of them."""
        cmap = plt.get_cmap(cmap_name)

        if len(strs_to_be_given_colours) > 0:
            colours = {}
            rescaled_colours = self.rescale([int(re.findall(r'[1-9]+', n)[0])
                                             for n in strs_to_be_given_colours])
    
            num_of_colours = len(strs_to_be_given_colours)
            for c in range(num_of_colours):
                colours[strs_to_be_given_colours[c]] = cmap(rescaled_colours[num_of_colours - 1 - c])
        else:
            colours = cmap(0)
        return colours

    @staticmethod
    def rescale(y):
        """Scales the given number."""
        return (y - np.min(y)) / (np.max(y) - np.min(y))

    @staticmethod
    def generate_colour_varns(num_of_colours: int, colour: tuple[int, int, int, int]) -> list:
        """Create an array of colours in (R, G, B) format which are lighter \
            (tints) and darker (shades) than the given colour."""
        colour_list = []

        shade = tuple(min((c + (1-c) * 0.2), 1) for c in colour[:-1])
        for j in range(int(num_of_colours/2)):
            shade = tuple(min((s + (1-s) * 0.2), 1) for s in shade)
            colour_list.append(shade)

        colour_list.reverse()
        colour_list.append(colour[:-1])

        tint = tuple(c * 0.9 for c in colour[:-1])
        for i in range(int(num_of_colours/2)):
            tint = tuple(t * 0.9 for t in tint)
            colour_list.append(tint)

        if num_of_colours % 2 == 0:
            colour_list = colour_list[:-1]
        return colour_list

    def paired_tetragram(self, percent, age):
        """Paired tetragram graph."""
        x_ticks = range(len(self.labels))

        _, ax = plt.subplots()

        plt.xlabel("% of Total")
        plt.ylabel("Paired Tetragram")
        plt.title('Frequency of Paired Tetragram - ' + age)

        plt.yticks(ha='right', ticks=x_ticks, labels=self.labels)
        plt.xlim((0, 100))

        for i, label in enumerate(percent):
            ax.text(percent[i] + 2, x_ticks[i] - 0.1, label)

        plt.plot(percent, x_ticks, marker='o')
        plt.show()

    def indiv_bar_graph(self, percent, filepath, row, col, age=None, num_of_tetragrams=None):
        """Individual bar graph."""
        _, ax = plt.subplots(layout='constrained', figsize=(9, 3))

        ax.set_ylabel("% of Total")
        ax.set_xlabel("Paired Tetragram")
        
        ex = f"({row}, {col})"

        if age is not None:
            ex += f", {age}dpf"
        
        if num_of_tetragrams is not None:
            ex += f", sample size of {num_of_tetragrams} tetragrams"
            
        ax.set_title('Frequency of Paired Tetragram - ' + ex)
            
        ax.set_xticks(np.arange(0, len(self.labels)),
                      self.labels, rotation=30, ha='right')


        ax.bar(np.arange(0, len(self.labels)), percent, 0.1)

        # plt.show() # uncomment to show as program is run
        plt.savefig(filepath)
        plt.close()

    def paired_tetragram_bar(self, turn_maps: dict, sample_size: dict):
        """Paired tetragram bar graph."""
        mod_turn_maps = {}

        for turn_map in turn_maps.items():
            counter = Counter(turn_map[1])

            percent = []
            for label in self.all_16_labels:
                percent.append(100 * counter[label] / sum(counter.values()))

            mod_turn_maps[turn_map[0]] = percent

        width = 0.1  # the width of the bars
        multiplier = 0

        _, ax = plt.subplots(layout='constrained', figsize=(17, 3))

        for attribute, measurement in mod_turn_maps.items():
            offset = width * multiplier
            adj = -0.1 * (float(len(turn_maps))/2)

            ax.bar(np.arange(adj, len(self.all_16_labels)+adj) + offset,
                   measurement,  width,
                   label=attribute + f" (n = {sample_size[attribute]})",
                   color=self.colours[attribute])

            multiplier += 1

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_xlabel("Paired Tetragram")
        ax.set_ylabel("% of Total")
        ax.set_title('Frequency of Paired Tetragram')
        ax.set_xticks(np.arange(0, len(self.all_16_labels)),
                      self.all_16_labels, rotation=30, ha='right')

        ax.legend(loc='upper left')
        ax.set_ylim(0, 40)
        plt.show()

    def indiv_fish_plot(self, percents: dict):
        """Create a plot of an individual fish."""
        x_ticks = range(len(self.labels))

        _, ax = plt.subplots(layout="constrained")

        ages = list(percents.keys())

        plt.xlabel("% of Total")
        plt.ylabel("Paired Tetragram")

        if len(ages) == 1:
            plt.title(f'Frequency of Paired Tetragram for {ages[0]}')
        else:
            plt.title('Frequency of Paired Tetragram')

        plt.yticks(ha='right', ticks=x_ticks, labels=self.labels)
        plt.xlim((0, 100))

        for age_name in percents:
            if len(percents[age_name]) > 0:
                start = True
                for percent in percents[age_name]:
                    if start:
                        plt.plot(percent, x_ticks, marker='o',
                                 color=self.colours[age_name], label=age_name)
                        start = False
                    else:
                        plt.plot(percent, x_ticks, marker='o',
                                 color=self.colours[age_name])

        ax.legend(loc='lower right')

        plt.show()

    def indiv_heatmap(self, percent: list):
        """Create a heatmap representing fish as individual datapoints."""
        percent = sorted(percent, key=lambda v: v[6])

        p = np.transpose(np.array(percent))

        _, ax = plt.subplots()

        ax.imshow(p)
        ax.set_xlabel("Fish 0 through {}".format(len(p[0]) - 1))

        # Show all ticks and label them with the respective list entries
        plt.xticks(ticks=np.arange(len(p[0])))
        plt.yticks(ticks=np.arange(len(self.labels)), labels=self.labels)

        # for i in range(len(labels)):
        #    for j in range(len(p[0])):
        #        text = ax.text(j, i, round(p[i, j],1), ha="center", va="center", color="w")

        plt.show()

    def sb_indiv_plot(self, percents: dict):
        """Create a scatter plot representing fish as individual datapoints."""
        _, ax = plt.subplots(figsize=(len(percents), len(percents)))

        df_form_percents = {}

        for age_name in percents:
            s_percents = [p[6] for p in percents[age_name]]
            df_form_percents[age_name] = s_percents

        df = pd.DataFrame.from_dict(df_form_percents, orient='index')
        df = df.transpose()
        df.to_csv('data.csv')

        sns.violinplot(data=df, ax=ax, orient='h', inner="point",
                       inner_kws={"norm": "linear"}, palette=self.colours)

        """
        for age_name in percents:
            if len(percents[age_name]) > 0:
                start = True

                # print(percents[age_name])
                s_percent = sorted([p[6] for p in percents[age_name]])
                print("PERCENT: ", s_percent)
                # print(s_percent)
                x_ticks = self.rescale(range(len(s_percent)))

                if start:
                    print(len(s_percent), len(x_ticks))
                    sns.violinplot(data = s_percent, ax = ax, orient = 'h')
                    start = False
                else:
                    sns.violinplot(data = s_percent, ax = ax, orient = 'h')
        """
        ax.legend(loc='upper left')

        plt.show()

    def scatter_indiv_plot(self, percents: dict):
        """Create a scatter plot representing fish as individual datapoints."""
        _, ax = plt.subplots()
        # print(percents)
        for age_name in percents:
            if len(percents[age_name]) > 0:
                start = True

                s_percent = sorted([p[6] for p in percents[age_name]])
                x_ticks = self.rescale(range(len(s_percent)))

                if start:
                    plt.plot(x_ticks, s_percent, marker='o',
                             color=self.colours[age_name], label=age_name,
                             ls="", markersize=4)
                    start = False
                else:
                    plt.plot(x_ticks, s_percent, marker='o',
                             color=self.colours[age_name], ls="", markersize=4)
        ax.legend(loc='upper left')

        plt.show()

    def video_specific_graph(self, per, age):
        """Create a bar graph for the individual fish within one video."""
        _, ax = plt.subplots()

        width = 0.05  # the width of the bars
        multiplier = 0

        _, ax = plt.subplots(layout='constrained', figsize=(9, 3))

        for attribute, measurement in per.items():
            offset = width * multiplier
            adj = -0.1 * (float(len(per))/4)

            ax.bar(np.arange(adj, len(self.labels)+adj) + offset, measurement,
                   width, label=attribute[25:], color=self.colours[age],
                   edgecolor=(0, 0, 0))

            multiplier += 1

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_xlabel("Paired Tetragram")
        ax.set_ylabel("% of Total")
        ax.set_title('Frequency of Paired Tetragram - ' + age)
        ax.set_xticks(np.arange(0, len(self.labels)),
                      self.labels, rotation=30, ha='right')

        ax.legend(loc='upper left')
        ax.set_ylim(0, 100)

        #plt.savefig(str(age) + "-vid-by-vid-comparison.png")
        plt.show()

    def compare_fish_per_directory(self, percent_by_row_col, age):
        """Create a bar graph for the individual fish within one video."""
        _, ax = plt.subplots()

        width = 0.05  # the width of the bars
        multiplier = 0

        _, ax = plt.subplots(layout='constrained', figsize=(9, 3))

        colour_arr = self.generate_colour_varns(len(percent_by_row_col[0][0]),
                                                self.colours[age])
        for row in percent_by_row_col:
            for item in row:
                for arr in item:
                    offset = width * multiplier

                    adj = - width * (float(len(percent_by_row_col[0])/2))

                    ax.bar(x=np.arange(adj, len(self.labels)+adj) + offset,
                           height=arr, width=width,
                           color=colour_arr[multiplier],
                           edgecolor=(0, 0, 0))

                    multiplier += 1

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_xlabel("Paired Tetragram")
        ax.set_ylabel("% of Total")
        ax.set_title('Frequency of Paired Tetragram - ' + age)
        ax.set_xticks(np.arange(0, len(self.labels)),
                      self.labels, rotation=30, ha='right')

        # ax.legend(loc='upper left')
        ax.set_ylim(0, 100)
        plt.show()

    def compare_fish_per_directory_non_tetr(self, percent_by_row_col, age):
        """Create a bar graph for the ."""
        # print(len(per),per)
        _, ax = plt.subplots()

        width = 0.05  # the width of the bars
        multiplier = 0

        _, ax = plt.subplots(layout='constrained', figsize=(9, 3))

        colour_arr = self.generate_colour_varns(len(percent_by_row_col[0][0]), self.colours[age])
        for row in percent_by_row_col:
            for item in row:
                for arr in item:
                    offset = width * multiplier

                    adj = - width * (float(len(percent_by_row_col[0])/2))

                    ax.bar(x=np.arange(adj, len(arr)+adj) + offset, height=arr,
                           width=width, color=colour_arr[multiplier],
                           edgecolor=(0, 0, 0))

                    multiplier += 1

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_xlabel("Paired Tetragram")
        ax.set_ylabel("% of Total")
        ax.set_title('Frequency of Paired Tetragram - ' + age)
        ax.set_xticks(np.arange(0, len(self.labels)),
                      self.labels, rotation=30, ha='right')

        # ax.legend(loc='upper left')
        ax.set_ylim(0, 100)
        plt.show()

    def fish_in_bar_tetr(self, percent_by_row_col, age, fns: list[str]):
        """Create a bar graph for the ."""
        # print(len(per),per)
        _, ax = plt.subplots()

        width = 0.15  # the width of the bars

        # print("attr", measurement)

        for row_num, row in enumerate(percent_by_row_col):
            for col_num, item in enumerate(row):
                _, ax = plt.subplots(layout='constrained', figsize=(9, 3))

                multiplier = 0

                colour_arr = self.generate_colour_varns(len(item), self.colours[age])

                for arr in item:
                    offset = width * multiplier

                    adj = - width * (float(len(item))/2) + width/2
                    # , color=self.defn_colours([str(x) for x in range(len(item))], "viridis"))
                    ax.bar(x=np.arange(adj, len(self.labels)+adj) + offset,
                           height=arr, label=fns[multiplier],
                           color=colour_arr[multiplier],
                           edgecolor=(0, 0, 0), width=width)

                    multiplier += 1

                ax.set_xlabel("Paired Tetragram")
                ax.set_ylabel("% of Total")
                ax.set_title('Frequency of Paired Tetragram - ' +
                             age + f' - [{row_num}, {col_num}]')
                ax.set_xticks(np.arange(0, len(self.labels)),
                              self.labels, rotation=30, ha='right')

                ax.legend(loc='upper left')
                ax.set_ylim(0, 100)
                plt.savefig(fns[0][:-5] + "-hist-" +
                            str(row_num) + "-" + str(col_num) + ".png")

                plt.close()
                #plt.show()

    """
    def create_pos_on_Y_viz(mask_path):
        df = pd.read_csv(output_filepath)
        df.head()

        for num, val in enumerate(np.unique(df['id'])):
            df.loc[df['id'] == val, 'id'] = num

        df.head()

        viz = cv2.imread(mask_path)

        viz = np.full((1200, 1760, 3), (255, 255, 255))
        tmp = df[df['frame'] < 4000]
        plt.figure(figsize=(10, 10))
        plt.imshow(viz)
        plt.scatter(tmp['pos_x'], tmp['pos_y'], c=tmp['id'])
    """

    def fish_in_bar_stacked_tetr(self, percent_by_row_col, age, fns: list[str]):
        """Create a bar graph for the ."""
        _, ax = plt.subplots()

        width = 0.1  # the width of the bars

        for row_num, row in enumerate(percent_by_row_col):
            for col_num, item in enumerate(row):
                _, ax = plt.subplots(layout='constrained', figsize=(9, 3))

                multiplier = 0

                LR_arr = np.array(item).transpose()
                bottom = np.zeros(len(item))

                colour_arr = self.generate_colour_varns(len(LR_arr), self.colours[age])

                for arr in LR_arr:
                    offset = width * multiplier

                    adj = - width * (float(len(item))/2) + width/2
                    # , color=self.defn_colours([str(x) for x in range(len(item))], "viridis"))
                    ax.bar(fns, arr, label=self.labels[multiplier],
                           bottom=bottom)

                    bottom += arr

                    multiplier += 1

                ax.set_xlabel("Paired Tetragram")
                ax.set_ylabel("% of Total")
                ax.set_title('Frequency of Paired Tetragram - ' +
                             age + f' - [{row_num}, {col_num}]')

                ax.set_xticklabels(fns, rotation=30, ha='right')
                ax.legend(loc='upper left')
                ax.set_ylim(0, 100)
                plt.savefig(fns[0][:-5] + "-stacked-" +
                            str(row_num) + "-" + str(col_num) + ".png")

                plt.close()
                #plt.show()

    def spont_percent_bar(self, percent: dict):
        """Paired tetragram bar graph."""
        width = 0.1  # the width of the bars
        multiplier = 0

        _, ax = plt.subplots(layout='constrained', figsize=(17, 3))

        for attribute, measurement in percent.items():
            # print(attribute, measurement)
            offset = width * multiplier
            adj = -0.1 * (float(len(percent))/2)

            ax.bar(np.arange(adj, len(percent)+adj) + offset, measurement,
                   width, label=attribute, color=self.colours[attribute])

            multiplier += 1

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_xlabel("Age")
        ax.set_ylabel("Spontaneous Alternation %")

        ax.legend(loc='upper left')
        plt.show()
