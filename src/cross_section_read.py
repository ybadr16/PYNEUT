from .physics import calculate_E_cm_prime
import os
import h5py
import numpy as np

class CrossSectionReader:
    def __init__(self, base_path: str):
        """
        Initialize the CrossSectionReader with the base path to the data files.
        :param base_path: Base directory where HDF5 files are located.
        """
        self.base_path = base_path

    def get_cross_section(self, element: str, mt: int, energy: float) -> float:
        """
        Get the cross-section for a specific nuclide, reaction, and energy.
        Handles both Global and Local energy grids.
        """
        # Validate inputs
        if not element.isalnum():
            raise ValueError("Invalid element format. Use alphanumeric characters (e.g., U235, Pb208).")
        if not (1 <= mt <= 999):
            raise ValueError("MT number must be between 1 and 999.")

        mt_str = f"{mt:03}"
        file_path = os.path.join(self.base_path, f"neutron/{element}.h5")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"HDF5 file for {element} not found at {file_path}.")

        # Paths
        reaction_group_path = f"{element}/reactions/reaction_{mt_str}/294K"
        global_energy_path = f"{element}/energy/294K"

        try:
            with h5py.File(file_path, 'r') as f:
                if reaction_group_path not in f:
                    return 0.0

                rx_group = f[reaction_group_path]

                # --- FIX START: Check for Local Energy Grid ---
                if "energy" in rx_group:
                    # CASE A: Use Local Grid (Exact Match)
                    # This prevents the resonance shifting bug
                    grid_energy = rx_group["energy"][:]
                    grid_xs = rx_group["xs"][:]

                    if energy < grid_energy[0] or energy > grid_energy[-1]:
                        return 0.0

                    return np.interp(energy, grid_energy, grid_xs)
                # --- FIX END ---

                else:
                    # CASE B: Use Global Grid + Threshold (Old Logic)
                    if global_energy_path not in f:
                         raise KeyError(f"Energy data path '{global_energy_path}' not found.")

                    global_energy = f[global_energy_path][:]
                    xs_data = rx_group["xs"][:]
                    threshold_idx = rx_group["xs"].attrs.get('threshold_idx', 0)

                    # Safety check on indices
                    if threshold_idx + len(xs_data) > len(global_energy):
                        len_to_use = len(global_energy) - threshold_idx
                        xs_data = xs_data[:len_to_use]

                    # Slice the global grid
                    relevant_energies = global_energy[threshold_idx : threshold_idx + len(xs_data)]

                    if energy < relevant_energies[0]:
                        return 0.0

                    return np.interp(energy, relevant_energies, xs_data)

        except (OSError, KeyError, ValueError) as e:
            if "reaction" in str(e) or "not found" in str(e):
                return 0.0
            raise RuntimeError(f"Error reading {element} MT={mt}: {e}") from e

    def calculate_macroscopic_xs(self, microscopic_xs: float, number_density: float) -> float:
        if microscopic_xs < 0: return 0.0
        microscopic_xs_cm2 = microscopic_xs * 1e-24
        return microscopic_xs_cm2 * number_density

    def get_macroscopic_xs(self, element: str, mt: int, energy: float, number_density: float) -> float:
        microscopic_xs = self.get_cross_section(element, mt, energy)
        return self.calculate_macroscopic_xs(microscopic_xs, number_density)

    def get_cross_sections(self, element, energy, sampler, number_density):
        # 1. Scattering (MT=2)
        # Note: We use E_lookup = energy (Lab Frame) for XS lookup
        E_lookup = energy

        Sigma_s = self.get_macroscopic_xs(element, 2, E_lookup, number_density)
        Sigma_a = self.get_macroscopic_xs(element, 102, E_lookup, number_density)

        try:
            Sigma_f = self.get_macroscopic_xs(element, 18, E_lookup, number_density)
        except:
            Sigma_f = 0.0

        Sigma_t = Sigma_s + Sigma_a + Sigma_f
        return Sigma_s, Sigma_a, Sigma_f, Sigma_t
