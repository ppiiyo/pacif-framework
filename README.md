# PACIF v3.0
**Predictive Alignment & Causal Information Flow**

PACIF is a diagnostic tool for measuring how strongly an algorithm shapes user behavior, whether that signal is reliable, and whether it changes over time.

It is designed for:
- recommendation systems,
- AI audit and compliance workflows,
- research on feedback loops and behavioral lock-in.

## Why this matters

Recommendation systems create feedback loops: the system adapts to users, and users adapt to the system.

PACIF helps answer practical questions like:
- Is the algorithm becoming too “sticky”?
- Are users being funneled into narrow content paths?
- Did behavior change after a model update?
- Can we trust the observed signal?

## What PACIF does

PACIF measures:
- predictive alignment between user actions and system context,
- reliability of the estimate,
- drift over time,
- directional asymmetry in behavior.

## What PACIF does not do

PACIF does **not**:
- prove causality,
- measure wellbeing or satisfaction,
- prove manipulation,
- replace randomized experiments.

It is an observational diagnostic tool, not a causal verdict.

## Quick demo

Try the live demo:

**[PACIF Streamlit Demo](https://pacif-demo.streamlit.app)**

## Example output

Typical output includes:
- a score for predictive alignment,
- a reliability flag,
- a drift status,
- a time-series view across windows.

If the estimate is marked **UNRELIABLE**, the sample is too small or too sparse for a safe conclusion.

## Data sources for testing

PACIF can be tested on:
- Yambda-5B,
- Spotify Music Streaming Sessions Dataset,
- OTTO session data,
- other session-based recommendation logs.

## Installation

```bash
git clone https://github.com/pacif-framework/pacif-core
cd pacif-core
pip install -r requirements.txt


streamlit run streamlit_app.py



