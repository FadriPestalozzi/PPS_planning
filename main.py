import numpy as np
from time import time as timestamp, sleep, strftime

import matplotlib; matplotlib.use("TkAgg")
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation

import dataloading as load
import PPSSimulation as pps
from PPSSimulation import sim_clock


# import webapp as web

if __name__ == '__main__':
    # start with getting the data set from sql
    production_orders, opcs, workplaces, dispatchdepartments, opcs_by_PA = pps.build_dataset()

    # for wp in workplaces.values():
    #     print(f'Workplace: {wp.name} has {len(wp.input_wip)} WIP')
    #     print([pa.PA for pa in wp.input_wip])

    simtime = pps.sim_clock()
    fig, ax = plt.subplots(constrained_layout=True)
    fig.set_size_inches(18.5, 10.5)
    # maximize window
    mng = plt.get_current_fig_manager()
    mng.window.state("zoomed")
    names = [workplaces[wp].name for wp in workplaces.keys()]
    # creating the first plot and frame
    ax.bar(names, [len(workplaces[wp].input_wip) for wp in workplaces.keys()])
    ax.set_xlabel("Workplace")
    ax.set_ylabel("WIP in PA")
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names, rotation=45, ha="right")
    ax.set_ylim(0, 150)
    plt.tight_layout(pad=2)
    sleep(.1)
    plt.savefig('start.png')
    print('saved start.png')
    plt.pause(0.001)

    # updates the data and graph
    def update(barplot, step = 0):
        for disp in dispatchdepartments.values():
            disp.run(simtime)
        # first process all wps, then ship them. Else process A, shipping to B then processing B results in PAs jumping multiple times in a sim day
        for disp in dispatchdepartments.values():
            disp.ship_output_wip(simtime)
        # updating the graph
        heights = [len(workplaces[wp].input_wip) for wp in workplaces.keys()]

        ax.cla()
        ax.bar(names, heights)
        ax.set_xlabel("Workplace")
        ax.set_ylabel("WIP in PA")

        ax.set_xticks(range(len(names)))
        ax.set_xticklabels(names, rotation=45, ha="right")
        ax.set_ylim(0, 150)
        simtime.tick()
        print(f'Step: {step}', simtime.date)
        sleep(.2)
        plt.title(simtime.date)
        plt.draw()
        plt.pause(0.001)

    for i in range(96):
        update(ax, i)
