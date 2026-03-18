# PatentPath User Manual

## 1. Introduction

PatentPath is an AI-guided platform for prior art discovery and innovation planning.
It helps students, inventors, and project teams:

- convert invention ideas into searchable patent queries,
- retrieve and rank prior art results from Espacenet,
- understand novelty risk using transparent NLP scoring,
- generate AI-assisted gap analysis and feasibility insights,
- prepare a structured patent preparation report.

PatentPath is designed for academic and innovation support. It is not a legal advice system.

## 2. Getting Started

### 2.1 Create an Account

1. Open the app in your browser.
2. Go to Register.
3. Enter display name, email, and password (minimum 8 characters).
4. Submit the form.

### 2.2 First Login

1. Open Login.
2. Enter your email and password.
3. After authentication, you are redirected to the Dashboard.

## 3. Creating Your First Innovation Project

1. From Dashboard, click New Project.
2. Fill in:
   - Project title
   - Problem statement
   - Optional domain IPC class
3. Save the project.
4. Open the project workspace to access searches, timeline, notes, and settings.

UI notes:

- Project cards show project status and session counts.
- Project pages provide tabs for Searches, Timeline, Notes, and Settings.

## 4. Conducting a Prior Art Search

### 4.1 Write an Effective Problem Statement

Recommended quality checklist:

- Be specific about the technical objective.
- Include domain vocabulary and component names.
- Explain constraints and intended behavior.
- Target at least 200 characters when possible.

Better inputs produce stronger keyword extraction and better CQL suggestions.

### 4.2 Understand the Auto-Generated CQL Query

After entering your invention description, use Preview Query to inspect generated CQL.

What happens:

- keywords are extracted,
- IPC suggestions are proposed,
- syntax checks validate the generated query.

You can edit the CQL manually before execution.

### 4.3 Use the Filter Panel

Available filters:

- Date range
- Country codes (example: EP, WO, US, JP, CN, KR, DE, FR, GB)
- IPC class codes
- Applicant name
- Legal status preference

Use filters to increase precision after an initial broad search.

### 4.4 Execute Search and Interpret Loading Phases

On execution, the workflow typically progresses through:

1. Building query
2. Querying Espacenet
3. Scoring results
4. Generating gap analysis

Duration depends on API quota, network, and result size.

## 5. Reading Your Results

### 5.1 Similarity Score Components

Each ranked result includes a composite similarity score:

- BM25 (30 percent)
- TF-IDF cosine (50 percent)
- Semantic cosine (20 percent)

Composite formula:

SS = 0.30 * BM25 + 0.50 * TF-IDF + 0.20 * Semantic

### 5.2 Risk Labels

Risk interpretation uses score thresholds:

- HIGH: SS >= 0.80
- MEDIUM: 0.55 <= SS < 0.80
- LOW: 0.30 <= SS < 0.55
- MINIMAL: SS < 0.30

General reading guidance:

- HIGH/MEDIUM: strong overlap with existing prior art; refine and differentiate.
- LOW/MINIMAL: lower overlap; still validate with legal review.

### 5.3 Narrow Results with Sidebar Filters

Use client-side filters (risk/date/country) to focus on the most relevant subset without rerunning the entire search.

### 5.4 View Patent Details and Family Members

Open a result to view:

- bibliographic metadata,
- abstract and claims excerpt,
- legal status,
- INPADOC family members and links.

Family view helps you inspect related filings across jurisdictions.

## 6. Gap Analysis

### 6.1 Covered Aspects vs Innovation Gaps

Gap analysis divides findings into:

- Covered aspects: parts of your idea likely anticipated by prior art.
- Gap aspects: parts not clearly covered, representing innovation opportunities.

### 6.2 Innovation Suggestions

Use suggestions to improve novelty by:

- modifying architecture,
- adding differentiating constraints,
- redefining technical claims scope.

Treat suggestions as ideation support, then validate technically and legally.

### 6.3 Feasibility Assessment

Feasibility includes:

- Technical readiness
- Domain specificity
- Claim drafting potential

A composite percentage summarizes overall readiness direction.

## 7. Managing Your Project

### 7.1 Save Notes and Ideas

Use project notes to capture:

- claim ideas,
- design decisions,
- references to specific sessions.

### 7.2 Use Timeline View

Timeline displays project activity events such as searches, analyses, and report generation.

### 7.3 Track Novelty Risk Over Time

Use risk trend charts to compare sessions and evaluate whether refinements are reducing novelty risk.

## 8. Generating Your Patent Preparation Report

### 8.1 What the Report Contains (10 Sections)

Generated PDF report includes:

1. Invention title and field
2. Problem statement
3. Prior art search summary
4. Technology gap analysis
5. Proposed invention description
6. Distinguishing features
7. Draft claims outline
8. Feasibility assessment
9. Recommended next steps
10. Appendix of analyzed patents

### 8.2 Download and Share

1. Trigger report generation from the report panel.
2. Wait for status READY.
3. Download PDF.
4. Share with your team and advisors.

### 8.3 Legal Disclaimer and Next Steps

The report is a computational support artifact, not a legal patentability opinion.
Always consult a qualified patent attorney or patent agent before filing.

## 9. Troubleshooting

### 9.1 "Espacenet is busy" or quota errors

Symptoms:

- rate-limit errors,
- quota exceeded messages,
- retry-after countdown.

Actions:

- wait for the retry window,
- narrow repeated requests,
- try again later when OPS usage resets.

### 9.2 Search returns 0 results

Actions:

- broaden wording in the problem statement,
- remove restrictive filters,
- test alternate IPC classes,
- reduce applicant/date constraints.

### 9.3 Gap analysis takes too long

Expected behavior:

- complex sessions may require extra processing time.

Actions:

- keep the session open and poll status,
- verify backend and worker health,
- retry if status stays unchanged for an extended period.

## 10. Technical Notes

### 10.1 IPC Classification Basics

IPC (International Patent Classification) organizes inventions into sections and technical classes.
Using correct IPC filters improves retrieval relevance and reduces noise.

### 10.2 CQL Syntax Quick Reference

Common examples:

- Title/abstract term search:
  - (ti="autonomous" OR ab="autonomous")
- IPC class filter:
  - ipc="G06N"
- Date range filter:
  - pd>=20200101 AND pd<=20251231
- Country/publication filter pattern:
  - pn="EP" OR pn="WO"

Tips:

- keep parentheses balanced,
- avoid over-constraining with too many AND clauses,
- iterate from broad to narrow.

---

Legal notice: PatentPath outputs are for academic innovation support only and do not replace professional legal counsel.
