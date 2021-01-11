from CONSTANTS import *
from z_RR_data import data_RR_2

plt.style.use('bmh')
lines = ['-', '--', '-.', ':', ]
lines.reverse()
markers = ['o', '+', '.', ',', '_', '*']
markers.reverse()
algs = ['CAMS', 'Max-sum_MST']
iterations = 10
fig, ax = plt.subplots()

for alg in algs:
    for line_indx, line in enumerate(data_RR_2[alg]['times']):
        first_item = line[1]
        new_line = []
        for item in line[1:]:
            new_line.append(item - first_item)
        data_RR_2[alg]['times'][line_indx] = new_line


# ------------ ADD ------------ #
def add_graph(line_index, marker_index, graph_dict, alg_name, alg_label, color):
    line_index = 0 if line_index == len(lines) else line_index
    marker_index = 0 if marker_index == len(markers) else marker_index
    matrix = graph_dict[alg_name]['times']
    avr = np.average(matrix, 0)
    std = np.std(matrix, 0)
    line = lines[line_index]
    marker = markers[marker_index]
    # print(f'{alg_name}: li:{line_index} mi:{marker_index}')
    ax.plot(range(len(avr)), avr, '%s%s' % (marker, line), label=alg_label, color=color)

    ax.fill_between(range(len(avr)), avr - AMOUNT_OF_STD * std, avr + AMOUNT_OF_STD * std,
                    alpha=0.2, antialiased=True, color=color)


# ----------------------------- #

add_graph(0, 4, data_RR_2, 'Max-sum_MST', 'Max-sum_MST', 'g')
add_graph(3, 3, data_RR_2, 'CAMS', 'CAMS', 'm')

ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', prop={'size': 15})
ax.set_ylabel('Time (seconds)', fontsize=15)
ax.set_xlabel('Iterations', fontsize=15)
ax.set_xticks(range(iterations))
# ax.set_xlim(xmin=iterations[0], xmax=iterations[-1])
fig.tight_layout()
plt.show()