# Dual Coupling in Elastic Spacetime: Gravity as the Stabilizing Restoring Force of Topological Matter

This repository contains the complete computational framework, source codes, and generated figures for the manuscript titled *"Dual Coupling in Elastic Spacetime: Gravity as the Stabilizing Restoring Force of Topological Matter"*.

## Overview

The project investigates whether a single mechanical mechanism—the elastic response of a continuous fabric—can simultaneously explain the origin of gravitational lensing and the dynamical stability of matter. It uses Fast Fourier Transform (FFT) relaxation on a 3D elastic lattice and acoustic metric integrations to recover the General Relativistic deflection law (4M/b) and resolve the thermodynamic paradox.

## Quick Start (Reproducibility)

To generate all the figures and the LaTeX manuscript from scratch, simply run the build script:

    python build_project.py

This script will:
1. Create all necessary directories.
2. Write the Python simulation codes (`simulate.py`) for all 6 modules.
3. Execute the simulations to generate the publication-ready figures.
4. Write the `paper.tex` file, ready for compilation.

## Requirements

Ensure you have Python 3.8+ installed. Install the required dependencies via:

    pip install -r requirements.txt

## Directory Structure

After running `build_project.py`, the following structure will be created:
* `paper.tex`: The complete LaTeX source code for the manuscript.
* `01_Topological_Visuals/`: Visual representation of six topological profiles.
* `02_Lensing_Discrimination/`: Deflection angle comparison (Open Sink vs. closed structures).
* `03_Elastic_Flow/`: Velocity flow field from the elastic potential.
* `04_Tensor_Lensing/`: Effective acoustic metric and light deflection (Analytical stitching).
* `05_Robustness_Analysis/`: Grid convergence and Lamé parameter sensitivity.
* `06_Dynamical_Stability/`: 1D soliton stability (nonlinear binding vs. linear dispersion).
* `*.png`: The 6 generated figures ready to be uploaded to Overleaf.

## Compiling the Paper

The generated `paper.tex` is ready to be uploaded to Overleaf (or compiled locally using `pdflatex`). Ensure that all `.png` images generated in the root directory are uploaded alongside the `.tex` file.

## Declaration of Generative AI Use

The author utilized an AI language model for assistance in drafting, structuring, and refining the manuscript text, as well as optimizing the Python code for numerical integration. The author reviewed and edited all content, verified all mathematical equations and references, and takes full responsibility for the accuracy and integrity of the work.

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.
