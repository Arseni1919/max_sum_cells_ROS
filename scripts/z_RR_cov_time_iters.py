from CONSTANTS import *
from z_RR_data import data_RR_2

plt.style.use('bmh')
lines = ['-', '--', '-.', ':', ]
lines.reverse()
markers = ['o', '+', '.', ',', '_', '*']
markers.reverse()
algs = ['CAMS', 'Max-sum_MST']
fig, ax = plt.subplots()

def get_avr_std(matrix1):
    avr_list = []
    std_list = []
    for line in matrix1:
        avr_list.append(np.mean(line))
        std_list.append(np.std(line))
    return np.array(avr_list), np.array(std_list)


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
    matrix_times = graph_dict[alg_name]['times']
    avr_t = np.average(matrix_times, 0)
    std_t = np.std(matrix_times, 0)
    matrix_cov = graph_dict[alg_name]['cov']
    avr_c = np.average(matrix_cov, 0)
    std_c = np.std(matrix_cov, 0)
    line = lines[line_index]
    marker = markers[marker_index]
    # print(f'{alg_name}: li:{line_index} mi:{marker_index}')
    ax.plot(avr_t, avr_c, '%s%s' % (marker, line), label=alg_label, color=color)

    ax.fill_between(avr_t, avr_c - AMOUNT_OF_STD * std_c, avr_c + AMOUNT_OF_STD * std_c,
                    alpha=0.2, antialiased=True, color=color)


# ----------------------------- #

add_graph(0, 4, data_RR_2, 'Max-sum_MST', 'Max-sum_MST', 'g')
add_graph(3, 3, data_RR_2, 'CAMS', 'CAMS', 'm')

ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', prop={'size': 15})
ax.set_ylabel('Remaining Coverage Requirement', fontsize=15)
ax.set_xlabel('Time (seconds)', fontsize=15)
# ax.set_ylabel('Time (seconds)', fontsize=15)
# ax.set_xlabel('Remaining Coverage Requirement', fontsize=15)
# ax.set_xticks(range(len(cov_list)))
# ax.set_xticklabels(cov_list)
# ax.set_xlim(xmin=iterations[0], xmax=iterations[-1])
fig.tight_layout()
plt.show()