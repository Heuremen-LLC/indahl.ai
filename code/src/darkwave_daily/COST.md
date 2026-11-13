# Cost of the daily table

Charged QPU seconds in the saved job records.

| Job | Circuits | Charged |
|---|---|---|
| Clock calibration job C, ibm_kingston and ibm_marrakesh, every day (31 Oct, 1 Nov) | 8 | 11 s |
| Clock jobs A and B | 10 each | 8 s each |
| Clock per chip per day | 28 | 27 s |
| Kit check 2 November, job 1 (8 kit circuits and the 8 study calibration circuits) | 16 | 20 s |
| Kit check 2 November, job 2 (N = 4 only) | 6 | 9 s |

The study's 8 calibration circuits alone cost 11 s as clock job C. In job 1 they shared the job with the kit's 8 circuits, so the kit's 8 circuits added 20 minus 11 = 9 s. A job of its own carries some fixed time on top, so the table job is planned at 12 s per chip per day. `daily_table.py` prints this as `est 12 s`.

Per day for both chips: the clock uses 54 s. The tables add 24 s. Together 78 s.

Remaining instance seconds at the dry run of 2 November 02:10 UTC: 1793 of 14000. At 54 s a day the clock alone would take 1793 to zero in 33 days. With the tables at 78 s a day it takes 23 days. With the clock's 300 s reserve and the tables' 600 s floor in force, the tables stop after about 15 days and the clock after about 21 days.

Other jobs on the same instance also use seconds. From 31 Oct 22:06 UTC (2107 remaining) to now the fall is 314 s. The clock used 108 s of it and the two kit checks 58 s. The other 148 s came from jobs that are neither, about 125 s a day over that stretch. If that continues, the clock alone lasts about 8 days and the clock with tables about 7 days before the reserve and floor stop them. The remaining seconds are shared, so the number to watch is the one in the dry run line.
