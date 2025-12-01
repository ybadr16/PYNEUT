from src.cross_section_read import CrossSectionReader
from src.vt_calc import VelocitySampler
from src.simulation import simulate_single_particle
from src.material import Material
from src.medium import Region, Sphere
from src.tally import Tally
from src.random_number_generator import RNGHandler
from src.settings import Settings
from multiprocessing import Pool
import time
import numpy as np

def benchmark():
    # 1. SETUP
    base_path = "./endfb"
    reader = CrossSectionReader(base_path)

    # 2. MATERIAL: Pure Pb-208
    # Note: Use specific mass for Pb208 to match OpenMC
    pb_mass_kg = 207.9766521 * 1.660539e-27
    lead = Material(name="Lead", density=11.35, atomic_mass=207.97, atomic_weight_ratio=207.2)

    N = lead.number_density
    A = lead.atomic_weight_ratio
    sampler = VelocitySampler(mass=pb_mass_kg)

    # 3. GEOMETRY: Sphere R=10
    # A single sphere region. Inside is Lead.
    # Note: Ensure your Region logic handles a single surface correctly.
    lead_sphere = Region(
        surfaces=[Sphere((0,0,0), 10.0)],
        name="LeadSphere",
        priority=1,
        element="Pb208"
    )

    # We need a void "World" or just assume everything else is void?
    # Your code loops through mediums. If no medium found, it returns "escaped".
    # So just defining the sphere is enough.
    mediums = [lead_sphere]

    # 4. SETTINGS
    # Shielding mode = Implicit Capture (Matches OpenMC default)
    N_PARTICLES = 10000
    settings = Settings(mode="shielding", particles=N_PARTICLES)

    rngs = [RNGHandler(seed=12345 + i) for i in range(N_PARTICLES)]
    tally = Tally()

    # 5. SOURCE: Point(0,0,0), 1 MeV
    particle_states = [
        {
            "x": 0.0, "y": 0.0, "z": 0.0,
            # Isotropic direction
            "theta": np.arccos(1 - 2 * rng.random()), # Sample cos(theta) uniformly
            "phi": rng.uniform(0, 2 * np.pi),
            "has_interacted": False,
            "energy": 1.0e6,  # 1 MeV
            "weight": 1.0
        }
        for rng in rngs
    ]

    args = [
        (state, reader, mediums, A, N, sampler, None, False, rng, settings)
        for state, rng in zip(particle_states, rngs)
    ]

    print(f"Starting Benchmark: Pb-208 Sphere (R=10cm), 1 MeV Source")

    with Pool() as pool:
        partial_results = pool.map(simulate_single_particle, args)

    # 6. ANALYZE RESULTS
    total_weight_escaped = 0.0
    escaped_energies = []

    for res in partial_results:
        # In Implicit capture (Shielding), particles "escape" with a weight.
        # "escaped" means they hit the boundary.
        # "killed" means they died via Roulette inside.

        if res["result"] == "escaped":
            w = res["final_weight"]
            e = res["final_energy"]
            total_weight_escaped += w
            # Weighted average calculation
            escaped_energies.append((e, w))

    # Calculate Metrics
    leakage_fraction = total_weight_escaped / N_PARTICLES

    if escaped_energies:
        numerator = sum(e * w for e, w in escaped_energies)
        denominator = sum(w for _, w in escaped_energies)
        avg_escape_energy = numerator / denominator
    else:
        avg_escape_energy = 0.0

    print("="*40)
    print(f"MY CODE RESULTS")
    print("="*40)
    print(f"Total Particles: {N_PARTICLES}")
    print(f"Leakage Fraction: {leakage_fraction:.5f}")
    print(f"Avg Escape Energy: {avg_escape_energy:.2f} eV")
    print("="*40)

if __name__ == "__main__":
    benchmark()
