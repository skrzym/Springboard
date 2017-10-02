import numpy as np
import matplotlib.pyplot as plt


def permutation_sample(data1, data2):
    """Generate a permutation sample from two data sets."""

    # Concatenate the data sets: data
    data = np.concatenate((data1,data2))

    # Permute the concatenated array: permuted_data
    permuted_data = np.random.permutation(data)

    # Split the permuted array into two: perm_sample_1, perm_sample_2
    perm_sample_1 = permuted_data[:len(data1)]
    perm_sample_2 = permuted_data[len(data1):]

    return perm_sample_1, perm_sample_2


def draw_perm_reps(data_1, data_2, func, size=1):
    """Generate multiple permutation replicates."""

    # Initialize array of replicates: perm_replicates
    perm_replicates = np.empty(size)

    for i in range(size):
        # Generate permutation sample
        perm_sample_1, perm_sample_2 = permutation_sample(data_1, data_2)

        # Compute the test statistic
        perm_replicates[i] = func(perm_sample_1, perm_sample_2)

    return perm_replicates


def ecdf(data):
    """Compute ECDF for a one-dimensional array of measurements."""

    # Number of data points: n
    n = len(data)

    # x-data for the ECDF: x
    x = np.sort(data)

    # y-data for the ECDF: y
    y = np.arange(1, n+1) / n

    return x, y


def plot_ecdf(x_and_y, linestyle='none', marker='.', title='Placeholder', xlabel='X-axis', ylabel='Y-axis', figsize=(15,10)):
    """ Plot ECDF using matplotlib. 
        Designed to take the output of the ecdf() function as a direct input.
        Returns a matplotlib.pyplot.axes instance."""
    fig, axes = plt.subplots(1,1,figsize=figsize)
    axes = plt.title(title)
    axes = plt.xlabel(xlabel)
    axes = plt.ylabel(ylabel)
    axes.plot(x_and_y[0], x_and_y[1], linestyle=linestyle, marker=marker)
    return axes