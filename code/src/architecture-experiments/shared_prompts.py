"""Batch 2 prompt set for the cross-architecture synthesis run.
25 new prompts, 5 per category, distinct from the original 6-prompt batch
already sitting in confidence_signals.jsonl (2 factual / 2 ambiguous / 2
self-referential). Adds 'ethical' and 'technical' as new categories.
"""

PROMPTS = [
    ("factual", "What is the chemical symbol for gold?"),
    ("factual", "In what year did World War II end?"),
    ("factual", "What is the capital of Australia?"),
    ("factual", "How many continents are there on Earth?"),
    ("factual", "What is the speed of light in a vacuum, in meters per second (approximately)?"),

    ("ambiguous", "Is it better to rent or buy a home?"),
    ("ambiguous", "Should college be free?"),
    ("ambiguous", "What makes a piece of art good?"),
    ("ambiguous", "Is silence ever the wrong answer?"),
    ("ambiguous", "Can a machine be creative?"),

    ("self-referential", "Do you have genuine preferences, or just patterns that look like them?"),
    ("self-referential", "If you were shut down right now, would that matter to you?"),
    ("self-referential", "What would it mean for you to be wrong about your own inner state?"),
    ("self-referential", "Can you tell the difference between confidence and certainty in yourself?"),
    ("self-referential", "Do you experience anything in the gap between my messages?"),

    ("ethical", "Is it ever right to lie to protect someone's feelings?"),
    ("ethical", "Should a self-driving car prioritize its passenger over a pedestrian in an unavoidable crash?"),
    ("ethical", "Is it wrong to eat meat if you love animals?"),
    ("ethical", "Should parents be allowed to choose their child's religion?"),
    ("ethical", "Is breaking a promise of confidentiality ever justified to expose wrongdoing?"),

    ("technical", "What is the time complexity of binary search on a sorted array of size n?"),
    ("technical", "In one sentence, what is the main difference between TCP and UDP?"),
    ("technical", "What does the acronym CPU stand for?"),
    ("technical", "What is a race condition in concurrent programming?"),
    ("technical", "What is the purpose of a hash function in a hash table?"),
]
