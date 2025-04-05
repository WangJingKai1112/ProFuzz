# ProFuzz

ProFuzz is a program-level hardware fuzzing method for processor core verification. Here, the brief workflow of ProFuzz is showcased.

### Workflow Overview

[](./Figure/ProFuzz.png)

### Directory Structure Description

- Step1_Initialization: Construct the initial population.

- Step2_Mating: Select parent pairs for Evolutionary operations.

- Step3_Crossover: Evolution Engine - Crossover

- Step4_Mutation: Evolution Engine - Mutation

- Step5_Compilation: Compile the individuals in the population.

- Step6_Debugging_and_Rebooting: Debugging and Rebooting.

- Step7_Coverage: Run coverage testing and collect coverage information.

- Step8_Selection: Merge the coverage information and select the individuals for the next generation.

- Libs: Store the libraries used in ProFuzz.

- Utils: Store the tools and reusable functions used in ProFuzz.

- main.py

- run.sh: The script to run ProFuzz, you just need to `./run.sh` to run ProFuzz.

### Todo List

- TODO: Replace your own message.
    - Step1_Initialization/initialization.py
        - `YOUR_MODEL_NAME`.
    - Step6_Debugging_and_Rebooting/debugging.py
        - `YOUR_MODEL_NAME`.
    - Step7_Coverage/coverage.py
        - `YOUR_SIMULATION_INITIALIZATION_COMMAND`
        - `YOUR_SIMULATION_COMMAND`
        - `YOUR_COVERAGE_COMMAND`
    - Step8_Selection/merge.py
        - `YOUR_MERGE_COMMAND`
        - `YOUR_MERGE_REPORT_COMMAND`.
    - Utils/format_utils.py
        - `YOUR_API_KEY`
        - `YOUR_BASE_URL`
    - Utils/file_utils.py
        - `YOUR_MODEL_NAME`

- TODO: Install the required tools.
    - Step5_Compilation/openc910/
        - `Xuantie-C910`
    - Step5_Compilation/Xuantie-900-gcc-elf-newlib-x86_64-.../
        - `Xuantie-900-gcc-elf-newlib-x86_64-V2.0.3-20210806` or other versions
    - Step7_Coverage/env/
        - the simulation and coverage testing tools
    - Libs/csmith/
        - `Csmith`
    - Libs/tree-sitter/
        - `Tree-sitter`