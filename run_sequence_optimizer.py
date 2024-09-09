import numpy as np
import random
import pandas as pd
import time
import copy

from general.functions import follow, evaluator, Settings, empty_arena_folder, write_fermentation_plan, read_new_line_arena
from methods.local_search import local_search
from methods.random_search import random_search
from methods.iterated_greedy import iterated_greedy
from simulator.scenarios.set_up_simulator_folder import prepare_simulator_folder


if __name__ == '__main__':

    # SETTINGS INPUT / OUTPUT
    title_run_results = "Results_sequence_optimizer"  # Title of results sequence optimizer
    scenario_name = "As-Is"  # Refers to the folder of the scenario that we are interested in
    source_folder = f'simulator/scenarios/{scenario_name}'  # Directory scenario data files
    destination_folder = "simulator/scenarios"  # Here the data files are copied that are read by the Arena simulator
    output_files_simulator = ["Output_file_1"]  # Define output files from every simulator run that need to be emptied

    # SETTINGS FOR ARENA INTEGRATION
    file_path = f'simulator/scenarios/file_R_OptimizationKPIs.txt'  # The file with the Optimization KPIs
    python_output = f"simulator/scenarios/file_D_FermentationPlanFromPython.txt"  # The input fermentation plan for Arena
    with open(file_path, 'w') as creating_new_csv_file:
        pass
    print("Empty File for Arena Output Created Successfully")
    with open(python_output, 'w') as creating_new_csv_file:
        pass
    print("Empty File for Python Output Created Successfully")
    loglines = follow(file_path)
    replication_counter = 0

    # SETTINGS FOR SCENARIO
    scenario_plan = prepare_simulator_folder(source_folder, destination_folder)
    n = scenario_plan.shape[0]

    # SETTINGS FOR SEARCH ALGORITHM
    summary = []
    # weights for kpis that together determine fitness
    l1 = 1  # weight of kpi 1
    l2 = 0  # weight of kpi 2
    l3 = 0  # weight of kpi 3
    l4 = 0  # weight of kpi 4

    budget = 10000  # number of replications for Arena
    setting = Settings(method="local_search", stop_criterium="Budget", budget=budget,
                       instance=scenario_name, size=len(scenario_plan), simulator="scenarios",
                       objective=f"l1_{l1}_l2={l2}_l3={l3}_l4={l4}", init="plan", seed=1, l1=l1, l2=l2, l3=l3, l4=l4)

    # INITIALIZE
    random.seed(setting.seed)
    np.random.seed(setting.seed)
    printing = False
    file_name = setting.make_file_name()
    f_eval = lambda x, i: evaluator(instance=scenario_plan , setting=setting, replication=replication_counter + i, sequence=x,
                                    testing=False, python_output=python_output, loglines=loglines,
                                    printing=printing)
    empty_arena_folder(output_files_simulator, simulator=setting.simulator)
    if setting.init == "random":
        init = None
    elif setting.init == "sorted":
        init = [i for i in range(0, setting.size)]
    elif setting.init == "plan":
        init = scenario_plan["Fermentation_sequence"].tolist()
        init = [i-1 for i in init]
        init = np.argsort(init)

    # RUN ALGORITHM
    # TODO: more advanced algorithms could improve the optimizer
    print(f"Start new instance {setting.instance}")
    start = time.time()
    if setting.method == "local_search":
        nr_iterations, best_sequence = local_search(n=setting.size, stop_criterium=setting.stop_criterium,
                                                    budget=setting.budget, f_eval=f_eval,
                                                    time_limit=setting.time_limit,
                                                    output_file=f'results/{file_name}.txt', write=True,
                                                    printing=printing, init=init)
    elif setting.method == "random_search":
        nr_iterations, best_sequence = random_search(n=setting.size, stop_criterium=setting.stop_criterium,
                                                     budget=setting.budget, f_eval=f_eval,
                                                     output_file=f'results/{file_name}.txt', write=True,
                                                     printing=printing)

    elif setting.method == "iterated_greedy":
        nr_iterations, best_sequence = iterated_greedy(n=n, stop_criterium=setting.budget, time_limit=setting.time_limit,
                                                       budget=setting.budget,  f_eval=f_eval,
                                                       output_file=f'results/{file_name}.txt',
                                                       init=init, seed=setting.seed)

    # PROCESS OUTPUT
    replication_counter += nr_iterations
    replication_counter += 1
    write_fermentation_plan(instance=scenario_plan, replication=replication_counter, sequence=list(best_sequence),
                            python_output=python_output)
    _, _, kpi_1, kpi_2, kpi_3, kpi_4 = read_new_line_arena(loglines, printing=True)

    summary.append({"simulator": setting.simulator,
                    "instance": setting.instance,
                    "method": setting.method,
                    "init": setting.init,
                    "objective": setting.objective,
                    "size": setting.size,
                    "stop_criterium": setting.stop_criterium,
                    "time": round(time.time()-start),
                    "budget": setting.budget,
                    "seed": setting.seed,
                    "sequence": list(best_sequence),
                    "kpi_1": kpi_1,
                    "kpi_2": kpi_2,
                    "kpi_3": kpi_3,
                    "kpi_2": kpi_4,
                    "fitness": setting.l1 * kpi_1 + setting.l2 * kpi_2 + setting.l3 * kpi_2 + setting.l4 * kpi_4,
                    "l1": setting.l1,
                    "l2": setting.l2,
                    "l3": setting.l3,
                    "l4": setting.l4})

    summary_df = pd.DataFrame(summary)
    summary_df.to_csv(f"optimizer_summary/{title_run_results}.csv")

    new_plan = copy.copy(scenario_plan)
    fermentation_sequence = np.argsort(best_sequence) + 1
    new_plan["Fermentation_sequence"] = fermentation_sequence
    new_plan.to_csv(f"results/fermentation_sequence/{file_name}.csv")




