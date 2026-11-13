# ATLAS stated against delivered: Google Cloud region carbon intensity against EPA's state record (28 Oct 2026)
Written and committed before any EPA state figure was set beside any Google figure.

## Statement
Google Cloud publishes, per region, a "Grid carbon intensity (gCO2eq / kWh)" and defines it as "the average operational gross emissions per unit of energy from the grid" (region-carbon-info README, GoogleCloudPlatform on GitHub). Files: data/yearly/2023.csv and 2024.csv, saved here with sha256 in SOURCES.sha256.

## Record
EPA eGRID, state output emission rate for CO2 in lb per MWh, as already built into ATLAS (atlas/electricity/carbon.json, data year stated in that file). Converted by 1 lb/MWh = 0.45359237 g/kWh. The state is the state of the region's named location: Iowa, Oklahoma, South Carolina, Georgia, Virginia, Ohio, Texas, Oregon, California, Utah, Nevada. Non-US regions and regions that are not one state are left out and listed.

## Rule (fixed here)
Ratio = Google figure divided by the EPA figure. CONSISTENT if the ratio is from 0.75 to 1.25. ABOVE if the ratio is above 1.25, BELOW if under 0.75. The band is wide on purpose: Google's figure is CO2 equivalent and EPA's is CO2 only, and the EPA figure follows where electricity is generated in the state while a data center buys across state lines. A result outside the band is a real gap between the two quantities. A result inside it is only that the two are not far apart. Both years are shown. If the eGRID data year differs from the Google year, each Google year is compared with the same EPA figure and the year is printed.

## What is not compared
Google's carbon free energy percentage. EPA publishes no counterpart, so the outcome is CANNOT_TELL and the figure is shown as stated. No operator other than Google publishes a regional figure in a machine readable file; none is compared.

## Output
One table on the ATLAS carbon page: region, state, Google 2023 and 2024, EPA, ratios, outcome, with a vendor-response path. Every printed figure gets a ledger row. No ranking.
