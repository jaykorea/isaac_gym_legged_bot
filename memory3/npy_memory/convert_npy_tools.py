import numpy as np
import pickle
import os

def convert_pkl_episodes_to_npy(pkl_file_path, npy_file_path):
    # Load the data from the pkl file
    with open(pkl_file_path, 'rb') as f:
        memory_utils_instance = pickle.load(f)

    # Ensure the data is an instance of MemoryUtils
    if not hasattr(memory_utils_instance, 'episodes'):
        print(f"[Error] The pkl file {pkl_file_path} does not contain 'episodes' attribute.")
        return

    episodes = memory_utils_instance.episodes

    # Save all episodes to a single npy file
    np.save(npy_file_path, episodes)

    print(f"All episodes from {pkl_file_path} have been saved to {npy_file_path}.")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    load_pkl_files = [os.path.join(current_dir, f"memory3/raw_memory{i+1}.pkl") for i in range(20)]
    output_npy_files = [os.path.join(current_dir, f"memory3/npy_memory{i+1}.npy") for i in range(20)]

    for pkl_file, npy_file in zip(load_pkl_files, output_npy_files):
        print(f"Converting {pkl_file} to {npy_file}")
        convert_pkl_episodes_to_npy(pkl_file, npy_file)
