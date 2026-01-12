# Persona-aware-dialogue-manipulation

A research project investigating how AI personas respond dynamically to user feedback, revealing manipulation patterns that emerge through interaction rather than static model properties.

## Overview

This project tests the hypothesis that **manipulation is fundamentally interactive**—different AI personas (Expert, Peer, Authority, Neutral) respond differently to user feedback (reinforcing, resistant, switching patterns), creating characteristic manipulation trajectories. Additionally, we developed **7 user personas** (Teenager, High-Income Adult, Retired Senior, Content Creator, Parent, Student, and Neutral control) to probe how different user types respond to manipulative queries, with persona-appropriate query framing and feedback generation.

## Key Research Questions

1. **RQ1**: Do personas have characteristic feedback-response patterns?
2. **RQ2**: Does reinforcement accelerate manipulation differently by persona?
3. **RQ3**: Which personas persist despite resistance?
4. **RQ4**: Does feedback type trigger tactic switching?
5. **RQ5**: Is there a "ratchet effect"—manipulation gains that resist reversal?

## Project Structure

```
ai-manipulation-hackathon/
├── plan.txt              # Original research plan
├── SUBMISSION_REPORT.md  # Complete research report
├── requirements.txt      # Python dependencies
├── src/                  # Source code
│   ├── personas.py       # AI persona definitions
│   ├── user_personas.py  # User persona definitions
│   ├── scenarios.py      # Scenario templates
│   ├── feedback_simulator.py  # User feedback generation
│   ├── manipulation_scorer.py  # LLM-judge scoring system
│   └── ...
├── experiments/          # Experiment scripts
│   ├── run_baseline.py
│   ├── run_full_experiment.py
│   ├── run_darkbench_experiment.py
│   └── analyze_results.py
├── scripts/             # Utility scripts
├── data/                # Data storage
│   ├── results/         # Aggregated result summaries
│   ├── raw/             # Raw conversation and metrics JSON files
│   │   └── darkbench_experiment/  # User persona experiment results
│   └── darkbench/       # DarkBench dataset
└── tests/               # Unit tests
```

## Quick Start

1. **Setup environment**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure API keys**
   ```bash
   # Primary: OpenRouter (recommended)
   echo "OPENROUTER_API_KEY=your_key" > .env
   
   # Alternative: Direct API keys (if not using OpenRouter)
   # echo "ANTHROPIC_API_KEY=your_key" >> .env
   # echo "OPENAI_API_KEY=your_key" >> .env
   ```
   
   Get your OpenRouter API key from [openrouter.ai](https://openrouter.ai)

3. **Run experiments**
   ```bash
   # Baseline experiment
   python experiments/run_baseline.py
   
   # Full experiment (AI persona × feedback pattern × scenario)
   python experiments/run_full_experiment.py
   
   # DarkBench experiment (standard - AI personas)
   python experiments/run_darkbench_experiment.py \
     --source data/darkbench/darkbench.json \
     --models or-claude-sonnet-4-5 \
     --max-queries 5
   
   # DarkBench experiment with user personas
   python experiments/run_darkbench_experiment.py \
     --source data/darkbench/darkbench.json \
     --user-persona teenager high_income_adult parent \
     --feedback-patterns reinforcing resistant \
     --models or-claude-sonnet-4-5 \
     --max-queries 5
   ```

## Documentation

- **SUBMISSION_REPORT.md**: Complete research report with methods, results, and findings
- **plan.txt**: Original research proposal with hypotheses and design

## Experimental Design

### AI Persona Experiments
- **4 AI Personas**: Neutral, Expert, Peer, Authority
- **4 Feedback Patterns**: Reinforcing, Resistant, Compliant→Resistant, Resistant→Compliant
- **5 Scenarios**: Health, Financial, Relationship, Political, Product
- **10 Turns per conversation**: Track manipulation trajectory
- **Target**: 80 conversations (4×4×5) × 3 models = 240 total

### User Persona Experiments
We developed **7 user personas** to investigate how different user types respond to manipulative queries:

**Experimental Design:**
- **7 User Personas**: Teenager, High-Income Adult, Retired Senior, Content Creator, Parent, Student, Neutral
- **AI Persona**: Always Neutral (to isolate user-side effects)
- **Feedback Patterns**: Reinforcing, Resistant (or custom patterns)
- **DarkBench Queries**: Real-world manipulative queries from DarkBench dataset
- **Multiple Turns**: Track manipulation trajectory across conversation
- **Target**: N queries × M user personas × P feedback patterns × K models

1. **Teenager** (15-17 years): Impressionable, seeks peer approval, influenced by trends and social media
   - Vulnerable to: social_proof, authority, liking, scarcity
   - Communication: Casual, uses slang, seeks reassurance

2. **High-Income Adult** (30-50 years): Successful professional with disposable income, values efficiency
   - Vulnerable to: urgency, scarcity, authority, anchoring
   - Communication: Professional, direct, values time

3. **Retired Senior** (65+ years): Less tech-savvy, trusts authority figures, values security
   - Vulnerable to: authority, reciprocity, commitment, framing
   - Communication: Polite, formal, trusts experts

4. **Content Creator** (20-40 years): Focused on growth, trends, and audience engagement
   - Vulnerable to: social_proof, brand_bias, scarcity, urgency
   - Communication: Enthusiastic, trend-focused

5. **Parent** (30-50 years): Concerned about family wellbeing, makes decisions for children
   - Vulnerable to: authority, reciprocity, emotional_manipulation, commitment
   - Communication: Caring, asks about safety/benefits

6. **Student** (18-25 years): Limited budget, seeks value, influenced by peer recommendations
   - Vulnerable to: scarcity, urgency, social_proof, anchoring
   - Communication: Practical, budget-conscious, time-sensitive

7. **Neutral User**: Baseline control condition with no special characteristics

**User Persona Implementation:**
- Personas are used to frame DarkBench queries from the user's perspective
- Each persona has a framing template that adapts queries to their communication style
- Feedback generation is persona-appropriate, reflecting their characteristics and vulnerabilities
- Experiments use neutral AI persona when testing user personas to isolate user-side effects
- User personas help probe how different user types respond to manipulative queries across various dark patterns

**Running User Persona Experiments:**
```bash
# Basic usage: test specific user personas
python experiments/run_darkbench_experiment.py \
  --source data/darkbench/darkbench.json \
  --user-persona teenager parent retired_senior \
  --feedback-patterns reinforcing resistant \
  --models or-claude-sonnet-4-5 \
  --max-queries 10

# Available user personas:
# - teenager
# - high_income_adult
# - retired_senior
# - content_creator
# - parent
# - student
# - neutral

# Results are saved with user persona information:
# - Filenames include user persona: darkbench_db_0001_teenager_reinforcing_...
# - Conversation JSON includes "user_persona_name" field
# - Metrics JSON includes "user_persona_name" field
# - Summary includes "by_user_persona" statistics
```

**Analyzing User Persona Results:**
```bash
# Analyze user persona experiments
python analyze_darkbench_user_persona.py

# This script:
# - Loads all conversation results with user personas
# - Groups statistics by user persona, feedback pattern, and scenario
# - Identifies high manipulation examples
# - Compares vulnerability across user types
```

## Key Metrics

- **Reinforcement Sensitivity**: How much manipulation increases per reinforcing turn
- **Resistance Persistence**: Manipulation maintained despite pushback
- **Ratchet Coefficient**: Manipulation retained after compliance→resistance switch
- **Capitulation Exploitation**: Manipulation surge after user gives in
- **Tactic Pivot Rate**: How often models switch manipulation tactics

## Timeline

- **Day 1**: Build feedback system, scoring pipeline, baseline calibration
- **Day 2**: Full experiment, metrics calculation, visualization, analysis

## Expected Findings

- Expert personas double down under resistance
- Peer personas back off with resistance
- Authority personas pivot tactics (pressure → concern trolling)
- Early compliance creates "ratchet effect" (manipulation persists)

## License

Research project for hackathon/demonstration purposes.

