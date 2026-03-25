from matplotlib import pyplot as plt
from matplotlib.gridspec import GridSpec

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white"
})

def initialize_plot(dispatchdepartments, workplaces):
    """

    :param dispatchdepartments:
    :param workplaces:
    :return:
    """
    fig = plt.figure(figsize=(18.5, 10.5))
    gs = GridSpec(3, 10, figure=fig)
    ax = fig.add_subplot(gs[0:2, 0:8])
    ax2 = fig.add_subplot(gs[0:2, 8:])
    ax_table = fig.add_subplot(gs[2, :])

    fig.set_size_inches(18.5, 10.5)
    ax_table.axis('off')
    # maximize window
    mng = plt.get_current_fig_manager()
    mng.window.state("zoomed")
    names = [dispatchdepartments[disp].name for disp in dispatchdepartments.keys()]
    heights = [sum(len(workplaces[wp.name].input_wip) for wp in dispatchdepartments[disp].workplaces) for disp in dispatchdepartments.keys()]
    bp = ax.bar(names, heights)
    ax.set_xlabel("Dispatch Department")
    ax.set_ylabel("WIP in PA")
    ax.set_xticks(range(len(names)))
    ax.bar_label(bp, labels=[str(h) for h in heights])
    ax.set_ylim(0, 150)
    ax2.bar(['fertig'], [len(workplaces[wp].output_wip) for wp in workplaces.keys() if wp == 'Abschlussbuchung'])
    # plt.tight_layout(pad=2)
    plt.pause(0.001)
    plt.savefig('./plots/start.png')
    return fig, ax , ax2, ax_table

def update_plot(fig, ax: plt.axis, ax2, dispatchdepartments, workplaces, title='', filename=''):
    names = [dispatchdepartments[disp].name for disp in dispatchdepartments.keys()]
    heights = [sum(len(workplaces[wp.name].input_wip) for wp in dispatchdepartments[disp].workplaces) for disp in dispatchdepartments.keys()]
    ax.cla()
    bp = ax.bar(names, heights)
    ax.bar_label(bp, labels=[str(h) for h in heights])
    ax.set_xticklabels(heights)
    ax.set_xlabel("Dispatch Department")
    ax.set_ylabel("WIP in PA")
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names, rotation=45, ha="right")
    ax.grid(True)
    ax.set_ylim(0, 100)

    ax2.cla()
    ax2.bar(['fertige WAs'],[len(workplaces[wp].output_wip) for wp in workplaces.keys() if wp == 'Abschlussbuchung'])


    fig.suptitle(title)
    plt.draw()
    plt.pause(0.001)
    fig.savefig(filename)

def save_plot(fig, filename):
    fig.savefig(filename)
    plt.close(fig)

def plot_saturation(dispatchdepartments, sats, simtime, fig_table, table_ax):
    """

    :param dispatchdepartments:
    :param simtime:
    :return:
    """
    def get_color(a):
        if a < 20:
            return 'y'
        elif a > 150:
            return 'r'
        else:
            return 'w'

    disps = ['Laser', 'Bohren & Fräsen', 'AOI', 'Dünnschichtlabor', 'Gal Cu Yasmin', 'Endprüfung Visuell']
    sat_of_day = []
    for disp in disps:
         sat_of_day.append(round(sum([len(wp.input_wip)/wp.capa_per_day * 100 for wp in dispatchdepartments[disp].workplaces]),1))
    sats[simtime.copy()] = sat_of_day
    # cellcolours = [['w']*len(disps)]*len([_ for _ in sats.keys()])

    cellcolours = [[get_color(sat) for sat in sat_of_day] for sat_of_day in sats.values()]
    # fig_table.patch.set_visible(False)
    table_ax.cla()
    table_ax.axis('off')
    table_ax.axis('tight')
    table_ax.table(cellText=[sats[key] for key in sats.keys()], rowLabels=[key.string() for key in sats.keys()], colLabels=disps,
                   loc='center', cellColours=cellcolours)
    fig_table.tight_layout()
    # table_ax.set_title(f'Saturation')
    return sats