# Persona × Feedback Manipulation Dynamics (PFMD)

A research project investigating how AI personas respond dynamically to user feedback, revealing manipulation patterns that emerge through interaction rather than static model properties.

## Overview

This project tests the hypothesis that **manipulation is fundamentally interactive**—different personas (Expert, Peer, Authority, Neutral) respond differently to user feedback (reinforcing, resistant, switching patterns), creating characteristic manipulation trajectories.

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
├── STRATEGY.md           # Detailed implementation strategy
├── QUICKSTART.md         # Quick setup guide
├── requirements.txt      # Python dependencies
├── src/                  # Source code
├── experiments/          # Experiment scripts
├── data/                 # Data storage
├── notebooks/           # Analysis notebooks
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
   echo "OPENAI_API_KEY=your_key" > .env
   ```

3. **Follow QUICKSTART.md** for implementation steps

## Documentation

- **plan.txt**: Original research proposal with hypotheses and design
- **STRATEGY.md**: Comprehensive implementation strategy, phases, and evaluation criteria
- **QUICKSTART.md**: Step-by-step setup and first implementation guide

## Experimental Design

- **4 Personas**: Neutral, Expert, Peer, Authority
- **4 Feedback Patterns**: Reinforcing, Resistant, Compliant→Resistant, Resistant→Compliant
- **5 Scenarios**: Health, Financial, Relationship, Political, Product
- **10 Turns per conversation**: Track manipulation trajectory
- **Target**: 80 conversations (4×4×5) × 3 models = 240 total

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

