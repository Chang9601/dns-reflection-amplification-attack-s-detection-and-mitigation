#!/usr/bin/python

############################################################################
##
##     This file is part of Purdue CS 422.
##
##     Purdue CS 422 is free software: you can redistribute it and/or modify
##     it under the terms of the GNU General Public License as published by
##     the Free Software Foundation, either version 3 of the License, or
##     (at your option) any later version.
##
##     Purdue CS 422 is distributed in the hope that it will be useful,
##     but WITHOUT ANY WARRANTY; without even the implied warranty of
##     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##     GNU General Public License for more details.
##
##     You should have received a copy of the GNU General Public License
##     along with Purdue CS 422. If not, see <https://www.gnu.org/licenses/>.
##
#############################################################################

import argparse

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def parse_test_output(fname):
    f = open(fname, 'r')
    num_dns = []
    for line in f:
        try:
            count = int(line.split(' ')[0])
            num_dns.append(count)
        except ValueError:
            pass
    f.close()
    return num_dns


def plot_dns(test_fnames, out_fname):
    # plot absolute # responses received
    fig = plt.figure(figsize=(16, 8))
    for fname in test_fnames:
        data = parse_test_output(fname)
        plt.plot(np.arange(len(data)) * 5, data, linewidth=2, label=fname.split('.')[0].split('_')[0])
    plt.legend(fontsize=16, loc=2)
    plt.xlabel("Seconds (approximate)", fontsize=16)
    plt.ylabel("Number of DNS responses received", fontsize=16)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.savefig(out_fname)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Plot DNS results')
    parser.add_argument("--list", nargs="+", required=True)
    parser.add_argument('--output', type=str, action="store", required=True)
    args = parser.parse_args()

    test_fnames = args.list
    out_fname = args.output
    plot_dns(test_fnames, out_fname)
    # plt.show()
