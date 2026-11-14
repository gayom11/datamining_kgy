# Exact Facts for Report (Solar Pro4는 아래 수치만 인용할 것)

## 보고서에서 인용할 수 있는 정확한 수치들. 이 문서에 없는 수치는 절대 만들어내지 말 것.

### Shared Drug Targets (ChEMBL bioactivity, Human targets)
| Drug Pair | Shared Targets | Jaccard |
|---|---|---|
| Morphine-Diazepam | 24 | 0.089 |
| Diazepam-Ketamine | 20 | 0.075 |
| Cocaine-Diazepam | 18 | 0.072 |
| Fentanyl-Diazepam | 17 | 0.066 |
| Morphine-Ketamine | 17 | 0.064 |

### PPI Hub Proteins (STRING, score > 400)
| Protein | Degree | Function |
|---|---|---|
| SLC6A4 (SERT) | 36 | Serotonin transporter |
| MAOA | 35 | Monoamine oxidase A |
| MAOB | 34 | Monoamine oxidase B |
| BDNF | 34 | Brain-derived neurotrophic factor |
| COMT | 33 | Catechol-O-methyltransferase |
| SLC6A3 (DAT) | 30 | Dopamine transporter |
| DRD2 | 30 | Dopamine receptor D2 |
| GRIN2B | 30 | NMDA receptor subunit |
| HTR2A | 29 | Serotonin receptor 2A |
| TH | 26 | Tyrosine hydroxylase |

### Drug-Disease Gene Overlap (top 10, NCBI Gene × NCBI disease genes)
| Chemical | Disease | Overlap Genes |
|---|---|---|
| Cocaine | Depressive Disorder | 22 |
| Cocaine | Schizophrenia | 21 |
| Morphine | Schizophrenia | 20 |
| Cocaine | Neurotoxicity | 20 |
| Methamphetamine | Depressive Disorder | 20 |
| Cocaine | Parkinson Disease | 17 |
| Cocaine | Alzheimer Disease | 17 |
| Methamphetamine | Schizophrenia | 17 |
| Morphine | Neurotoxicity | 18 |
| Morphine | Seizures | 17 |

### Neurological Adverse Events (OpenFDA FAERS)
| Chemical | N_Neuro_AE_Types | Total_Neuro_Reports | Top_AE (count) |
|---|---|---|---|
| Diazepam | 18 | 37,315 | Somnolence (3,769) |
| Cocaine | 16 | 5,383 | Coma (1,235) |
| Ketamine | 15 | 5,134 | Sedation (600) |
| Methamphetamine | 14 | 1,166 | Anxiety (112) |
| Morphine | 13 | 42,582 | Headache (6,491) |
| Fentanyl | 12 | 26,462 | Anxiety (3,239) |
| THC | 11 | 1,215 | Headache (193) |
| MDMA | 11 | 76 | Somnolence (23) |

### Neuro AE Ratio (neuro reports / total reports)
| Chemical | Ratio |
|---|---|
| Diazepam | 19.4% |
| MDMA | 16.5% |
| Ketamine | 14.4% |
| Cocaine | 10.9% |
| Morphine | 10.7% |
| THC | 10.2% |
| Fentanyl | 9.9% |
| Methamphetamine | 5.4% |

### HIGH Risk Combinations
| Inhibitor | Victim | CYP | Strength | Risk |
|---|---|---|---|---|
| Cocaine | Fentanyl | CYP3A4 | Moderate | HIGH |
| Cocaine | Diazepam | CYP3A4 | Moderate | HIGH |
| Cocaine | Ketamine | CYP3A4 | Moderate | HIGH |
| Cocaine | THC | CYP3A4 | Moderate | HIGH |

### Additional Important Combination (not in CYP3A4 screen but HIGH risk by different mechanism)
| Inhibitor | Victim | CYP | Strength | Note |
|---|---|---|---|---|
| MDMA | Methamphetamine | CYP2D6 | Strong (mechanism-based) | Irreversible inhibition, 30-50% clearance reduction estimate |

### Database Record Counts
| Database | Records |
|---|---|
| PubChem | 1,062 |
| ChEMBL | 1,801 |
| KEGG | 2,426 |
| STRING | 478 |
| UniProt | 53 |
| Open Targets | 800 |
| NCBI Gene | 388 |
| OpenFDA | 800 |
| Pharmacogenomics | 56 |
| Total | ~7,864 |

### PPI Network Summary
- Total interactions: 478
- Total proteins: 52
- Confidence score threshold: > 400

### CYP Polymorphism Frequencies
| CYP Gene | PM Frequency |
|---|---|
| CYP2D6 | PM: 5-10% Caucasian, 1-2% Asian |
| CYP2C19 | PM: 2-5% Caucasian, 15-20% Asian |
| CYP2C9 | PM: 1-3% Caucasian |
