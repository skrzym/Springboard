import numpy as np
import matplotlib.pyplot as plt


class HypothesisTest(object):
    """Represents a hypothesis test."""

    def __init__(self, data):
        """Initializes.

        data: data in whatever form is relevant
        """
        self.data = data
        self.make_model()
        self.actual = self.test_statistic(data)
        self.test_stats = None

    def p_value(self, iters=1000):
        """Computes the distribution of the test statistic and p-value.

        iters: number of iterations

        returns: float p-value
        """
        iters = float(iters)
        self.test_stats = np.array([self.test_statistic(self.run_model())
                                    for _ in range(int(iters))])

        count = float(sum(self.test_stats >= self.actual))
        return count / iters

    def max_test_stat(self):
        """Returns the largest test statistic seen during simulations.
        """
        return max(self.test_stats)

    def plot_hist(self, label=None):
        """Draws a CDF with vertical lines at the observed test stat.
        """
        ys, xs, patches = plt.hist(self.test_stats, color='blue')
        plt.vlines(self.actual, 0, max(ys), linewidth=3, color='0.8')
        plt.xlabel('test statistic')
        plt.ylabel('count')

    def test_statistic(self, data):
        """Computes the test statistic.

        data: data in whatever form is relevant
        """
        raise UnimplementedMethodException()

    def make_model(self):
        """Build a model of the null hypothesis.
        """
        pass

    def run_model(self):
        """Run the model of the null hypothesis.

        returns: simulated data
        """
        raise UnimplementedMethodException()


class DiffMeansPermute(HypothesisTest):
    """Tests a difference in means by permutation."""

    def test_statistic(self, data):
        """Computes the test statistic.

        data: data in whatever form is relevant
        """
        group1, group2 = data
        test_stat = abs(group1.mean() - group2.mean())
        return test_stat

    def make_model(self):
        """Build a model of the null hypothesis.
        """
        group1, group2 = self.data
        self.n, self.m = len(group1), len(group2)
        self.pool = np.hstack((group1, group2))

    def run_model(self):
        """Run the model of the null hypothesis.

        returns: simulated data
        """
        np.random.shuffle(self.pool)
        data = self.pool[:self.n], self.pool[self.n:]
        return data


class BinomialPermutationTest(HypothesisTest):
    def test_statistic(self, data):
        """Calculates the success probabilities for both groups

        returns: absolute difference between the groups' success probabilities
        """
        g1, g2 = data
        g1_success_count = sum(g1)
        g1_total_count = len(g1)
        g2_success_count = sum(g2)
        g2_total_count = len(g2)

        g1_success_prob = float(g1_success_count) / float(g1_total_count)
        g2_success_prob = float(g2_success_count) / float(g2_total_count)

        group_diff = abs(g1_success_prob - g2_success_prob)
        return group_diff

    def make_model(self):
        """Build a model of the null hypothesis.
        """
        group1, group2 = self.data
        self.n, self.m = len(group1), len(group2)
        self.pool = np.hstack((group1, group2))

    def run_model(self):
        """Run the model of the null hypothesis.

        returns: simulated data
        """
        np.random.shuffle(self.pool)
        data = self.pool[:self.n], self.pool[self.n:]
        return data
