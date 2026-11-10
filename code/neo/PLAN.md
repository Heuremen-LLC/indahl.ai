# NEO: stated close-approach distances against the later record. Plan, written before any stated distance was set beside a later one.

## Claim read
NASA's Center for Near-Earth Object Studies (CNEOS) at JPL publishes a table of close approaches to Earth by near-Earth objects. For each approach the table states a nominal distance, a minimum distance and a maximum distance. The SBDB Close-Approach Data API (version 1.5) defines them:
- dist: "nominal approach distance (au)".
- dist_min: "minimum (3-sigma) approach distance (au)".
- dist_max: "maximum (3-sigma) approach distance (au)".
- orbit_id: "orbit ID used for the close-approach computation".
The CNEOS table legend calls the minimum "the minimum possible close-approach distance" and says it "is based on the 3-sigma Earth target-plane error ellipse". The CNEOS uncertainties page (https://cneos.jpl.nasa.gov/ca/neo_ca_info.html) says: "Earth close-approach statistics for a given NEO can change (often by large amounts) as new data become available and the orbit is updated."

Question: when a later orbit solution replaces the one a distance was stated from, how often does the later distance fall inside the minimum to maximum range that was stated earlier, and how far does it move, by how long before the approach the statement was made?

JPL states the range as 3-sigma. JPL does not state a share of approaches that should fall inside it. Reading a 3-sigma range as one that should hold about 99.7 percent of later values is our reading, from a normal error model. It is named as ours wherever it is printed.

## Can earlier statements be fetched (scouted before this plan)
JPL serves the current solution only.
- Close-Approach Data API: "provides access to current close-approach data". It has no filter for solution date or older orbit IDs.
- SBDB API: returns one orbit (the current orbit_id with its solution date, condition code, data arc, first and last observation). Its alt-orbits option is documented as "typically only for comets" and returned an empty list for the asteroid tried.
- Horizons: the object header prints one solution ("soln ref.= JPL#80" with one solution date for the object tried). No option selects an older asteroid solution.
- Sentry API: a current list and a removed list. The removed list carries a designation and a removal time and no earlier values.
- MPC: Minor Planet Electronic Circulars are dated and archived and carry orbital elements. They carry no stated range for a close-approach distance.
So an earlier statement can be read only from a copy made at the time. Two such copies are used.

## Data
Stated side, part one: archived copies. The Internet Archive Wayback Machine holds copies of responses from https://ssd-api.jpl.nasa.gov/cad.api. Its index lists 83 copies with status 200 from 1 January 2024 to plan time. Each copy is a response JPL served at the archived time, with orbit_id, dist, dist_min and dist_max per approach. Every such copy is used if it parses, its signature source is the Close-Approach Data API, and its approach body is Earth (no body parameter, or body=Earth). Copies that hold a count only are listed and not used.
Stated side, part two: our own copies. From the first run on, each run of neo_tick.py stores the current response for Earth approaches of NEOs from 60 days back to 60 days ahead inside 0.2 au, at most one copy per 6 hours. They enter the stated side under the same rules as the archived copies. This is how the frame grows.

Delivered side. The current Close-Approach Data API record of the same approach, read at run time: the latest orbit solution's dist, dist_min, dist_max and orbit_id. For an approach that has passed, the latest solution may include observations made during and after the approach. The SBDB API gives the latest solution's date, condition code, data arc and last observation date, for display.

All sources are public and need no key. One request at a time, paced, with a user agent that names this desk. Every response is kept in data/raw.

## Frame (fixed now)
- Objects: every object in a used copy. No object is picked by us.
- Approaches: Earth approaches with a stated nominal distance of 0.05 au or less and an approach date on or after 1 January 2024.
- A statement counts as a projection only if the copy was made before the stated approach time. Statements copied after the approach are listed apart and not scored.
- A row is scored only after the approach time has passed at run time. Until then the row reads NOTHING_RETURNED.
- Match. The delivered record is the current record of the same designation whose approach time is nearest to the stated time and within 10 days of it. Ten days is the CNEOS table's own limit on 3-sigma time uncertainty. The lookup is by designation out to 0.5 au, so an approach that moved outside 0.05 au is still found.
- One row is one object, one approach, one stated orbit_id. The stated time of a row is the earliest copy that carries that orbit_id for that approach. Lead is the approach time minus that copy's time, in days.
- Headline row per approach: the row with the longest lead. Later statements of the same approach are scored and shown, and are not in the headline cells.

## Rules (fixed now)
Row outcome. Stated range is [stated dist_min, stated dist_max]. Delivered interval is [latest dist_min, latest dist_max], the latest solution's own 3-sigma range.
- CONSISTENT: the whole delivered interval is inside the stated range.
- ABOVE: the whole delivered interval is above the stated maximum (the object passed farther than the stated range).
- BELOW: the whole delivered interval is below the stated minimum (the object passed closer than the stated range).
- CANNOT_TELL, each reason counted apart:
  - same solution: the latest orbit_id equals the stated orbit_id, so no later solution exists.
  - wide range: stated dist_max minus dist_min is more than 0.05 au, wider than the frame itself.
  - edge: the delivered interval crosses an edge of the stated range.
  - no record: no current record within 10 days and 0.5 au.
  - unreadable: a stated or delivered value does not parse, or min is above max.
Values are compared at the precision JPL serves. No tolerance is added.

Cells. A cell is a set of headline rows. Its share is CONSISTENT rows over rows that read CONSISTENT, ABOVE or BELOW. CANNOT_TELL rows are shown beside every cell and are never folded into either side. The interval is a 95% Wilson interval. One object gives one headline row per approach, and an object with more than one approach in a cell is counted once by its earliest approach.
- Cells: all leads, and leads of 0 to 7 days, 8 to 30 days, and more than 30 days.
- Cell outcome against our 99.7 percent reading: BELOW if the interval's upper bound is under 0.9973. CONSISTENT if its lower bound is 0.98 or more. ABOVE if its lower bound is over 0.9973. Otherwise CANNOT_TELL. Fewer than 10 scored rows is CANNOT_TELL.
- At 95% a cell needs about 190 scored rows, all inside, to read CONSISTENT. The page says so if the sample is smaller.

Described and not scored: the shift of the nominal distance in units of the stated sigma, where sigma is (stated dist_max minus stated dist_min) divided by 6. Median absolute shift and the share beyond 1 sigma, by lead cell. The shift of the approach time against the stated 3-sigma time uncertainty. The latest solution's condition code and data arc.

Subset shown apart: approaches dated August 2026. The owner tracked objects that month. No note naming them was found in our files, so no object is singled out. The subset uses the same rows and rules and has no outcome of its own unless it holds 10 scored rows.

## Both alternatives
A. The stated ranges hold the later distance about as often as a 3-sigma range would under a normal error model. The cell reads CONSISTENT, or CANNOT_TELL with a share near 1.
B. The stated ranges hold the later distance less often than that. The cell reads BELOW.
Either result is printed the same way. A BELOW cell says how often a later solution left the range. It names no cause.

## Known-good gates (a failed gate turns every outcome into CANNOT_TELL)
1. Format. The current response's signature version is 1.5 and the field list holds des, orbit_id, jd, dist, dist_min, dist_max. Every used copy has the same fields.
2. Reader. Three stated rows read directly from the raw text of three archived copies equal the parsed rows. The rows are picked from the stated side only and written into CHECKS.md.
3. Join. Among rows whose latest orbit_id equals the stated orbit_id, the delivered dist equals the stated dist to 1 part in 100,000 in at least 95 percent of rows. A join that pairs the wrong approach fails this.
4. Rule. Synthetic rows with a known answer read ABOVE, BELOW, CONSISTENT and each CANNOT_TELL reason correctly, and heuremen_kit's self-test passes.

## Set aside
- Sentry impact probabilities and removals. A removal is a later record against an earlier probability, with no stated range to test. Each run stores the Sentry summary and removed lists so a later plan can use them. No outcome is given.
- Scout (objects on the NEO Confirmation Page). Not archived by JPL after confirmation.
- MPC circulars and orbits. No stated range for a close-approach distance.
- ESA NEOCC and NEODyS close-approach lists. Not read here.
- Our own orbit fits from earlier astrometry. That would be our statement, not JPL's.
- Approaches that never appear in a copy. The copies are what third parties and this desk happened to store. They are not a random sample of approaches, and the table itself holds only approaches inside the CNEOS limits (time uncertainty within 10 days and position uncertainty within 0.1 au, both 3-sigma).
- Approaches before 2024, approaches to other bodies, and stated distances beyond 0.05 au.

## Reading done before this plan was written
- The Wayback index of cad.api copies (times and addresses). The 83 copies were downloaded to data/raw/wayback and not opened or parsed.
- One current Close-Approach response for 1 to 10 August 2026 (the first six rows were seen), one current SBDB record (2024 YR4), the first rows of the current Sentry summary and removed lists, one Horizons object header (2024 YR4). All are current-solution values.
- The API documentation and the CNEOS close-approach legend and uncertainties page.
No stated distance from an earlier solution was set beside a later one.

## Terms recorded
- JPL SSD/CNEOS API fair use policy (https://ssd-api.jpl.nasa.gov/doc/index.php): requests limited to those reasonably necessary, results cached and reused, one request at a time, back off on errors, an application-specific User-Agent with product name, version and contact information, no embedding of the APIs in a website, formats can change without notice so the version field is checked.
- Internet Archive: copies are read through the public Wayback index and raw-copy addresses, paced.
- MPC: not used for values.
