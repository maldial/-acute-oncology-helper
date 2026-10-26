# Acute Oncology Helper

A multilingual, voice-enabled helper for stable cancer patients to report symptoms and non-clinical queries naturally in their own language, and for Acute Oncology nurses to receive a verified, structured report alongside the relevant UKONS guideline.

**Hackathon prototype — not for clinical use.**

Built for the **Meta AI Developer Hackathon (Cerebral Valley)**.
Synthetic/test data only. Not a medical device. Must not be used to make clinical decisions or provide autonomous medical advice.

**Clinical Lead:** Medical Oncologist (>5 years experience, Acute Oncology quality improvement and ePROMs experience)

---

## The Problem

The 24-hour Acute Oncology helpline is inundated. From local Acute Oncology call audits and presentations, the majority of low-priority calls are **not** acute oncology symptoms:

1. **Can't reach other teams:** "When is my next treatment? When is my blood test appointment?"
2. **General questions:** "Can I have a flu / cold vaccine? Can I eat this food?"
3. **Confirmations:** "I just want to report I've had my bloods taken" / weekly monitoring patients reporting their blood test is done

These calls consume nursing time during working hours. Urgent patients wait, or cannot get through at all.

Patients from our local socially deprived population consistently feedback: the helpline is busy the majority of the time, they have to leave a message, sometimes they don't even bother.

### The Hidden Group: Patients Who Do Not Call At All

There is a second, less visible problem. Patients with language barriers are often **reluctant to speak to the team, or unable to communicate effectively even when they get through.**

* **Reluctance to speak:** Fear of not being understood, embarrassment discussing diarrhoea, vomiting, bowel, skin or other sensitive symptoms through an interpreter or family member, not wanting to "bother" busy nurses, worry they will be told to come into hospital unnecessarily, and lack of confidence speaking English on the phone to an unknown clinician.
* **Unable to communicate:** Limited English, low literacy in any language, no family member available to interpret at that moment, chemotherapy-related fatigue and cognitive fog, breathlessness, mouth pain from mucositis, hearing or speech difficulties, and being unable to explain a complex symptom in a short, pressured phone call.
* **Dependence on others:** Care is delayed until a son, daughter or partner is home to make the call. The history the nurse receives is then second-hand, and sensitive details are often minimised or missed.

The result is the same: symptoms are reported **late, incompletely, or not at all.**

Existing ePROMs do not solve this. A rigid 40-question English form helps patients who can already complete forms in English. It does not help a patient who cannot do a phone call in English.

**Acute Oncology Helper explores a different model:** Let the patient just talk, in their own language, in their own words, at their own pace. The system figures out what they want, verifies it with them, asks only the next relevant question, and does not bombard them with a huge checklist.

---

## Who This Is For — And Who It Is Not For

**For:** Stable patients at home, between treatments, who want to report a symptom, log a confirmation, ask a non-urgent question, or complete a scheduled follow-up report without waiting on a busy helpline.

**Not for:** Very unwell patients.

If a patient feels very unwell, is deteriorating rapidly, or reports fever on cancer treatment, chest pain, or breathlessness at rest, the system **stops the form**, directs them to call the 24-hour helpline immediately, and flags the incomplete report as priority for the nurse.

This is an asynchronous, ePROMs-style reporting service for stable patients. It is not an emergency triage service.

All patients in the intended future service would be given a clear instruction: *If you are unwell, do not fill in this form — call the helpline straight away.*

---

## The Concept

The patient is never presented with a big checklist of problems to click "No" through, like many GP online systems.

They are asked one simple thing:

> "Tell me what you wanted to tell the team today."

Patient talks freely (voice or text, English or Urdu for this prototype):

> *"Assalamualaikum, from morning loose motions, four five times, I had Keytruda three weeks ago..."*
>
> *"Today my blood test is done at GP, just wanted to tell the team, every week I do."*
>
> *"Can I take the flu injection? My GP is asking, I am on treatment."*
>
> *"My next chemo date I don't know, nobody is picking up the phone in the lung team."*

The system then aims to:

1. **Infer intent from free talk** — symptom report, confirmation, admin/appointment query, general information question, or message for another team
2. **Verify intent with one confirmation** — "It sounds like you want to tell us your blood test is done today. Is that right?" `[Yes] [No]`
3. **Scan the whole utterance for safety phrases** regardless of intent — fever, temperature, chest pain, breathless, feeling very unwell
4. **Extract facts already provided**, linked to evidence of what the patient actually said
5. **Compare with information required by the UKONS pathway** for that symptom
6. **Ask only the next missing or unclear question**, one at a time — RAG is used for *questioning*, not for giving the patient answers
7. **Verify vague answers to a categorical band** — e.g. "four-five times" → patient taps `[1-3] [4-6] [7-9] [10+]`
8. **Produce a validated structured report** for nurse review
9. **Display the source UKONS grading/management excerpt** alongside the report

The patient never receives a grade, a diagnosis, or treatment advice from the system.

---

## Designing for Reluctant and Unable Communicators

Translation alone is not enough. The prototype is designed to lower the threshold to report:

* **Talk, don't type:** Voice-first input in the preferred language (English/Urdu), with audio read-back, so literacy is not required to participate.
* **At their own pace:** Asynchronous reporting at home. The patient can pause, re-record and correct themselves — unlike a live, pressured helpline call.
* **Privacy for sensitive symptoms:** Diarrhoea, vomiting, bowel and skin symptoms can be reported privately by voice and categorical taps, without a live interpreter or family member listening.
* **Verification without interrogation:** If a patient is vague, the system gently asks for one tap to confirm, rather than a nurse repeatedly asking on the phone.
* **Representative reporting is explicit:** If a family member helps or reports on behalf of the patient, the source is flagged on the dashboard — `Reported by: Daughter, using patient's phone` — so the nurse knows the history is second-hand.
* **Acknowledgement builds trust:** A silent submission will not be repeated next week. The patient receives: Instant Receipt → Seen by Nurse → Nurse Response, in their language, with audio.
* **Human route is always visible:** An "I feel worse / I need urgent help" option is on every screen. Digital reporting is an additional route, never the only route.

---

## Two Workflows

### 1. Inbound Stable Report

Patient initiates via a demo link/QR (WhatsApp-style interface for hackathon demonstration only). They report a symptom, confirmation, admin query, or general question.

The system routes it to the correct queue. Most non-clinical reports should never consume Acute Oncology clinical grading time.

**Nurse Dashboard Queues:**

`PRIORITY INCOMPLETE (safety stop)` | `SYMPTOM REPORTS` | `INFO REQUESTS (vaccine/food)` | `ADMIN / FORWARD TO OTHER TEAM` | `CONFIRMATIONS LOGGED (bloods done)`

For information requests, the nurse replies asynchronously using approved templates. The system does not give the patient a personalised "yes, you can have this vaccine / eat this" answer.

### 2. Scheduled Follow-Up — Patient-Initiated Reporting

Example: A patient is discharged with immune-related diarrhoea and colitis (UKONS Guideline 21) on a reducing steroid taper (Guideline 29). Currently the team make a weekly phone call to check progress.

In this model, the nurse instructs the patient **once** at discharge:

> "Report every **Monday**, or on any day you feel worse, using the same link. Just talk and tell us it's your weekly check."

**No nurse-generated link per week.** No extra nurse admin.

The patient reports on Monday. The dashboard links reports into a longitudinal trend:

Week 1 - Mon: ✓ Received | Stools 4-6 | Blood: No | Steroid taken: Yes Week 2 - Mon: ✓ Received | Stools 1-3 | Blood: No | Steroid missed 2 days ⚠ Week 3 - Mon: ⏳ Due today — Not yet received


If a report is overdue, it is flagged **OVERDUE**. Non-response is never assumed to mean the patient is well.

If a follow-up report shows worsening (e.g. stools back to 7-9, blood returning, fever, steroids stopped), the routine flow stops, the patient is directed to call, and the report is flagged priority.

### Two-Way Communication

Acknowledgement is a core safety and trust feature:

1. **System Receipt (instant, not clinical):** "Your report was received at 09:15. It has not yet been reviewed by a nurse."
2. **Nurse Viewed:** "Seen by Acute Oncology Nurse at 14:10"
3. **Nurse Response:** Nurse selects an approved response template and can add a short note. The patient receives it in their language as text and audio, and taps `[I understood]`.

The AI cannot close an encounter. A clinician does.

---

## Dual Purpose: Patient Facilitation + Nurse Upskilling

This is not only about collecting data. It addresses a daily clinician problem:

A nurse escalates: *"Doctor, this patient has diarrhoea."*
The clinician asks: Did you ask about immunotherapy? Last treatment? Blood? Temperature? Stool count above baseline?
Too often, those questions were not asked — not through lack of care, but because junior, bank, and new-to-oncology nurses cannot be expected to memorise 42 complex UKONS guidelines, especially under staffing pressure.

The nurse dashboard places the guideline card **next to** the patient report:

| Left: Patient Report | Right: UKONS Teaching Card |
| :--- | :--- |
| What the patient actually said (verbatim) | Source guideline, number and page (e.g. UKONS V4 G21, p28) |
| Verified facts in green, Unknowns in red | Grading table, with the criteria matching this patient highlighted |
| Treatment history as reported | What would change the grade (grade boundaries) |
| Missing information flagged | Investigations and checks the nurse still needs to do |
| Trend across weeks for follow-ups | Management excerpt by grade, and cross-references (e.g. to Guideline 12 Neutropenic Sepsis) |

The system **never pre-selects a grade**. The nurse reviews, verifies verbally where needed, assigns the grade herself, and decides the action.

In doing so, she learns the guideline in the workflow, at the point of care. After reviewing 20 diarrhoea reports this way, a junior nurse builds real competence — without needing to be taken off a short-staffed rota for a training day. This is just-in-time upskilling for a stretched workforce.

---

## Model Architecture — 100% Meta Models

Built for the Meta AI Developer Hackathon on Meta open models. No competitor ASR or LLM models.

| Logical Agent | Meta Model | Responsibility |
| :--- | :--- | :--- |
| [0] Intent Agent | Llama 4 Scout | Infers intent from free talk: symptom / confirmation / admin / info / message for other team |
| [1] Transcription Agent | SeamlessM4T v2 Large | Urdu audio → Urdu transcript + English translation |
| [2] Transcription Verification Agent | Llama 4 Scout | Flags numbers, negation, medication names, temperatures and durations for patient tap-confirmation |
| Safety Gate | Llama Guard 4 + deterministic rules | Detects fever / urgency in any utterance → stops form, directs to helpline |
| [3] Clinical Fact Extraction Agent | Llama 4 Maverick | Extracts structured facts **only with an evidence span** from what the patient said |
| [4] Extraction Checker Agent | Llama 4 Maverick (independent call) | Rejects facts if a number changed, negation was flipped, meaning was inferred, or "don't know" became "no". It cannot rewrite facts. |
| [5] Guideline Agent | Deterministic state | Loads the UKONS-required information set for the selected symptom from the Question Registry |
| [6] Missing-Information Agent | Llama 4 Scout + state machine | Required information − validated facts = only the next question. Stops early; does not ask 40 questions. |
| [7] Question / Language Agent | SeamlessM4T v2 Large | Converts an approved question template, and nurse acknowledgement, into simple Urdu text + audio |

Deterministic Python application code handles encounter state, queues, IDs, timestamps, and hard safety rules. Language models are used only for tasks that require language understanding.

### Hybrid Question Model — ePROMs-Style Fixed Data + Free Speech

Not all UKONS questions can be safely asked in the same way. Each question in the Registry is classified:

* **Type A — Fixed Categorical Only:** Large tap buttons for grade-defining facts.
  *Stools above normal? `[1-3] [4-6] [7-9] [10+] [Don't Know]`*
* **Type B — Voice First, Then Tap to Confirm:** Patient speaks naturally in their language; the system proposes a category; the patient confirms it.
  *Used for treatment names and symptom descriptions.*
* **Type C — Nurse Only, Never Ask the Patient:** Information a patient cannot reliably provide.
  *e.g. neutrophil count, NEWS score, DPD deficiency consideration, blood results. These appear on the teaching card as nurse checks.*

Free speech is an input method. The clinical record is always a confirmed categorical fact, or an explicitly flagged `UNKNOWN`.

---

## Safety Principles

1. **Talk-first, no bombardment.** No 20-item checklist for patients to click "No" through to reach the questionnaire.
2. **Stable patients only by design.** A simple front gate in the patient's language: "I feel very unwell and need help now" vs "I feel stable to report my symptoms".
3. **Fever on cancer treatment is a hard stop.** It overrides diarrhoea, admin, confirmation and every other intent. The form stops and the patient is directed to call. (UKONS Guideline 12)
4. **Transcription is uncertain evidence, not truth.** Medication names, numbers, temperatures, doses, durations and negation always require verification.
5. **No evidence span = no fact.** Every extracted fact must link to what the patient said or tapped.
6. **Unknown is never a negative.** Missing information is displayed in red as `UNKNOWN / NOT ASKED`, never silently converted to "No".
7. **Maximum 2 clarifications per fact.** After that, flag as unknown for the nurse. Do not exhaust an unwell patient.
8. **Patient-reported data is not a clinical grade.** The nurse confirms the UKONS grade after review, examination and results where required.
9. **The AI cannot close an encounter,** give treatment advice to a patient, or send a clinical reply without nurse approval.
10. **Acknowledgement is mandatory.** Submission into a black hole destroys trust and future reporting.

---

## Guideline-Grounded Retrieval

Retrieval-Augmented Generation (RAG) in this project retrieves **questions to ask and source excerpts to show the nurse** — not treatment answers to give the patient.

**Source:** UKONS Acute Oncology Initial Management Guidelines **Version 4.0 (13.02.2023)**

**Deep module for the demo:** Diarrhoea — a critical safety distinction
* Guideline 6: Diarrhoea (SACT-related, p13) — e.g. capecitabine / 5FU / irinotecan
* Guideline 21: Diarrhoea & Colitis (immune-related adverse event, p28) — immunotherapy

Both present with 4-6 stools/day at Grade 2, but their pathways are different. Correct capture of treatment history is therefore the key routing question, and both excerpts are shown to the nurse for diarrhoea so she can confirm the route.

**Follow-up module:** Guideline 29 Steroid Tapering Guidance (p36)
**Hard-stop module:** Guideline 12 Suspected Neutropenic Sepsis (p19)

Grading and management excerpts on the nurse card are manually curated for the demo symptoms to be faithful to source, with guideline number and page number displayed for verification.

---

## Encounter and Privacy Architecture

A deterministic application layer manages: encounter creation, opaque Encounter ID, status, timestamps, preferred language, queue management, human acknowledgement and closure.

The LLM receives only the clinical context necessary for extraction, not unnecessary patient identifiers.

**Hackathon demo constraints:**
* Synthetic patient data only
* No real patient data, no EPR/PAS matching
* WhatsApp-style interface is a demonstration interface only, not a production WhatsApp integration
* Demo data is deleted after use

Production identity verification, EPR/SACT authoritative treatment lookup, NHS Login, UK data hosting, DPIA, DCB0129 clinical safety case and DTAC assessment are explicitly **future work**.

---

## 7-Day Solo Execution Plan

This is a solo clinician-led build, supported by Meta models, over 1 week within a $150 Meta API credit budget (Llama API only; SeamlessM4T v2 is an open Meta model served via Hugging Face).

| Phase | Day | Work Completed By | Deliverable |
| :--- | :--- | :--- | :--- |
| **Phase 0: Clinical Content Lock** | 1 | Clinician | Diarrhoea Question Registry (A/B/C classified), closed drug list, UKONS G6/G21 teaching cards. Urdu wording verified by clinical lead. |
| **Phase 1: Golden Cases & Safety Rules** | 2 | Clinician + Python rules | 10 synthetic cases from call audit (admin, confirmation, diarrhoea, follow-up, fever). Expected intent, band, route and unknowns for each. |
| **Phase 2: Talk-First Patient App** | 3 | Llama 4 Scout + SeamlessM4T | WhatsApp-style Streamlit app. Stable gate → free talk → intent inference → 1-tap intent verification. |
| **Phase 3: Verification Pipeline** | 4 | Llama 4 Maverick + Rules | Transcription verification, extraction with evidence spans, independent checker rejecting changed numbers/negation. Final patient read-back in Urdu. |
| **Phase 4: Nurse Dashboard** | 5 | Streamlit | Queues, verified/unknown report, UKONS teaching card side-by-side, nurse grade assignment, acknowledgement templates. |
| **Phase 5: Monday Follow-Up** | 5-6 | State machine | Steroid taper trend view (Week 1 vs Week 2), overdue flag, priority flag on worsening. |
| **Phase 6: Testing** | 6 | Automated golden-case run | Pass criteria: 100% immunotherapy recognition, 100% fever hard-stop, 0 unknown→no conversions, 0 facts without evidence. |
| **Phase 7: Demo & Pitch** | 7 | Clinician | 3-case live demo, results, scalability assessment, future roadmap. $50 API reserve held for live judging. |

**Scalability test for the hackathon:**
1. Can an Urdu-speaking patient complete a stable report unaided in < 3 minutes?
2. Do critical facts (immunotherapy status, blood, stool band) survive verification in 10/10 golden cases?
3. Can a junior nurse review a structured report in < 60 seconds compared with a voicemail callback?

---

## Hackathon Scope

**In scope:**
English + Urdu, talk-first intent routing, Diarrhoea deep module, Fever hard-stop, confirmation/admin/info routing, Monday steroid-taper follow-up with two-way acknowledgement, nurse dashboard with teaching card.

**Out of scope (Future Phase):**
Production messaging channels, real patient deployment, EPR/PAS and SACT system integration, validated identity matching, additional languages, all 42 UKONS guidelines, formal clinical validation and regulatory approval.

The initial prototype focuses on representative languages relevant to the local population in Bradford, UK, where there is significant social deprivation and language-related health inequality. The purpose is to develop and test the underlying multilingual safety principles, not to claim comprehensive language coverage. Additional languages would be validated and added subsequently.

---

## Technology

* **Llama 4 Scout** — fast intent routing, transcription verification, missing-information logic
* **Llama 4 Maverick** — high-accuracy structured extraction and independent checking
* **Llama Guard 4** — safety classification for urgent mentions
* **SeamlessM4T v2 Large** — Meta's open speech model: Urdu speech in, Urdu speech out for patient questions and nurse acknowledgements
* **Streamlit (Python)** — demonstration patient interface and nurse dashboard
* **Deterministic Python** — encounter state, question registry, safety hard-stops, number/negation/drug rules, queues

Architecture is model-aware so individual components can be evaluated and replaced independently.

---

## Prior Work

The clinical lead has undertaken multiple Acute Oncology quality improvement projects, presentations analysing why patients call the helpline and common presenting symptoms, and work involving ePROMs. This repository represents the new hackathon implementation integrating that prior learning with natural-language interaction, multilingual voice, transcription safety, guideline-grounded question retrieval, and human clinical review.

Development during the hackathon will be documented through this repository's commit history.

---

## Future Development

* Invited, EPR-linked patient access with authoritative SACT/immunotherapy treatment lookup (removing reliance on patient recall for pathway routing)
* Validation of additional Bradford-relevant languages through forward/back-translation and patient co-design
* Automated reminders for overdue follow-up reports
* Broader UKONS pathway coverage with senior nurse sign-off per guideline card
* Formal ASR performance evaluation in Urdu for clinical vocabulary
* Clinical safety testing, information governance, DCB0129 / DTAC
* Prospective pilot with the Acute Oncology team measuring helpline diversion, nurse time saved, junior nurse competency development, and reporting rates among patients with language barriers

---

## Disclaimer

Acute Oncology Helper is an experimental hackathon prototype.

It is not validated for clinical use, is not intended to diagnose or treat disease, and must not be used to replace professional medical assessment, the 24-hour Acute Oncology helpline, or emergency services.

All prototype demonstrations must use synthetic or appropriately non-identifiable test data.

