# Plot settings file

from math import sqrt


fig_width_pt = 220.  # Get this from LaTeX using \showthe\columnwidth
inches_per_pt = 1.0 / 72.27               # Convert pt to inch
golden_mean = (sqrt(5.0) - 1.0) / 2.0         # Aesthetic ratio
fig_width = fig_width_pt * inches_per_pt  # width in inches
fig_height = fig_width * golden_mean      # height in inches
fig_height *= 1.25
fig_size = [fig_width, fig_height]
plot_params = {
    'backend': 'ps',
    'axes.labelsize': 10,
    'text.fontsize': 10,
    'legend.fontsize': 7,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'text.usetex': True,
    'figure.figsize': fig_size,
    'lines.markersize': 2,
    'figure.autolayout': True
}

