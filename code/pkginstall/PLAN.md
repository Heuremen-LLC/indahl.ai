# PKGINSTALL: the install command a PyPI project's README gives against whether that command resolves. Plan, written before any command is run.

## Claim read
A PyPI project's description tells the reader to run a command such as pip install NAME. Stated: this command installs the project. Record: whether pip can resolve that command today, on a fresh environment, for a current Python.

## Population
The 1,000 most downloaded PyPI projects in the top-pypi-packages list (the list's date is stored). Unit: one project.

## Read (fixed now)
Description: the long description in the PyPI JSON API. Stated command: the first line anywhere in it that, after an optional "$ " or "> " prompt, starts with pip install, pip3 install or python -m pip install (python or python3). A trailing comment after "#" is dropped. The rest of the line is split like a shell line. Options allowed: -U, --upgrade, -q, --quiet, --user. Anything else makes the command NOT_COMPARABLE (other options, a git or URL or file or path target, a requirements file, an editable install, a placeholder such as <name>, ..., or text in braces).
Run: a new virtual environment on Python 3.12, then pip install --dry-run --only-binary=:all: --no-cache-dir with the command's targets. Dry run resolves and runs no package code, and only wheels are used so no setup script is ever executed. The environment is macOS on arm64. The pip version is stored.
Classes: AGREE (pip would install). DISAGREE (pip fails and the failure is one of: a target that is not on PyPI, a conflict between the requirements, or no matching version although the project has a wheel that fits this Python and platform). NOT_COMPARABLE (no pip command in the description, a command of the kinds above, or pip fails only because the project has no wheel that fits this Python and platform, which includes projects that publish only source distributions).
Reported: counts by class, the share DISAGREE among AGREE plus DISAGREE with a Wilson 95% interval, the reasons for NOT_COMPARABLE, and every DISAGREE row with the command and pip's error line.
Outcome against the claim that the stated command installs (zero failures): ABOVE if the lower end of the share is above 0.10, CONSISTENT if the upper end is below 0.05, otherwise CANNOT_TELL. Fewer than 30 comparable projects: CANNOT_TELL. Same thresholds as HFLICENSE.
Re-read every 30 days.

## Hand check (fixed now)
Every DISAGREE row is opened by hand, the README line and the error, before it is shown, and the reason written beside it. A row where the reading, not the project, was wrong is corrected by a dated addendum and the whole read is run again.

## Known-good
Before each read: pip install requests resolves (AGREE). requests==0.0.0001 fails with no matching version while requests has fitting wheels (DISAGREE). A made-up name fails as not on PyPI (DISAGREE). Parser: "$ pip install foo" reads foo, "python -m pip install -U foo[extra]==1.2" reads foo[extra]==1.2, "pip install git+https://x/y" and "pip install -e ." and "pip install <name>" and "pip install -r r.txt" read NOT_COMPARABLE. Any wrong answer stops the pass.

## Not claimed
That the project works after it installs. That a command fails on another operating system or Python. Anything about commands that need a source build, which are not run.

## Addendum 1 (29 Oct, after the first read and its hand check, before anything was shown)
The first read had one DISAGREE row, nvidia-cusparselt-cu13, whose description tells the reader to run pip install nvidia-cusparselt-cuXX, where XX stands for the CUDA major version. That is a placeholder the reader did not recognise, not a project whose command fails. The placeholder rule now also treats a run of two capital X letters, YOUR_ or YOUR- followed by a word, and any angle-bracketed word in a target as a placeholder, so the command is NOT_COMPARABLE. The whole read is run again. The first read's numbers (545 agree, 1 disagree, 454 not comparable) are not used. No other rule changed.

## Addendum 2 (29 Oct, after the second read, before anything was shown)
The second read had no DISAGREE rows. Sampling the AGREE rows by hand found commands that do not install the project they were read from: the first pip install line in cffi's description installs pytest, in thinc's it upgrades pip, setuptools and wheel, in google-cloud-bigquery it installs virtualenv. In the second read 22 of 545 AGREE rows were of this kind. The claim read is that the command installs the project, so a command that does not name the project is not that claim. A command now counts only when one of its targets, with its extras removed and with hyphens, underscores and periods treated as one, equals the project's name, or equals the project's name with one listed extra added after a hyphen (psycopg[binary] for psycopg-binary). Any other command is NOT_COMPARABLE with the reason "command does not name this project". The whole read is run again. The second read's numbers (545 agree, 0 disagree) are not used. No threshold or outcome rule changed.

## Note 1 (29 Oct, hand check of the third read, before anything was shown)
After addendum 2 the read has 525 AGREE rows, no DISAGREE rows and 475 NOT_COMPARABLE rows. With no DISAGREE row there is nothing to open, so ten AGREE rows chosen with seed 11 were read by hand, the command against the description, and each names its project. A read of this size with zero failures bounds the share failing below 0.8% at 95%. No rule changed.

## Note 2 (29 Oct, from the internal audit)
1. The classifier scored any pip failure it did not recognise as DISAGREE, so a network or build error would have read as the project failing. An unrecognised failure is now NOT_COMPARABLE with its message. No project changed class.
2. Stated and not fixed: 525 of 525 comparable commands agree, and a command that names a project by its own PyPI name from the top-PyPI list has little room to fail, so the ruler can barely show failure here. The 424 projects with no pip install line are found by a line-start pattern and an inline command would read as absent. The 0.8 percent bound treats projects as independent although families share one install line.
