# Sequence Optimizer

This repository contains the code to connect python with the Seclin simulation tool, developed in Arena. 
It contains optimization algorithms that use an Arena simulation tool as evaluator. 

The repository also contains a manual that explains how to set up the Arena - Python integration. However,
for a working implementation the Python scripts must be connected to an Arena model, and the Arena model
should contain logic to run a replication based on a new fermentation plan that is located at 
"simulator/scenarios/file_D_FermentationPlanFromPython.txt", and should write the replication results to a 
new line in "simulator/scenarios/file_R_OptimizationKPIs.txt".


