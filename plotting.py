from matplotlib import pyplot as plt

def initialize_plot(dispatchdepartments, workplaces):
    # fig, [ax, ax2] = plt.subplots(constrained_layout=True, nrows=1, ncols=1) # ncols=2
    fig, ax = plt.subplots(constrained_layout=True, nrows=1, ncols=1) # ncols=2
    fig.set_size_inches(18.5, 10.5)

    # maximize window
    mng = plt.get_current_fig_manager()
    mng.window.state("zoomed")
    names = [dispatchdepartments[disp].name for disp in dispatchdepartments.keys()]
    heights = [sum(len(workplaces[wp.name].input_wip) for wp in dispatchdepartments[disp].workplaces) for disp in dispatchdepartments.keys()]
    ax.bar(names, heights)
    ax.set_xlabel("Dispatch Department")
    ax.set_ylabel("WIP in PA")
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names, rotation=45, ha="right")
    ax.set_ylim(0, 150)
    # ax2.bar(['fertig'], [len(workplaces[wp].output_wip) for wp in workplaces.keys() if wp == 'Abschlussbuchung'])
    plt.tight_layout(pad=2)
    plt.pause(0.001)
    plt.savefig('./plots/start.png')
    # return fig, ax , ax2
    return fig, ax , 0

def update_plot(fig, ax, ax2, dispatchdepartments, workplaces, title='', filename=''):
    names = [dispatchdepartments[disp].name for disp in dispatchdepartments.keys()]
    heights = [sum(len(workplaces[wp.name].input_wip) for wp in dispatchdepartments[disp].workplaces) for disp in dispatchdepartments.keys()]
    ax.cla()
    ax.bar(names, heights)
    ax.set_xlabel("Dispatch Department")
    ax.set_ylabel("WIP in PA")
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names, rotation=45, ha="right")
    ax.set_ylim(0, 150)

    # ax2.cla()
    # ax2.bar(['fertig'],[len(workplaces[wp].output_wip) for wp in workplaces.keys() if wp == 'Abschlussbuchung'])

    fig.suptitle(title)
    plt.draw()
    plt.pause(0.001)
    fig.savefig(filename)


def save_plot(fig, filename):
    fig.savefig(filename)
    plt.close(fig)


def saturation(dispatchdepartments, simtime):
    fig, ax = plt.subplots()
    wip = 0
    sat = {}
    for disp in dispatchdepartments.values():
        sat[disp.name] = [sum([len(wp.input_wip) for wp in disp.workplaces])]
        # TODO
    return