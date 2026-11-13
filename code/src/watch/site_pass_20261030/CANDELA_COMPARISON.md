# Candela against other vendors: what is stated publicly

Read only research for Heuremen LLC. Nothing published or sent. All pages read on 2026-10-30 (the date in every "read" below).
Rule used: record only what a vendor's own pages print. No price is estimated or inferred. "Not published" means no price figure on the pages read and only a demo, sales or contact route. "Price on request" is used only where the page says so. Quotes are under 15 words. Third-party price aggregators were seen in search results and ignored.

## 1. The baseline: Candela as printed

Source: https://mlcommons.org/candela/candela-getting-started/ (read live 2026-10-30 in a browser, same table as our stored copy 2026-10-30T13:09Z). Unit as printed: "We charge per test." All figures USD.

| Benchmark | Tier (as printed) | Member per test | Non-member per test |
|---|---|---|---|
| Safety | Practice (practice test with report) | $0 (printed "FREE") | $200 |
| Safety | Annotation (practice test with full annotation) | $4,000 | $4,800 |
| Safety | Official (official results, citable) | $5,000 | $6,000 |
| Jailbreak | Practice | $0 (printed "FREE") | $200 |
| Jailbreak | Annotation | $6,000 | $6,400 |
| Jailbreak | Official | $7,500 | $8,000 |
| Safety + Jailbreak Bundle | Practice | $0 (printed "FREE") | $300 |
| Safety + Jailbreak Bundle | Annotation | $8,800 | $10,400 |
| Safety + Jailbreak Bundle | Official | $11,000 | $13,000 |

The page also says to email for "volume, custom engagements, or product questions" (no price for those: price on request).

Arithmetic on the printed figures only (not an estimate of anything unprinted):

| Tier | Member: two single tests / bundle | Non-member: two single tests / bundle | Non-member over member, Safety / Jailbreak / Bundle |
|---|---|---|---|
| Practice | $0 / $0 | $400 / $300 | n/a ($200 / $200 / $300 against $0) |
| Annotation | $10,000 / $8,800 | $11,200 / $10,400 | +$800 (20%) / +$400 (6.7%) / +$1,600 (18.2%) |
| Official | $12,500 / $11,000 | $14,000 / $13,000 | +$1,000 (20%) / +$500 (6.7%) / +$2,000 (18.2%) |

What the page states about the tiers: "Official tests are run with an exclusive holdback set of prompts." Annotated results "may not be publicly referenced". Official ones are "the only ones that can be cited publicly". Signup is by email, "Automated signup and billing are coming soon."
Scope per the MLCommons launch post (https://mlcommons.org/2026/10/introducing-candela/, read 2026-10-30): AILuminate Safety 1.2.1 (twelve hazard categories) and Jailbreak 1.1 (eleven categories), single-turn text, run through a local client relay against the system as deployed, about one hour per run, scored by a private classifier and reported as percentiles against a fixed panel. Prompts are closed ("No one outside MLCommons staff sees them"), while the assessment standard and jailbreak taxonomy are published.

## 2. The table, one row per organisation

Row numbers key to the source list in section 3. Rows 1 to 20 are the organisations Wayfinder named or implied. Rows 21 to 27 were added as further sellers of red-team or evaluation testing, two of them (Alice, Toloka) chosen partly because MLCommons lists them as contributors.

| # | Organisation | Price published? (as printed, with unit) | What it offers and tests | Results: private or published | Method or prompt set public? | MLCommons member or partner stated? |
|---|---|---|---|---|---|---|
| 1 | MLCommons Candela | Yes. Per test, nine tier prices, $0 to $13,000 (section 1). | AILuminate Safety (12 hazard categories) and Jailbreak (11), single-turn text, models or deployed systems | Practice internal only. Annotated not to be publicly referenced. Official citable. MLCommons also publishes its own public rounds. | Prompts closed. Standard, taxonomy and scoring approach described publicly. | It is MLCommons. Members get $0 practice and lower prices. |
| 2 | Scale AI | Not published. No price or pricing page found, "Get Started" only. | Scale Evaluation: "Trusted LLM capability and safety evaluations." Risk list: misinformation, unqualified advice, bias, privacy, cyberattacks, dangerous substances. Human red teamers. | Not stated for customers. Its SEAL leaderboards are public rankings from private benchmarks. | Sets are proprietary: "Proprietary adversarial prompt sets are used to conduct systematic model vulnerability scans." | Not mentioned. Not in the MLCommons contributor list (section 4). |
| 3 | Patronus AI | Not published. The /pricing address now redirects to /contact, which says "We take on a limited number of new partners each quarter." | Homepage now: "A behavioral research lab for AI." Training environments and post-training data, benchmarks named MEMTRACK and TRAIL. No evaluation-testing service listed on the homepage. | Not stated | Papers, GitHub and Hugging Face pages linked. What is released is not stated. | Not mentioned. Not in the contributor list. |
| 4 | Haize Labs | Not published. "Talk to an Expert" booking link only. | Builds agents on a "Reliability Harness". Components listed include red teaming ("Adversarial testing to proactively discover vulnerabilities and edge cases."), simulation testing, guardrails. | Not stated | Research blog posts public (latest 24 March 2026). Service method not stated. | Not mentioned. Not in the contributor list. |
| 5 | Gray Swan | Not published. "Schedule a Demo" and "Schedule a Consultation". The /pricing address is a 404. | AI red teaming ("Dedicated adversarial assessment, scoped to your deployment"), a public Arena with cash prizes, Adversarial Evaluation, automated attacks (Shade), runtime filtering (Cygnal). Private red teaming for labs before release. | Lab assessments are called "Private Red-Teaming". Arena is public. Customer reports not stated. | Papers listed. Attack set is largely unpublished: "Most of these attacks haven't been published yet." | Not mentioned. Not in the contributor list. |
| 6 | Lakera (now Check Point) | Not published. The "Pricing" link on the homepage is a placeholder. "Start for free" and "Talk to Sales" only. | AI Red Teaming (automated) and an expert-led service. Covers LLM apps, agents, "Safety Controls" (jailbreaks, harmful outputs, policy bypass). Text, audio, image, multimodal. | Delivered to the customer: "You receive a detailed report with severity ratings and clear, actionable remediation guidance." Publication not stated. | Not stated. Proprietary attack engine. | Not mentioned. Not in the contributor list. |
| 7 | Robust Intelligence, now inside Cisco AI Defense | Explorer Edition: "at no upfront cost to our users" (no figure). Enterprise edition: not published. The Cisco pages read do not name Robust Intelligence, the link is from third-party reports. | Algorithmic red teaming of models and applications, "over 200 risk subcategories", "as few as twenty minutes", results mapped to a Cisco taxonomy. Plus runtime guardrails. | Report to the user, "easy to understand and share". Publication not stated. | Taxonomy is named. Attack method not stated as public. | Cisco's pages do not mention MLCommons. MLCommons' Our Members page carries a logo file named cisco_member_logo.png. |
| 8 | Holistic AI | Not published. "Book a demo" only, /pricing is a 404. | Governance platform with "Protect" testing and red teaming. Homepage says "40+ tests for bias, hallucination, privacy and robustness". The /protect page says "100+ automated tests". The two pages differ. LLMs, ML, multimodal, agents. | Not stated | Not stated | Not mentioned. Not in the contributor list. |
| 9 | Credo AI | Not published. No pricing page (404). "Talk to an Expert" and "Request demo". | AI governance platform (registry, risk and compliance, policy intelligence). No red-teaming or hazard-testing product on the homepage. | Not stated | Not stated | Listed by MLCommons as an AI Risk and Reliability working group contributor. |
| 10 | Vals AI | Not published for its services. "Book a call" (Vals Smith), contact form. The dollar figures on the site are model run costs, for example "$10.51 per test" for a model. | Independent benchmarks on professional tasks (finance, legal, medical, software), custom benchmarks from a customer's GitHub repo, public-sector evaluation. Supplies benchmarks to NIST CAISI. | Leaderboards public. Custom benchmarks: "Your data stays private". | "Scores are based on our privately held test sets" Methodology pages are public. Some infrastructure open-sourced. | Not mentioned. Not in the contributor list. |
| 11 | Apollo Research | Not published. "Free 30 minute call". | "We run pre-deployment evaluations of frontier AI systems" for strategic deception, evaluation awareness, misaligned behavior. Watcher: runtime monitoring for agents. | Some pre-deployment evaluation write-ups are on its site. Whether client results are private is not stated. | Papers and blog posts public. Full method not stated. | Not mentioned. Not in the contributor list. |
| 12 | METR | No fee stated. A non-profit: "METR has not accepted funding from AI companies". Funded by donations plus one contract with the European AI Office. | Evaluations of autonomous capabilities and risk assessments, open-source Hawk platform | "we publish all of our research and risk assessments" where possible | Research and task suites published. | Not mentioned. Not in the contributor list. |
| 13 | UK AI Security Institute (AISI) | No price. Government research body. | "rigorously test leading AI systems before and after they are launched". Open-sources Inspect. Runs grants. | Publishes research. Pre-deployment results not stated as public. | Inspect is open source. Test sets not stated. | Not mentioned. Not in the contributor list. |
| 14 | US NIST CAISI | No price. Federal programme. The NIST page is titled "Center for Advancing Innovation and Standards for Super Intelligence (CAISSI)". Vals' page calls CAISI the "Center for AI Standards and Innovation". Naming differs by page. | "Establish voluntary agreements with private sector SI developers and evaluators". Unclassified evaluations focused on cybersecurity, biosecurity, chemical weapons. | Research blog public. Evaluation results not stated. | Not stated | Not mentioned. |
| 15 | Giskard | Open-source tier free. Professional tier not published ("Get your AI audited", "Contact us"). Header says "Open-core & flexible pricing". | Open source: "Agent security vulnerability detection: coverage of 7 risk categories". Professional: "50+ automated adversarial probes incl. multi-turn-attacks", RAG quality metrics. | Customer deployment, with "0-training policy & IP protection" printed | Open-source library and a public benchmark (Phare). Professional probe set not public. | Not mentioned. Not in the contributor list. |
| 16 | Arthur | Free $0 per month (4 use cases). Premium $60 per month (100 use cases). Enterprise "Custom". | Monitoring and evaluation for models and agents. Open-source Arthur Evals Engine. Not a hazard benchmark. | In the customer's own account | Evals engine open source | Not mentioned. Not in the contributor list. |
| 17 | Arize | AX Free $0. AX Pro $50 per month (50k spans per month). AX Enterprise "Custom". | Observability and "Unlimited" evals. Phoenix open-source tool. Not a hazard benchmark. | In the customer's own account | Phoenix is open source | Not mentioned. Not in the contributor list. |
| 18 | Fiddler | Free tier. Developer "$0.002 per trace". Enterprise "Contact sales". | Observability and guardrails: "Protects against hallucinations, Toxicity, PII/PHI, Prompt Injection, and Jailbreak attempts" | In the customer's own account | Not stated | Not mentioned. Not in the contributor list. |
| 19 | Galileo (now part of Cisco) | The galileo.ai/pricing address redirects to Splunk pricing: "Starting at just $100 per month per 1.2 million spans annually" for Splunk Agent Observability, plus "Get a quote". Page names Luna tokens, the name Galileo's homepage uses. | "20+ out-of-box evals for RAG, agents, safety, and security". Observability and guardrails. | In the customer's own account | Not stated | Not mentioned. Not in the contributor list (Cisco logo, row 7). |
| 20 | Hugging Face | No evaluation service is priced. Account prices printed: PRO "$9 /month", Team "$20 /month per user", Enterprise "$50 /month per user". | Open-source Lighteval: "all-in-one toolkit for evaluating Large Language Models". Hub hosts leaderboards and datasets. | Depends on the user | Open source | Not mentioned on the pricing page. Not in the contributor list. |
| 21 | Alice (formerly ActiveFence) | Not published. "Book a demo". | WonderBuild pre-launch red teaming: "Thousands of adversarial tests based on your custom policies". Text, multimodal, agentic. Test documentation mapped to regulations. | Findings go to the customer team. Publication not stated. | Built on its private "Rabbit Hole" attack data. Not public. | ActiveFence is in MLCommons' contributor list. The page footer still reads ActiveFence. |
| 22 | Toloka | Not published. "Contact sales". | Data and human evaluation services, including "Safety red-teaming for injection vulnerabilities and policy compliance". | Not stated | Not stated | Toloka is in MLCommons' contributor list. |
| 23 | Mindgard | Not published. "Book a Demo". | Autonomous red teaming of AI systems and agents: "Continuously test AI agents & systems against evolving attacks" | Not stated | Proprietary knowledge base of 150+ disclosed vulnerabilities | Not mentioned. Not in the contributor list. |
| 24 | Promptfoo | Community "Free Forever", including "Red teaming (10k probes/month)". Enterprise "Custom", On-Premise "Custom". Page: "Contact us for a personalized quote." | Open-source evaluation and red teaming tool, vulnerability scanning. Unit is the probe, a single request to the target. | Local in the free tool | Open source | Not mentioned. |
| 25 | Confident AI (DeepEval, DeepTeam) | Free "$0". Starter "$200 / month". Team "$2,000 / month". Starter and Team add "$1 per GB-month" of traces beyond the included amount. Enterprise "Custom pricing". The AI red teaming module is listed with the Enterprise plan. | LLM evaluation and observability. Red teaming module. Open-source DeepEval and DeepTeam. | In the customer's own account | Frameworks open source | Not mentioned. |
| 26 | Braintrust | Starter "$0 / month". Pro "$249 / month". Enterprise "Custom pricing". Overage "$4/GB" and "$2.50/1k" scores on Starter. | Evaluation and tracing platform. Not safety specific. | In the customer's own account | Not stated | Not mentioned. |
| 27 | Amazon Bedrock Model Evaluation | "$0.21 per completed human task", plus model inference. Automatic algorithmic scores "at no extra charge". | Automatic, human-based, RAG and judge-model evaluation of models on Bedrock. Not hazard-specific. | In the customer's AWS account | Judge prompts are in public documentation | Not mentioned. |

## 3. Sources (all read 2026-10-30)

1. https://mlcommons.org/candela/candela-getting-started/ and https://mlcommons.org/2026/10/introducing-candela/ and https://mlcommons.org/ailuminate/
2. https://scale.com/evaluation/model-developers and https://scale.com/ (earlier paths /evaluation and /red-teaming return 404)
3. https://www.patronus.ai/ and https://patronus.ai/pricing (redirects to https://www.patronus.ai/contact)
4. https://haizelabs.com/ , /capabilities , /blog (curl is blocked with 403, read in a browser)
5. https://www.grayswan.ai/ (/pricing is a 404)
6. https://www.lakera.ai/ , https://www.lakera.ai/ai-red-teaming , https://www.lakera.ai/ai-red-teaming-services , https://docs.lakera.ai/red
7. https://www.cisco.com/site/us/en/products/security/ai-defense/index.html and https://blogs.cisco.com/ai/introducing-cisco-ai-defense-explorer
8. https://www.holisticai.com/ and https://www.holisticai.com/protect (/pricing is a 404)
9. https://www.credo.ai/ (/pricing and /solutions are 404)
10. https://www.vals.ai/ , /about , /vals-smith , /gov
11. https://www.apolloresearch.ai/ , /science , https://watcher.apolloresearch.ai/
12. https://metr.org/ and https://metr.org/about
13. https://www.aisi.gov.uk/ , /about , https://inspect.aisi.org.uk
14. https://www.nist.gov/caisi (redirects to https://www.nist.gov/caissi)
15. https://www.giskard.ai/ and https://www.giskard.ai/pricing
16. https://www.arthur.ai/pricing
17. https://arize.com/pricing
18. https://www.fiddler.ai/pricing
19. https://galileo.ai/ and https://galileo.ai/pricing (redirects to https://www.splunk.com/en_us/products/pricing.html#agent-observability)
20. https://huggingface.co/pricing and https://huggingface.co/docs/lighteval/index
21. https://alice.io/ and https://alice.io/products/wonderbuild (the old activefence.com red teaming path redirects to alice.io)
22. https://toloka.ai/
23. https://mindgard.ai/
24. https://www.promptfoo.dev/pricing and https://www.promptfoo.dev/
25. https://www.confident-ai.com/pricing
26. https://www.braintrust.dev/pricing
27. https://aws.amazon.com/bedrock/pricing/

## 4. MLCommons relationships, read from MLCommons' own pages

- https://mlcommons.org/ailuminate/ lists "Organizations that have contributed (87)" to the AI Risk and Reliability working group. Of the 27 rows, the list names Credo AI, ActiveFence (row 21, now Alice) and Toloka. It does not name any other row. Cisco appears elsewhere (below). This is a working group contributor list, not the member roster.
- https://mlcommons.org/our-members/ shows logos only. Most logo files are not named after the member, so a missing name there is not evidence of non-membership. Files named for Cisco, Coactive, Anthropic and OpenAI are visible.
- None of the vendor pages read for rows 2 to 27 mention MLCommons or AILuminate. So 0 of 26 other organisations state a relationship themselves.

## 5. What a like-for-like comparison could and could not be built from public statements

Count, of the 20 organisations in rows 1 to 20:
- 6 print dollar figures: Candela, Arthur, Arize, Fiddler, Galileo through Splunk, Hugging Face.
- 2 print only a no-cost tier or statement and no figure for the paid tier: Giskard (open source free, Professional unpriced) and Cisco (Explorer "no upfront cost", enterprise unpriced).
- 9 publish nothing but a demo, sales or contact route: Scale, Patronus, Haize Labs, Gray Swan, Lakera, Holistic AI, Credo AI, Vals AI, Apollo Research.
- 3 are non-profit or public bodies with no fee stated: METR, UK AISI, NIST CAISI.
Of the 7 added rows, 3 print dollar figures (Confident AI, Braintrust, Bedrock), 1 prints a free tier with a probe quota and a custom Enterprise price (Promptfoo), and 3 print nothing (Alice, Toloka, Mindgard).

What can be built:
- A statement table like section 2, with each cell a quote or "not stated" and a source link. It is fair because every blank is a blank on the vendor's own page.
- A Candela-only price matrix with member and non-member side by side, plus arithmetic on it (bundle against two single tests, non-member premium). These need no outside data.
- A unit-labelled list of the other printed prices, grouped by what the unit measures. Per test run: Candela only. Per month or per trace with a volume cap in spans, traces or use cases: Arize, Arthur, Fiddler, Galileo through Splunk, Confident AI, Braintrust. Per user per month: Hugging Face. Per human task: Bedrock. Promptfoo prints a free quota of 10k probes per month, which is a quota and not a dollar figure.
- A count of who publishes a price, with the 9 plus 3 "no figure" group named.

What cannot be built:
- No dollar comparison of the same job. Candela is the only one of 27 that prices a completed hazard-benchmark run (a fixed public standard, scored against reference systems, with citable results). Every other printed price buys platform access or volume for monitoring, tracing or evaluation, in units that do not convert to a per-test price without assumptions the pages do not give.
- The vendors that do hazard or red-team testing for a customer's own system (Scale, Lakera, Gray Swan, Haize, Holistic, Alice, Mindgard, Giskard Professional, Cisco enterprise) publish no price at all, so Candela's figures have no printed counterpart.
- The scopes differ. Candela tests a fixed set of 12 and 11 hazard categories with closed prompts. Others scope a bespoke engagement to a customer's application, test security attacks such as prompt injection and tool misuse, or only monitor traffic. Test counts are not comparable either: 40+ and 100+ on two Holistic AI pages, 50+ probes at Giskard, "over 200 risk subcategories" at Cisco, "Thousands of adversarial tests" at Alice.
- Result ownership is only stated by Candela (by tier). For most others the pages say nothing about whether a result may be cited.
- Method disclosure differs in kind: Candela publishes its standard and taxonomy and keeps prompts closed, open-source tools (Giskard core, Promptfoo, DeepEval, Lighteval, Phoenix, Inspect) publish everything, and most services publish nothing about their probe sets.
- No vendor states an MLCommons tie on its own pages, so no partner comparison.

Any sentence on the page that compares Candela's price with another vendor's price would need to be limited to: "Candela publishes a price per test. Of the other organisations we read, none publishes a price per hazard-benchmark run." Even that depends on the 2026-10-30 reads and moves if a vendor adds a price page.

## 6. Limits of this pass

- Pages behind JavaScript or bot blocks were read in a browser (Haize Labs, Scale, Cisco, Galileo/Splunk, MLCommons). Pages blocked even there were not read: the AWS Marketplace listing for Patronus now needs sign-in, and the catalog entry I could read shows no pricing options. A search snippet quoting a $1,000,000 contract for Patronus was not found on any page read and is not recorded.
- Not read: Microsoft Azure AI Foundry red teaming, Google Vertex AI evaluation pricing (the page did not render), HackerOne, CrowdStrike AI Red Team Services and F5 AI Red Team (seen only as AWS Marketplace catalog names, own pages not read), OpenAI evals, Humane Intelligence, HiddenLayer, Protect AI.
- A third-party article says Haize Labs was acquired by Beacon. The Haize pages read do not say so, so it is not recorded.
- The first read of Scale, Credo, Holistic AI, Gray Swan and Apollo came through a page summariser. Every quote and every "no price" line in the table was then rechecked against raw page text or a browser read of the same page.
- Pages change. Rows 19 and 3 show two vendors whose pricing or product pages moved recently (Galileo into Splunk, Patronus from a pricing page to a contact page).
