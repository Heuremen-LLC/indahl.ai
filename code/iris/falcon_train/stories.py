"""stories.py: 12 training stories and 2 evaluation stories (FALCON_TRAIN_PLAN.md). None appears in rounds 1 to 13."""
from common import story
TRAIN = [
 story('compilers', 'Compiler', 'the same benchmark programs', 'built {k} of {n} programs without error', 'programs', 'A build log says', [24, 38, 52, 72, 96, 128], (140, 470), [5, 8, 10, 12]),
 story('thermostat controllers', 'Controller', 'the same simulated winter days', 'kept the room in range on {k} of {n} simulated days', 'days', 'A test report says', [26, 40, 58, 78, 104, 134], (150, 490), [6, 7, 9, 11]),
 story('fingerprint matchers', 'Matcher', 'the same enrolled prints', 'matched {k} of {n} prints to the right person', 'prints', 'An evaluation memo says', [32, 46, 62, 82, 108, 138], (130, 480), [5, 7, 10, 12]),
 story('route planners', 'Planner', 'the same delivery maps', 'found a valid route on {k} of {n} maps', 'maps', 'A field note says', [28, 44, 60, 80, 100, 132], (160, 500), [6, 8, 9, 12]),
 story('sentiment models', 'Model', 'the same product reviews', 'labelled {k} of {n} reviews with the right sentiment', 'reviews', 'A product team slide says', [30, 42, 66, 86, 112, 142], (140, 460), [5, 8, 11, 12]),
 story('anomaly detectors', 'Detector', 'the same server logs', 'flagged {k} of {n} planted faults', 'faults', 'A reliability report says', [25, 36, 54, 74, 98, 126], (120, 450), [6, 7, 10, 12]),
 story('OCR engines', 'Engine', 'the same scanned pages', 'read {k} of {n} pages with no errors', 'pages', 'A digitisation log says', [34, 48, 68, 88, 114, 144], (150, 510), [5, 9, 10, 11]),
 story('recommendation models', 'Recommender', 'the same held-out sessions', 'put a clicked item in the top slot for {k} of {n} sessions', 'sessions', 'A dashboard note says', [27, 41, 57, 77, 101, 131], (140, 470), [6, 8, 9, 12]),
 story('pose estimators', 'Estimator', 'the same video clips', 'tracked the whole body correctly in {k} of {n} clips', 'clips', 'A lab notebook says', [29, 43, 63, 83, 109, 139], (130, 490), [5, 7, 9, 11]),
 story('grammar checkers', 'Checker', 'the same student essays', 'corrected {k} of {n} essays fully', 'essays', 'A tool review says', [33, 47, 67, 87, 113, 143], (160, 520), [6, 9, 10, 12]),
 story('crop classifiers', 'Classifier', 'the same field photographs', 'named the right crop in {k} of {n} photographs', 'photographs', 'A survey summary says', [31, 45, 61, 81, 107, 137], (140, 480), [5, 8, 10, 12]),
 story('call routers', 'Router', 'the same recorded support calls', 'sent {k} of {n} calls to the right team', 'calls', 'An operations memo says', [35, 49, 69, 89, 115, 145], (150, 500), [6, 7, 11, 12]),
]
EVAL = {
 'A': story('battery models', 'Model', 'the same charge cycles', 'predicted the end of life within a week on {k} of {n} cells', 'cells', 'A durability report says', [30, 45, 70, 90, 120, 150], (140, 480), [5, 8, 10, 12]),
 'B': story('bridge inspectors', 'Inspector', 'the same set of load tests', 'found the planted crack in {k} of {n} load tests', 'load tests', 'An inspection summary says', [30, 45, 70, 90, 120, 150], (140, 480), [6, 7, 9, 12]),
}
EVAL_SEEDS = {'A': (20271001, 20271002), 'B': (20272001, 20272002)}
TRAIN_SEED0 = 20270001
