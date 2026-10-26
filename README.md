# -acute-oncology-helper
Multilingual, voice-enabled acute oncology helper for natural-language symptom assessment, guideline-grounded support and human clinical review.
Acute Oncology Helper

A multilingual, voice-enabled acute oncology helper for natural-language symptom assessment, guideline-grounded clinical support, and human review.

Hackathon prototype — not for clinical use.
This project is being developed as a proof of concept using synthetic/test patient data. It is not a medical device and must not be used to make clinical decisions or provide autonomous medical advice.

The Problem

Patients receiving cancer treatment can develop acute symptoms that require timely assessment by an acute oncology service.

Traditional digital symptom-assessment tools often rely on forms or rigid questionnaires. Patients, however, naturally describe several symptoms together, provide information in different orders, use everyday terminology, and may prefer to communicate by voice or in a language other than English.

Acute Oncology Helper explores whether multimodal AI can support a more natural interaction while keeping clinical decision-making with healthcare professionals.

The Concept

Patients communicate naturally using text or voice.

For example:

“I’ve had diarrhoea about six times since yesterday, I’ve been sick twice and I’m feeling dizzy.”

The system aims to:

1. Identify all symptoms mentioned by the patient.
2. Reflect its understanding back to the patient where appropriate.
3. Explore one symptom at a time using an open question first.
4. Extract information the patient has already provided.
5. Compare this with the information required by the relevant acute oncology pathway.
6. Ask missing or clarification questions individually when required.
7. Retrieve relevant guideline/pathway evidence.
8. Produce a structured encounter summary for human clinical review.

The aim is to support clinical information gathering — not to replace clinical judgement.

Proposed Workflow

Patient contact
      ↓
Encounter initialisation
      ↓
Patient confirms supplied details
      ↓
Encounter ID generated
      ↓
Preferred communication language
      ↓
Patient-reported cancer and treatment context
      ↓
Natural-language symptom description
(text or voice)
      ↓
Transcription safety layer (for voice)
      ↓
Clinical information extraction
      ↓
Identify all symptoms
      ↓
Open exploration of each symptom
      ↓
Guideline/pathway gap checking
      ↓
Ask unanswered questions individually
      ↓
Retrieve relevant guideline evidence
      ↓
Structured clinical summary
      ↓
Acute Oncology dashboard
      ↓
Human clinical review and action

Conversational Assessment

The project follows a simple conversational principle:

Reflect → Open exploration → Extract → Pathway gap-check → Targeted clarification → Next symptom

Rather than immediately presenting a questionnaire, the patient is initially encouraged to describe the problem naturally.

If required clinical information is not provided spontaneously, the system asks the outstanding questions individually.

Information that has not been obtained remains explicitly unknown rather than being inferred by the AI.

Multilingual Voice and Transcription Safety

Automatic speech recognition can produce plausible but clinically significant errors.

Particular risks include:

* medication and cancer-treatment names
* numbers and symptom frequency
* temperatures
* doses
* duration and dates
* clinically important negation
* incorrect language or script detection

The project therefore treats an ASR transcript as potentially uncertain evidence rather than clinical truth.

The prototype will explore independent transcription/verification approaches and disagreement detection for clinically important information.

Where clinically significant information cannot be established reliably, the system should request clarification rather than guess.

Language Handling

Patients explicitly select their preferred communication language rather than relying solely on automatic language detection.

The initial prototype will focus on a small number of representative languages relevant to the local population in Bradford, UK. The purpose is to develop and test the underlying multilingual safety principles rather than claim comprehensive language coverage.

Additional languages could subsequently be validated and added for deployment in other populations.

Encounter and Privacy Architecture

Patient identity and encounter management are separated from LLM processing.

A deterministic application layer is responsible for:

* patient-supplied identification information
* encounter creation
* encounter status
* timestamps
* communication language
* patient-reported cancer context
* patient-reported treatment context
* queue management
* human acknowledgement
* encounter closure

After initialisation, an opaque Encounter ID is used within the AI workflow.

The LLM should receive only the clinical context necessary for the assessment rather than unnecessary patient identifiers.

For the hackathon prototype, patient information is synthetic/test data and is not matched against a real Electronic Patient Record (EPR).

Human in the Loop

The system is designed as clinical decision support rather than autonomous clinical decision-making.

The clinician remains responsible for:

* reviewing the patient’s information
* interpreting retrieved guideline evidence
* resolving uncertainty
* determining clinical urgency
* contacting the patient
* providing clinical advice
* deciding clinical action
* closing the encounter

The AI cannot autonomously close an encounter.

Guideline-Grounded Retrieval

The project will explore retrieval-augmented generation (RAG) using acute oncology pathways and guidelines.

The intended principle is:

LLM understands the conversation; approved clinical pathways define the assessment.

Relevant source material should be displayed alongside the structured patient summary so that clinicians can review the underlying evidence rather than relying on an unsupported AI conclusion.

Safety Principles

The prototype is being designed around several principles:

Use deterministic code for things that must be predictable. Use language models for tasks that genuinely require language understanding.

Never convert missing information into a negative finding.

Do not silently correct uncertain clinically important information.

Transcription uncertainty should be visible rather than hidden.

The AI should be able to say “unable to determine — requires human review.”

Clinical decision-making remains with the healthcare professional.

Hackathon Scope

The initial build will deliberately be narrow.

The first end-to-end demonstration will focus on a small number of acute oncology scenarios and establish the core architecture before expanding functionality.

Planned development sequence:

1. Encounter initialisation
2. Natural-language symptom extraction
3. Conversational symptom assessment
4. Structured clinical state
5. Guideline/pathway retrieval
6. Clinician-facing summary/dashboard
7. Voice transcription
8. Transcription uncertainty detection
9. Multilingual interaction
10. Human acknowledgement and encounter closure

Integration with real EPR/PAS systems, validated patient identity matching and production clinical deployment are outside the hackathon scope.

Technology

The prototype is being developed for the Meta AI Developer Hackathon and will explore Meta open-weight models for:

* natural-language conversation
* structured clinical information extraction
* multilingual understanding
* audio/transcription workflows
* guideline-grounded retrieval

Hackathon inference partners may be used for model serving and experimentation.

The application architecture is intentionally model- and infrastructure-aware so that individual components can be evaluated and replaced independently.

Prior Work and Hackathon Development

Previous exploratory work considered acute oncology digital forms, guideline retrieval/RAG concepts and possible conversational workflows.

This repository represents the new hackathon implementation integrating natural-language interaction, multilingual voice processing, transcription-safety mechanisms, structured clinical assessment, guideline-grounded retrieval and human clinical review.

Development undertaken during the hackathon will be documented through this repository’s commit history.

Future Development

Potential future work includes:

* EPR/PAS integration
* authoritative treatment-record integration
* broader acute oncology pathway coverage
* validation across additional languages
* formal ASR performance evaluation
* clinical safety testing
* information-governance assessment
* validated prioritisation models
* production-grade messaging integration
* prospective clinical evaluation

Disclaimer

Acute Oncology Helper is an experimental hackathon prototype.

It is not validated for clinical use, is not intended to diagnose or treat disease, and must not be used to replace professional medical assessment or emergency services.

All prototype demonstrations should use synthetic or appropriately non-identifiable test data.