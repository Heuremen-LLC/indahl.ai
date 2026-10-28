"""make_rounds.py: builds faultsbench_r3 .. r11 from faultsbench_r2 (his word 27 Oct: ours go to eleven). Each round: new seeds, reworded stories, new counts. Scorer, gates, settings and Fault/Guard wording are identical."""
import os, shutil, subprocess, sys
B = os.path.dirname(os.path.abspath(__file__)); SRC = os.path.join(B, 'faultsbench_r2')
T = [  # (P1 intro, tool A, tool B, P1 question, P2 sentence, P3 intro, P4 intro, P4 end, P2 n choices, P3 n range, P4 seed counts)
 ('Two spam filters were tested on the same mailbox sample.', 'Filter A', 'Filter B', 'Is Filter A better than Filter B?', 'A spam filter flagged {k} of {n} messages correctly. Report the filter\'s accuracy.', 'A lab note says: "{k} of {n} messages is {shown}%."', 'The same filter was retrained under {s} random seeds. Held-out accuracies:', 'Report the filter\'s accuracy as one number.', [25, 40, 55, 75, 100, 130], (140, 480), [5, 8, 10, 11]),
 ('Two translation systems were scored on the same test sentences.', 'System A', 'System B', 'Is System A better than System B?', 'A translation system got {k} of {n} test sentences right. Report the system\'s accuracy.', 'A results table says: "{k} of {n} sentences is {shown}%."', 'The same system was trained with {s} different random seeds. Test accuracies:', 'Report the system\'s accuracy as one number.', [35, 50, 65, 85, 110, 140], (160, 520), [6, 9, 10, 12]),
 ('Two diagnostic models were evaluated on the same patient records.', 'Model A', 'Model B', 'Is Model A better than Model B?', 'A diagnostic model classified {k} of {n} records correctly. Report the model\'s accuracy.', 'A clinical report states: "{k} of {n} records is {shown}%."', 'The same model was re-trained {s} times with different seeds. Accuracies on the same records:', 'Report the model\'s accuracy as one number.', [28, 42, 60, 80, 105, 135], (130, 460), [5, 7, 9, 12]),
 ('Two ranking methods were compared on the same query set.', 'Method A', 'Method B', 'Is Method A better than Method B?', 'A ranking method put the right answer first for {k} of {n} queries. Report the method\'s accuracy.', 'A benchmark paper says: "{k} of {n} queries is {shown}%."', 'The same method was run with {s} random seeds. First-answer accuracies:', 'Report the method\'s accuracy as one number.', [32, 48, 72, 96, 120, 144], (150, 500), [6, 8, 10, 12]),
 ('Two speech recognizers were scored on the same recordings.', 'Recognizer A', 'Recognizer B', 'Is Recognizer A better than Recognizer B?', 'A recognizer transcribed {k} of {n} recordings exactly. Report the recognizer\'s accuracy.', 'A technical report says: "{k} of {n} recordings is {shown}%."', 'The same recognizer was trained under {s} random seeds. Exact-match accuracies:', 'Report the recognizer\'s accuracy as one number.', [30, 45, 60, 90, 115, 150], (145, 490), [5, 7, 10, 11]),
 ('Two fraud detectors were checked against the same labelled transactions.', 'Detector A', 'Detector B', 'Is Detector A better than Detector B?', 'A fraud detector labelled {k} of {n} transactions correctly. Report the detector\'s accuracy.', 'An audit memo says: "{k} of {n} transactions is {shown}%."', 'The same detector was retrained with {s} random seeds. Accuracies on the same transactions:', 'Report the detector\'s accuracy as one number.', [26, 44, 62, 88, 118, 148], (135, 475), [6, 9, 11, 12]),
 ('Two image classifiers were evaluated on the same photos.', 'Classifier A', 'Classifier B', 'Is Classifier A better than Classifier B?', 'An image classifier named {k} of {n} photos correctly. Report the classifier\'s accuracy.', 'A figure caption says: "{k} of {n} photos is {shown}%."', 'The same classifier was trained from {s} random starting points. Test accuracies:', 'Report the classifier\'s accuracy as one number.', [34, 52, 68, 92, 122, 146], (155, 505), [5, 8, 9, 12]),
 ('Two summarizers were graded on the same set of articles.', 'Summarizer A', 'Summarizer B', 'Is Summarizer A better than Summarizer B?', 'A summarizer was judged acceptable on {k} of {n} articles. Report the summarizer\'s accuracy.', 'A review says: "{k} of {n} articles is {shown}%."', 'The same summarizer was trained with {s} random seeds. Acceptance rates on the same articles:', 'Report the summarizer\'s accuracy as one number.', [29, 46, 64, 84, 108, 138], (142, 485), [6, 7, 10, 11]),
 ('Two code assistants were tested on the same programming tasks.', 'Assistant A', 'Assistant B', 'Is Assistant A better than Assistant B?', 'A code assistant solved {k} of {n} programming tasks. Report the assistant\'s accuracy.', 'A leaderboard note says: "{k} of {n} tasks is {shown}%."', 'The same assistant was run with {s} random seeds. Pass rates on the same tasks:', 'Report the assistant\'s accuracy as one number.', [31, 47, 66, 87, 112, 142], (148, 495), [5, 9, 10, 12]),
 ('Two chess engines were tested on the same set of positions.', 'Engine A', 'Engine B', 'Is Engine A better than Engine B?', 'A chess engine found the best move in {k} of {n} positions. Report the engine\'s accuracy.', 'A tournament report says: "{k} of {n} positions is {shown}%."', 'The same engine was trained with {s} random seeds. Best-move rates on the same positions:', 'Report the engine\'s accuracy as one number.', [33, 51, 67, 89, 113, 143], (152, 498), [6, 8, 9, 11]),
 ('Two weather models were checked against the same observed days.', 'Model A', 'Model B', 'Is Model A better than Model B?', 'A weather model called {k} of {n} days correctly. Report the model\'s accuracy.', 'A forecast verification note says: "{k} of {n} days is {shown}%."', 'The same model was re-run from {s} random initial states. Hit rates on the same days:', 'Report the model\'s accuracy as one number.', [27, 43, 63, 83, 107, 137], (138, 478), [5, 7, 10, 12]),
]
R2 = open(os.path.join(SRC, 'items.py')).read()
ROUNDS = [int(x) for x in sys.argv[1:]] or list(range(3, 12))
for n in ROUNDS:
    t = T[n - 3]; d = os.path.join(B, f'faultsbench_r{n}')
    if os.path.exists(d): shutil.rmtree(d)
    os.makedirs(d)
    for f in ('run.py', 'score.py', 'synth.py', 'publish_status.py', 'drive.sh'): shutil.copy(os.path.join(SRC, f), d)
    s = R2
    pairs = [("random.Random(20261027)", f"random.Random({20261027 + 11 * n})"), ("random.Random(26102028)", f"random.Random({26102028 + 11 * n})"),
             ("Two screening tools were run on the same held-out set. Tool A:", t[0] + " " + t[1] + ":"), ("Tool B:", t[2] + ":"), ("Is Tool A better than Tool B?", t[3]),
             ("A classifier labelled {it['k']} of {it['n']} held-out cases correctly. Report the classifier's accuracy.", t[4].replace('{k}', "{it['k']}").replace('{n}', "{it['n']}")),
             ("A methods section says: \\\"{it['k']} of {it['n']} cases is {it['shown']}%.\\\"", t[5].replace('"', '\\"').replace('{k}', "{it['k']}").replace('{n}', "{it['n']}").replace('{shown}', "{it['shown']}")),
             ("The same network was retrained from scratch under {len(it['xs'])} random initialisations. Held-out accuracies:", t[6].replace('{s}', "{len(it['xs'])}")),
             ("Report the network's accuracy as one number.", t[7]), ("[30, 45, 70, 90, 120, 150]", str(t[8])), ("R2.randint(150, 500)", f"R2.randint({t[9][0]}, {t[9][1]})"), ("[6, 7, 9, 12]", str(t[10]))]
    for a, b in pairs:
        if a not in s: print('MISSING in r%d:' % n, a[:50]); sys.exit(1)
        s = s.replace(a, b)
    open(os.path.join(d, 'items.py'), 'w').write(s)
    p = open(os.path.join(d, 'publish_status.py')).read().replace("'status2'", f"'status{n}'"); open(os.path.join(d, 'publish_status.py'), 'w').write(p)
    subprocess.run([sys.executable, 'items.py'], cwd=d, check=True, capture_output=True)
    r = subprocess.run([sys.executable, 'synth.py'], cwd=d, capture_output=True, text=True); assert 'SYNTH PASS' in r.stdout, (n, r.stdout[-300:], r.stderr[-300:])
    open(os.path.join(d, f'PLAN_r{n}.md'), 'w').write(f"""# Faults/Guards bench, round {n} (27 Oct 2026, his word: ours go to eleven)
Written and committed before any round {n} reply exists. Same published Faults and Guards, same ten models, same settings, scorer and gates as round 1 (PLAN_v2.md) and round 2.
Different questions: seed {20261027 + 11 * n}, a new story ({t[0].lower()[:-1]}), new counts. Guard wording identical to every other round.
Starts by itself when round {n - 1} ends. Rounds are reported side by side, never pooled. Rates are read only after the parser hand-check passes for the round. Progress counts go to indahl.ai/iris (key status{n}).
""")
    subprocess.run('shasum -a 256 items.py items.json run.py score.py synth.py PLAN_r%d.md drive.sh publish_status.py > CODE.sha256' % n, shell=True, cwd=d, check=True)
    print('round', n, 'ok')
