import time
import os
import random
import copy
import numpy as np


def empty_arena_folder(output_files, simulator="Factory"):
    for output_file_arena in output_files:
        with open(f"simulator/{simulator}/file_R_{output_file_arena}.txt",
                  'w') as creating_new_csv_file:
            pass
    print("Empty Files for ArenaOutput Created Successfully")


def write_fermentation_plan(instance, replication, sequence, python_output):
    """
    :param instance: a fermentation plan for Seclin for which the fermentation sequence has to be determined
    :param replication: the replication that matches with the Arena replication number
    :param sequence: the sequence in which the batches must be prioritized
    :param python_output: the destination from which Arena reads in the sequences

    This function reads in a fermentation sequence for a certain instance and
    translates this to the required fermentation plan input that is written to
    the python_output destination.
    """
    #print(sequence)
    if sequence is None:
        print("No sequence was given")
        fermentation_plan = copy.copy(instance)

    elif len(sequence) == instance.shape[0]:
        fermentation_sequence = np.argsort(sequence)
        fermentation_plan = copy.copy(instance)
        fermentation_plan["Fermentation_sequence"] = fermentation_sequence + 1

    else:
        fermentation_plan = copy.copy(instance)
        fermentation_plan = fermentation_plan.loc[sequence]
        fermentation_plan["ID"] = range(1, fermentation_plan.shape[0] + 1)
        fermentation_plan["Fermentation_sequence"] = range(1, fermentation_plan.shape[0] + 1)

    fermentation_plan.insert(fermentation_plan.shape[1], "Replication", replication)

    num_columns = len(fermentation_plan.columns)
    if num_columns == 17:
        fermentation_plan = fermentation_plan.drop(fermentation_plan.columns[0], axis=1)
    fermentation_plan.to_csv(python_output, header=False, index=False)


def follow(filepath):
    """
    :param filepath:
    :return: generator object, line in text file
    Generator function that yields new lines in a file
    """
    thefile = open(filepath, 'r')
    st_results = os.stat(filepath)
    st_size = st_results[6]
    thefile.seek(st_size)

    while True:
        where = thefile.tell()
        line = thefile.readline()
        if not line or not line.endswith('\n'):
            time.sleep(0.1)
            thefile.seek(where)
            continue
        else:
            yield line


def read_new_line_arena(loglines, printing=True):
    """
    :param loglines: generator object that follows lines in text file
    :param objective: the required KPI for optimization
    :return: fitness value (the required KPI)
    """

    line = next(loglines)  # read in the new line
    line_split = line.split(",")
    replication = line_split[0]  # check replication ID
    check_sequence = line_split[1].split()  # Arena sequence
    check_sequence = [int(i) for i in check_sequence]

    # KPIS
    kpi_1 = float(line_split[2])
    kpi_2 = float(line_split[3])
    kpi_3 = float(line_split[9])
    kpi_4 = float(line_split[10])

    if int(line_split[6]) == 1:
        print("Warning, deadlock issue while testing")
        print(line_split)
        kpi_1 = 9999999
        kpi_2 = 9999999
        kpi_3 = 9999999
        kpi_4 = 9999999

    if printing:
        # Print all relevant KPIs
        print(f"KPI 1 is {kpi_1}")
        print(f"KPI 2 is {kpi_2}")
        print(f"KPI 3 is {kpi_3}")
        print(f"KPI 4 is {kpi_4}")

    return replication, check_sequence, kpi_1, kpi_2, kpi_3, kpi_4


def evaluator(instance, replication, sequence, python_output, loglines, setting, testing=False, printing=True):
    """
    :param instance: fermentation plan
    :param replication: replication ID that matches with Arena replications
    :param sequence: fermentation sequence that must be tested
    :param python_output: destination of python file from which Arena reads in fermentation plan
    :param loglines: generator object that follows new lines in Arena output
    :param objective: the required KPI for optimization
    :return: fitness
    """
    if testing:
        write_fermentation_plan(instance, replication, sequence, python_output)
        fitness = random.randint(-1000000, 0)
    else:
        # TODO: note this could be adjusted if different KPIS are needed
        write_fermentation_plan(instance, replication, sequence, python_output)
        replication, check_sequence, kpi_1, kpi_2, kpi_3, kpi_4 = read_new_line_arena(loglines, printing=printing)
        fitness = setting.l1 * kpi_1 + setting.l2 * kpi_2 + setting.l3 * kpi_3 + setting.l4 * kpi_4
        print(f'fitness is {fitness}')

    return fitness


class Settings:
    def __init__(self, size=5, method="local_search", time_limit=180, budget=400, stop_criterium="Time",
                 simulator="Factory", seed=1, instance="5_1", objective="Makespan", init="random", l1=1, l2=0, l3=0, l4=0,
                 k=40, m=20):
        self.method = method
        self.init = init
        self.time_limit = time_limit
        self.budget = budget
        self.stop_criterium = stop_criterium
        self.seed = seed
        self.simulator = simulator
        self.instance = instance
        self.size = size
        self.objective = objective
        self.l1 = l1
        self.l2 = l2
        self.l3 = l3
        self.l4 = l4
        self.k = k
        self.m = m

    def make_file_name(self):
        if self.stop_criterium == "Time":
            return f'{self.method}_simulator={self.simulator}_time_limit={self.time_limit}_seed={self.seed}_instance_' \
                   f'{self.instance}_objective={self.objective}_init={self.init}'

        else:
            return f'{self.method}_simulator={self.simulator}_budget={self.budget}_seed={self.seed}_instance_' \
                   f'{self.instance}_objective={self.objective}_init={self.init}'
