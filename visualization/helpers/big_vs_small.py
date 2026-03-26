import numpy as np

def read_in_sizes(fn):
    f = open(fn, 'r')
    d = dict()

    new_fn = ""

    for line in f.readlines():
        if len(line) > 40:
            if new_fn != "":
                d.update({new_fn: arr})

#            new_fn = line.strip('\n').split("/")[-1]
#            arr = [[0 for i in range(4)] for i in range(3)]
            l = line.strip('\n').split(' ')
            if "run" in l[0]:
                new_fn = l[0].split("/")[-1].split("run")[-1][:-len("-dpix-post-processed.csv")]
            else:
                new_fn = l[0].split("/")[-1][:-len("-dpix-post-processed.csv")]
            arr = [[0 for i in range(int(l[2]))] for i in range(int(l[1]))]

        else:
            l = line.split(' ')
            row = int(l[0])
            col = int(l[1])

            size = float(l[2].strip('\n'))
            if np.isnan(size):
                arr[row][col] = 0
            else:
                arr[row][col] = size

    return d

def read_in_velocities(fn):
    f = open(fn, 'r')
    d = dict()

    new_fn = ""

    for line in f.readlines():
        if len(line) > 40:
            if new_fn != "":
                d.update({new_fn: arr})

#            new_fn = line.strip('\n').split("/")[-1]
#            arr = [[0 for i in range(4)] for i in range(3)]
            l = line.strip('\n').split(' ')
            if "run" in l[0]:
                new_fn = l[0].split("/")[-1].split("run")[-1][:-len("mode_no_whitethresh-post-processed.csv")]
            else:
                new_fn = l[0].split("/")[-1][:-len("mode_no_whitethresh-post-processed.csv")]

            arr = [[0 for i in range(int(l[2]))] for i in range(int(l[1]))]

        else:
            l = line.split(' ')
            row = int(l[0])
            col = int(l[1])

            size = float(l[2].strip('\n'))
            if np.isnan(size):
                arr[row][col] = 0
            else:
                arr[row][col] = size

    return d