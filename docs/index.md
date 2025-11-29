# Monte Carlo Neutron Transport Simulation

A Python-based Monte Carlo code for simulating neutron transport through various materials and geometries. **Intended for educational purposes only.**

[![Python 3.x](https://img.shields.io/badge/python-3.x-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## Quick Links

- [🚀 Quick Start Guide](quick-start.md) - Get started in 5 minutes
- [📖 API Reference](api-reference.md) - Complete function documentation
- [🐛 Known Issues](bugs-and-fixes.md) - Bug reports and improvements
- [⚠️ Critical Fixes](critical-fixes.md) - Important bugs to fix first

---

## Features

✅ Energy-dependent cross sections (ENDF/B-VIII data)  
✅ Thermal scattering with Maxwell-Boltzmann sampling  
✅ Multi-region geometry (cylinders, planes, spheres, boxes)  
✅ Parallel processing via multiprocessing  
✅ Optional trajectory tracking  

---

## Installation

```bash
git clone https://github.com/yourusername/monte-carlo-shielding.git
cd monte-carlo-shielding
pip install -e .
```

See [requirements.txt](https://github.com/yourusername/monte-carlo-shielding/blob/main/requirements.txt) for dependencies.

---

## Quick Example

```python
from src.cross_section_read import CrossSectionReader
from src.material import Material
from src.medium import Region, Cylinder, Plane
from src.simulation import simulate_single_particle
from multiprocessing import Pool

# Initialize
reader = CrossSectionReader("./endfb")
lead = Material("Lead", 11.35, 208, 2.5)

# Define geometry - lead cylinder
regions = [
    Region(
        surfaces=[Cylinder("z", 10, (0,0,0)), 
                  Plane(0,0,-1,10), Plane(0,0,1,10)],
        name="Shield", element="Pb208"
    )
]

# Simulate 100 neutrons
# ... (see Quick Start for complete example)
```

[View full example →](quick-start.md#example-1-simple-slab-shielding)

---

## ⚠️ Important: Apply Critical Fixes First

This code has **5 critical bugs** that must be fixed before use:

1. **Cylinder.normal()** - Method indentation error
2. **Plane normalization** - Sign convention inconsistency
3. **Duplicate Box class** - Defined twice
4. **Missing fission handling**
5. **Region detection counter bug**

**Fix in 30 minutes:** [See Critical Fixes →](critical-fixes.md)

```bash
# Quick fix
cp medium_FIXED.py src/medium.py
cp simulation_FIXED.py src/simulation.py
python test_fixes.py
```

---

## Physics Models

- **Elastic scattering**: Thermal motion via Maxwell-Boltzmann sampling
- **Absorption**: Radiative capture (MT=102)
- **Fission**: Basic tracking (no daughter neutrons yet)
- **Cross sections**: ENDF/B-VIII data, linearly interpolated

---

## Documentation Structure

```
docs/
├── index.md              ← You are here
├── quick-start.md        ← Usage examples & tutorials
├── api-reference.md      ← Complete API documentation
├── bugs-and-fixes.md     ← Known issues & improvements
└── critical-fixes.md     ← Priority fixes (start here!)
```

---

## Testing

Run the test suite:

```bash
# Basic geometry tests
pytest tests/test_cylinder.py

# Verify bug fixes
python test_fixes.py
```

See [tests/](https://github.com/yourusername/monte-carlo-shielding/tree/main/tests) for comprehensive geometry validation.

---

## Validation Status

⚠️ **Not yet validated against established codes** (MCNP, OpenMC, etc.)

Before trusting results:
1. Apply critical bug fixes
2. Run all tests
3. Compare with analytical solutions
4. Benchmark against established codes

---

## Code Structure

```
src/
├── cross_section_read.py  # ENDF data reader
├── material.py            # Material properties
├── medium.py              # Geometry (Region, Plane, Cylinder, Sphere)
├── physics.py             # Scattering physics
├── vt_calc.py            # Thermal velocity sampling
├── geometry.py            # Boundary tracking
├── simulation.py          # Main transport loop
├── tally.py              # Results accumulation
└── random_number_generator.py
```

---

## Limitations

Current limitations:
- Single isotope per region
- Isotropic scattering in CM frame only
- Fixed temperature (294K)
- No secondary particles from fission
- Mono-energetic source only

See [roadmap](bugs-and-fixes.md#recommendations-for-improvement) for planned features.

---

## Contributing

Improvements welcome! Especially:
- Validation benchmarks
- Additional physics models
- Performance optimizations
- Bug fixes

---

## References

- [ENDF/B-VIII Nuclear Data](https://www.nndc.bnl.gov/endf/)
- Lux & Koblinger: *Monte Carlo Particle Transport Methods*
- Duderstadt & Hamilton: *Nuclear Reactor Analysis*

---

## License

[MIT License](LICENSE) - Free for educational and research use.

---

## Contact

**Youssef**  
Nuclear and Radiation Engineering  
Alexandria University, Egypt

[GitHub Repository](https://github.com/yourusername/monte-carlo-shielding) • [Report Issues](https://github.com/yourusername/monte-carlo-shielding/issues)

---

<p align="center">
  <em>⚠️ Disclaimer: For educational purposes only. Not validated for production use.</em>
</p>
