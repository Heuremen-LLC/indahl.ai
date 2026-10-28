# Code

Scripts behind the tables on indahl.ai. Free to read, run and cite with attribution. See LICENSE.txt in the repository root.

- `sad/` builds and checks the Stated against Delivered sources, one claims checker per source.
- `iris/` holds the Faults and Guards bench (items, runner, scorer), the Falcon training plan and scripts, and the model claims round for SmolLM2.
- `coin/` collects block records from public explorers, recomputes block hashes from header fields, and checks a chain's stated claims against its own record. It reads public data only.

Each plan file is committed before the run it describes. Run any script with `python3 -I` from its own folder.
