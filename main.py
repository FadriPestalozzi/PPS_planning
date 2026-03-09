from time import sleep
from datetime import datetime
import matplotlib; matplotlib.use("TkAgg")
from matplotlib import pyplot as plt
import PPSSimulation as pps

# import webapp as web

if __name__ == '__main__':
    # start with getting the data set from sql
    production_orders, opcs, workplaces, dispatchdepartments, opcs_by_PA = pps.build_dataset()

    # for wp in workplaces.values():
    #     print(f'Workplace: {wp.name} has {len(wp.input_wip)} WIP')
    #     print([pa.PA for pa in wp.input_wip])

    simtime = pps.sim_clock()
    fig, [ax, ax2] = plt.subplots(constrained_layout=True, nrows=1, ncols=2)
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
    ax2.bar(['fertig'], [len(workplaces[wp].output_wip) for wp in workplaces.keys() if wp == 'Abschlussbuchung'])
    sleep(.1)
    plt.savefig('start.png')
    print('saved start.png')
    plt.pause(0.001)
    logpath = f'./logs/log{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.txt'
    with open(logpath, 'a+', encoding='UTF-8') as f:
        f.write(f'Logfile for {datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}\n')
        f.write('Dispatchlists:\n')
        for disp in dispatchdepartments.values():
            for wp in disp.workplaces:
                f.write(f'Workplace: {wp.name} has {len(wp.input_wip)} WIP\n')
                f.write(','.join([str(elem.PA)+ ' ' + str(elem.current_step.opcID) +' ' + str(round(elem.current_step.TotalActiveTime,2)) + '/' + str(round(elem.current_step.PlannedOperationTime,2)) for elem in wp.input_wip]) + '\n')
        f.write('\n')

    def update(barplot, step = 0):
        with open(logpath, 'a+', encoding='UTF-8') as f:
            print(f'Step: {step}', simtime.date)
            f.write(f'Step: {step}, {simtime.date}\n')
            for disp in dispatchdepartments.values():
                disp.run(simtime, f)
            # first process all wps, then ship them. Else process A, shipping to B then processing B results in PAs jumping multiple times in a sim day
            for disp in dispatchdepartments.values():
                disp.ship_output_wip(simtime, f)
            simtime.tick()

        # updating the graph
        heights = [len(workplaces[wp].input_wip) for wp in workplaces.keys()]
        ax.cla()
        ax.bar(names, heights)
        ax.set_xlabel("Workplace")
        ax.set_ylabel("WIP in PA")
        ax.set_xticks(range(len(names)))
        ax.set_xticklabels(names, rotation=45, ha="right")
        ax.set_ylim(0, 150)
        ax2.bar(['fertig'],[len(workplaces[wp].output_wip) for wp in workplaces.keys() if wp.name == 'Abschlussbuchung'])
        sleep(.05)
        plt.title(simtime.date)
        plt.draw()
        plt.pause(0.001)

    for i in range(100):
        update(ax, i)

        plt.savefig(f'./finish.png')