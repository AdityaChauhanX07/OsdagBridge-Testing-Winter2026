# Test environment and setup notes

## Machine
- Windows 11 (64-bit, x86_64), Intel Raptor Lake-S Mobile Graphics, OpenGL 4.6
- Miniconda (conda 26.9.4), Git 2.53.0
- A second, headless run of the automated suite was done on Linux using the same `environment.yml`.

## Software under test
- Repository: https://github.com/Nidhikhare12/OsdagBridge, branch `dev`
- Commit: `d74f56dd7f22925fb8148cabf5740ed8d1e39ff3`. Tested as published; no changes made to OsdagBridge's code.
- Conda env `osdagbridge-env`, created with `conda env create -f environment.yml`:
  python 3.12.16, osdag 2026.04.0.0, pyside6 / qt6-main 6.11.3, pythonocc-core 8.0.1.2,
  numpy 2.5.4, scipy 1.18.1, pandas 3.1.1, matplotlib 3.11.2, openseespy 3.8.0.0, osdagbridge 1.0.0 (editable install)

## Setup problems and how they were solved
1. **Anaconda Terms of Service prompt.** conda 26.x asks you to accept the ToS for the `defaults` channels when creating the env.
   I declined and removed `defaults` from both config files:
   `conda config --remove channels defaults` (user `.condarc`) and
   `conda config --file C:\Users\<user>\miniconda3\.condarc --remove channels defaults` (installation `.condarc`).
   After that, the environment builds from conda-forge and the osdag channels only.
2. **Running the logger from inside the OsdagBridge folder.** The testing scripts are kept in a separate repository, so the
   OsdagBridge working tree stays clean (`git status` empty). They are run from `OsdagBridge\src` so that
   `import osdagbridge` resolves to the checked-out code.
3. **Linux only:** the `osdag_core` package shipped its SQLite database as a `.sql` dump with an empty `.sqlite` file.
   I rebuilt it from the dump (`sqlite3.executescript`). Windows already had the database.

## How the GUI runs were recorded
`python ..\..\OsdagBridge-Testing-Winter2026\scripts\run_logged.py <LABEL>` from `OsdagBridge\src` (osdagbridge-env active).
Each Design click writes the UI input dict, the backend input dict, the full output dict, run metadata and a diff
against the previous run into `runs\<timestamp>_<LABEL>\` inside the testing repository. The two manual sessions
kept as evidence are in `gui_runs/`.
