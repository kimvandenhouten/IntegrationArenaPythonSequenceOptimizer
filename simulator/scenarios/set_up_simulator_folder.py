import os
import shutil
import pandas as pd


def prepare_simulator_folder(source_folder, destination_folder, instance_file_path=None):
    """
    This script sets all the data files in the simulator folder
    and returns the instance
    """

    # Check if the source folder exists
    if not os.path.exists(source_folder):
        print(f"Source folder '{source_folder}' does not exist.")
        exit()

    # Check if the destination folder exists, create it if not
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    # Loop through files in the source folder
    for filename in os.listdir(source_folder):
        # Check if the file has a ".txt" extension
        if filename.endswith('.txt'):
            source_file = os.path.join(source_folder, filename)
            destination_file = os.path.join(destination_folder, filename)

            # Copy the file to the destination folder
            shutil.copy(source_file, destination_file)
            print(f"Copied '{filename}' to '{destination_folder}'")

    print("Copy operation completed.")

    column_names = ["ID", "Product", "Batch_ID", "Year", "Month", "MachineA", "MachineB", "Dummy1", "Dummy2", "Dummy3", "Dummy4",
                    "Fermentation_sequence", "Start_date", "Month_required", "Dummy_column"]
    if instance_file_path is None:
        instance = pd.read_csv(f'{destination_folder}/file_D_Fermentation Plan.txt', header=None)
        instance.columns = column_names
    else:
        instance = pd.read_csv(instance_file_path)
    return instance


