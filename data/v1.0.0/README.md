# Research data for “Normal representation recovery and score geometry in noisy anomalous sound detection: a controlled audit”

**Version 1.0.0** · Zhijian Yang, Quanan Qiu, Xuegang Kong, Rong Luo and Zhengzheng Deng.

These data support a controlled comparison between recovering clean normal features and ranking anomalous machine recordings under added noise. The main comparison covers nine DCASE 2024 and eight DCASE 2025 machine-year cases. Post-hoc analyses use previously examined 2026 development fan and five-machine evaluation data. Repeated noise conditions, controls and reference interfaces reuse the same recordings.

## Finding and using the data

| Location | Contents |
|---|---|
| `results/E4`–`results/E10` | Machine scores, metrics and contrasts for BEATs and ECHOv2, including angular recovery, reference-interface, permutation and noise-window comparisons. |
| `results/E11`, `results/E12` | Single-fan spatial and calibration diagnostics. For domain AUC and per-machine H, use `results/E12/E11_corrected_metrics.csv`. The older E11 table uses within-domain comparisons and is retained for audit. |
| `supplementary/E11_E13_portable_audit_with_replay_20261030.zip` | Score-based E11/E12 audit, 200 public fan development filenames with class and domain parsed from the names, and E13 execution evidence for 900 recordings and 1,800 feature views. |
| `results/E14`, `results/E15` | Five-machine spatial diagnostic and replay evidence for 4,000 recordings and 8,000 individual channel comparisons. |
| `results/E18`, `reproducibility/E18` | Effect of leaving out one of the eight fixed noise conditions. The E18 ZIP provides the input tables, analysis, validator and results. |
| `reproduce`, `recipes`, `protocols`, `maintainer_scripts`, `provenance` | Replay recipes, input hashes, study protocols, original project code and recorded execution checks. Paths beginning with `experiments/` identify expected locations within a user-supplied data or project root. |
| `manifest.json` | SHA-256 and byte count for every other top-level archive member, including both nested ZIP files. |

Across the study stages there are 8,243,000 query-score rows. A score row represents one application of a particular scoring procedure to a recording under a particular condition. Read the column headers and protocols before pooling. In E6, `D_angle` is shuffled minus paired angular error, `D_H` is paired minus shuffled composite H and `D_T` is the paired minus shuffled oracle TPR at a 10% false-positive budget. In E7, `noisy_D_H_vs_joint` and `original_D_H_vs_joint` compare original-reference and jointly mapped reference banks on noisy and original queries.

## Redraw Figures 1 and 2

Download the data ZIP and its companion `plot_from_data_archive.py` into the same directory. With Python 3.12, install the reference plotting dependencies and run:

```sh
python -m pip install matplotlib==3.9.4 numpy==1.26.4 Pillow==12.3.0
python -I plot_from_data_archive.py research_data_v1.0.0.zip --output figures
```

Leave the archive compressed and choose a new output directory. The script checks the archive and the two plotting CSVs, then exports two PNGs, two PDFs, the coordinates and a validation receipt. Figure 1 plots 51 machine/view records twice. Figure 2 plots 18 view/year/method records twice. The study tables and the figure coordinates are fixed across the November release and the earlier October 31 archive.

## Check the score tables and sensitivity analyses

Unpack the top-level ZIP into a new directory. Keep the original ZIP available. From the extracted directory run the following command, replacing the archive argument with its path.

```sh
python reproduce/verify_E12_archive_portable_20261030.py PATH_TO_DATA_ZIP
```

For the E11/E12 label-based metric check, extract the nested E11–E13 audit into a separate directory. Run the following command there. It checks the 56 E12 FPR/FNR rows and the 28 corrected E11 domain AUC/pAUC/H rows.

```sh
python verify_E11_E12_metrics_portable_20261030.py PATH_TO_DATA_ZIP E11_E12_derived_test_filename_index_20261030.csv
```

For the E18 calculation, extract its nested archive and run the following two commands from that archive's root. Use a temporary working copy for execution.

```sh
python experiments/src/e18_leave_one_condition_20261031.py
python experiments/src/e18_validate_20261031.py
```

The code for E4/E5 audio replay checks separately acquired recordings, software trees and checkpoints against the recipe hashes. E9/E10 and the 2026 audio-to-feature analyses additionally use original workspace artifacts. The recorded execution checks describe historical runs on previously examined material. The E11–E13 index derives its annotations directly from the public DCASE 2026 fan development filenames. Evaluation-set labels needed by the earlier metric programs must be acquired from the official evaluators.

## Attribution and licenses

The authors license their derived scores, metrics, recipes, protocols and reports under [Creative Commons Attribution–NonCommercial–ShareAlike 4.0 International](https://creativecommons.org/licenses/by-nc-sa/4.0/), subject to applicable source rights. The authors' original Python code, including the separate plotting script, is distributed under the MIT License in `LICENSE-MIT.txt`. The source data providers below supplied the recordings and filename conventions. This study selected subsets and channels, mixed noise under fixed conditions, encoded features, fitted recovery maps and produced scores and comparisons. The fan index also parses domain and class from public development filenames. Source recordings, weights, feature arrays, fitted maps, third-party source trees and official evaluation ground-truth files must be obtained separately.

The seven DCASE dataset records each identify CC BY-NC-SA 4.0 as the source license. Credit also belongs to the dataset creators below. The 2024 records credit Hitachi, NTT and STMicroelectronics. The 2025 training record credits Hitachi and NTT, the 2025 evaluation record also credits STMicroelectronics, and the 2026 records credit Hitachi and NTT.

- **DCASE 2024 Challenge Task 2**. Tomoya Nishida, Keisuke Imoto, Noboru Harada, Daisuke Niizumi, Davide Albertini, Roberto Sannino, Simone Pradolini, Filippo Augusti, Kota Dohi, Harsh Purohit, Takashi Endo and Yohei Kawaguchi. [Additional Training Dataset, v2](https://doi.org/10.5281/zenodo.11259435) · [Evaluation Dataset, v1](https://doi.org/10.5281/zenodo.11363076).
- **DCASE 2025 Challenge Task 2**. Tomoya Nishida, Noboru Harada, Daisuke Niizumi, Davide Albertini, Roberto Sannino, Simone Pradolini, Filippo Augusti, Keisuke Imoto, Kota Dohi, Harsh Purohit, Takashi Endo and Yohei Kawaguchi. [Additional Training Dataset, v1](https://doi.org/10.5281/zenodo.15392814) · [Evaluation Dataset, v1](https://doi.org/10.5281/zenodo.15519362).
- **DCASE 2026 Challenge Task 2**. Tomoya Nishida, Noboru Harada, Daiki Takeuchi, Daisuke Niizumi, Keisuke Imoto, Kota Dohi, Harsh Purohit, Takashi Endo and Yohei Kawaguchi. [Development Dataset, v1, fan subset](https://doi.org/10.5281/zenodo.19336329) · [Additional Training Dataset, v1](https://doi.org/10.5281/zenodo.20151556) · [Evaluation Dataset, v1](https://doi.org/10.5281/zenodo.20437238).
- **Encoders and evaluators**. The study used the separately supplied ECHOv2 source and small checkpoint and a BEATs-family checkpoint from a pinned mirror. Upstream byte equivalence for the latter is unverified. Use the hashes in the study recipes and the original terms supplied by each provider. [ECHOv2 source](https://github.com/yucongzh/ECHOv2/tree/b2fb58549f343dfcf6271a600e1280945d647334) · [ECHOv2 weights](https://huggingface.co/yucongzh/echo-small-v2/tree/234c2cc250225a1915f8bad964bb6f3aa7d5109f) · [BEATs checkpoint mirror](https://huggingface.co/lpepino/beats_ckpts/tree/5b53b0404df452a3a607d7e67687227730e5bad1) · [2024 evaluator](https://github.com/nttcslab/dcase2024_task2_evaluator/tree/b5d17f63769bf4372a5412a7ede1f814c9590047) · [2025 evaluator](https://github.com/nttcslab/dcase2025_task2_evaluator/tree/f903124a40a4cdb3faf2b2d6fa69c6a9f1794192).

A separate snapshot of the authors' early replay code is available in the [ACA code archive](https://github.com/yangzj6677/ACA/blob/f8294167a11b1b7b4ff335da02603bfad7c6aead/ACA_github_ready_20261029.zip).

## Cite this dataset

Yang, Z., Qiu, Q., Kong, X., Luo, R., & Deng, Z. (2026). Research data for “Normal representation recovery and score geometry in noisy anomalous sound detection: a controlled audit” (Version 1.0.0) [Data set]. Zenodo. Use the version-specific DOI shown on the Zenodo record when citing this release.
