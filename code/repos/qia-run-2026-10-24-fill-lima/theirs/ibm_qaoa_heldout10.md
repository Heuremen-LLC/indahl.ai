# IBM QAOA Held-out 10 Graphs

Ultima actualizacion: 2026-05-05

## Objetivo

Ejecutar una ultima replicacion IBM QAOA pre-especificada para evidencia secundaria de hardware.
No estima exponentes ni valida la ley asintotica; solo verifica consistencia end-to-end del pipeline en hardware real.

## Protocolo

```text
phase: ibm_qaoa_heldout10
circuito: QAOA MaxCut random graph
n_qubits: 5
depth: r=1
graph seeds: [606, 707, 808, 909, 1001, 1102, 1203, 1304, 1405, 1506]
scale factors: [1, 3]
shots: 4000 por escala
backend predefinido: ibm_marrakesh
plan: IBM Open Plan
criterio PASS: ZNE mejora al menos 7/10 grafos y reduce el error absoluto medio
```

Antes de enviar el job se verifico:

```text
active account: name='open'
plan: open
usage before run: 34/600 s
remaining before run: 566 s
```

## Runner

```powershell
python -m zne_qiskit_validation.runners.run_ibm_qaoa_heldout10 --submit --backend ibm_marrakesh --shots 4000 --plans-preference open
```

## Artefactos

```text
results/processed/ibm_qaoa_heldout10_summary.csv
results/checkpoints/ibm_qaoa_heldout10_counts.csv
results/raw/ibm_qaoa_heldout10/*.json.gz
logs/ibm_qaoa_heldout10_20260505_174604.log
```

## Resultado

```text
status: PASS
result_label: HELDOUT_PASS
backend: ibm_marrakesh
job_id: d7t76dkt738s73chg7i0
measurement_rows: 20
per_graph_rows: 10
raw count files: 20
```

Agregado:

| Metrica | Valor |
|---|---:|
| Grafos | 10 |
| ZNE mejora | 9/10 |
| lambda=3 degrada | 10/10 |
| ZNE en rango fisico | 10/10 |
| Error medio lambda=1 | 0.064448 |
| Error medio ZNE | 0.028104 |

Uso IBM posterior:

```text
usage after run: 61/600 s
remaining after run: 539 s
additional consumed: 27 s
```

## Tabla por grafo

| Graph seed | Edges | Ideal | lambda=1 | lambda=3 | ZNE | Error lambda=1 | Error ZNE | Mejora |
|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 606 | 6 | -0.426375 | -0.385833 | -0.316750 | -0.420375 | 0.040542 | 0.006000 | si |
| 707 | 6 | -0.521519 | -0.459250 | -0.345583 | -0.516083 | 0.062269 | 0.005436 | si |
| 808 | 8 | -0.526298 | -0.409750 | -0.304438 | -0.462406 | 0.116548 | 0.063892 | si |
| 909 | 6 | -0.426375 | -0.373667 | -0.310667 | -0.405167 | 0.052708 | 0.021208 | si |
| 1001 | 7 | -0.486360 | -0.397571 | -0.343429 | -0.424643 | 0.088788 | 0.061717 | si |
| 1102 | 6 | -0.573350 | -0.507667 | -0.393333 | -0.564833 | 0.065683 | 0.008517 | si |
| 1203 | 5 | -0.535553 | -0.491200 | -0.411200 | -0.531200 | 0.044353 | 0.004353 | si |
| 1304 | 2 | -0.411068 | -0.418500 | -0.414500 | -0.420500 | 0.007432 | 0.009432 | no |
| 1405 | 5 | -0.535553 | -0.464500 | -0.373900 | -0.509800 | 0.071053 | 0.025753 | si |
| 1506 | 6 | -0.521519 | -0.426417 | -0.385667 | -0.446792 | 0.095102 | 0.074727 | si |

## Lectura cientifica

Esta corrida fortalece la evidencia de hardware consistency:

```text
The pre-specified held-out IBM QAOA replication improved the ZNE estimate in 9/10 cases and reduced mean absolute error from 0.06445 to 0.02810.
```

No debe presentarse como estimacion de la frontera asintotica ni como prueba de exponentes en hardware. La afirmacion correcta es que el pipeline QAOA + folding + raw-count persistence + Richardson ZNE funciona en hardware real en un batch held-out predefinido.
