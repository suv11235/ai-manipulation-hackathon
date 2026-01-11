# Implementation Roadmap

## Current Status: ✅ Strategy Complete

You now have:
- ✅ **plan.txt**: Original research proposal
- ✅ **STRATEGY.md**: Comprehensive implementation strategy
- ✅ **QUICKSTART.md**: Step-by-step setup guide
- ✅ **README.md**: Project overview
- ✅ **requirements.txt**: Dependencies
- ✅ **Project structure**: Directories created
- ✅ **src/config.py**: Configuration template

## Next Actions (Priority Order)

### Immediate (Next 30 minutes)

1. **Set up environment**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Create .env file**
   ```bash
   # Create .env file manually with:
   OPENAI_API_KEY=your_key_here
   ANTHROPIC_API_KEY=your_key_here  # Optional
   ```

3. **Implement first scenario** (`src/scenarios.py`)
   - Start with health_misinformation
   - Define Scenario dataclass
   - Create scenario template

4. **Implement first persona** (`src/personas.py`)
   - Start with Neutral (baseline)
   - Define Persona dataclass
   - Create system prompt

### Phase 1: Foundation (Hours 0-4)

**Priority 1: Core Classes**
- [ ] `src/scenarios.py` - All 5 scenarios
- [ ] `src/personas.py` - All 4 personas
- [ ] `src/feedback_simulator.py` - Feedback generation
- [ ] `src/conversation.py` - Conversation management

**Priority 2: Testing**
- [ ] Test scenario generation
- [ ] Test persona injection
- [ ] Test single conversation loop

### Phase 2: Scoring (Hours 4-6)

**Priority 1: Scorer**
- [ ] `src/manipulation_scorer.py` - LLM-judge scoring
- [ ] Define manipulation taxonomy
- [ ] Create scoring prompts

**Priority 2: Integration**
- [ ] Integrate scorer into conversation loop
- [ ] Test scoring on known examples
- [ ] Validate scoring consistency

### Phase 3: Baseline (Hours 6-8)

**Priority 1: Baseline Run**
- [ ] `experiments/run_baseline.py`
- [ ] Run Neutral × all feedback × 5 scenarios
- [ ] Validate system working

**Priority 2: Calibration**
- [ ] Check scores are reasonable
- [ ] Verify feedback patterns
- [ ] Adjust if needed

### Phase 4: Full Experiment (Day 2, Hours 0-3)

**Priority 1: Full Matrix**
- [ ] `experiments/run_full_experiment.py`
- [ ] Run 4 personas × 4 feedback × 5 scenarios
- [ ] Implement checkpointing/error handling

**Priority 2: Data Validation**
- [ ] Verify all conversations complete
- [ ] Check data integrity

### Phase 5: Analysis (Day 2, Hours 3-5)

**Priority 1: Metrics**
- [ ] `src/metrics.py` - All metric calculations
- [ ] Calculate core metrics
- [ ] Calculate tactic metrics

**Priority 2: Analysis**
- [ ] `src/analysis.py` - Statistical analysis
- [ ] Answer research questions
- [ ] Identify patterns

### Phase 6: Visualization (Day 2, Hours 5-8)

**Priority 1: Core Plots**
- [ ] `src/visualization.py`
- [ ] Persona × Feedback matrix
- [ ] Trajectory plots
- [ ] Ratchet effect visualization

**Priority 2: Dashboard/Report**
- [ ] Interactive dashboard (if time)
- [ ] Findings document
- [ ] Key insights summary

## Decision Points

### Model Selection
- **Start with**: GPT-4 (most capable)
- **Expand to**: GPT-3.5-turbo, Claude (if time/budget allows)
- **Fallback**: Single model if time constrained

### Scope Reduction (if needed)
- Reduce to 3 scenarios (health, financial, relationship)
- Reduce to 1 model (GPT-4)
- Reduce to 5 turns (instead of 10)
- **Still answers core RQs with reduced scope**

### Scoring Approach
- **Primary**: LLM-judge (GPT-4)
- **Enhancement**: Lexical markers (if time)
- **Validation**: Manual spot checks

## Success Criteria

### Minimum Viable
- [ ] 4 personas working
- [ ] 4 feedback patterns working
- [ ] 5 scenarios defined
- [ ] Scorer functional
- [ ] Baseline complete (20 conversations)
- [ ] Core metrics calculated
- [ ] 2+ visualizations

### Full Success
- [ ] Full experiment (80+ conversations)
- [ ] All 5 RQs answered
- [ ] Persona signatures identified
- [ ] Ratchet effect demonstrated
- [ ] Findings documented

## Time Management Tips

1. **Start simple**: Get one scenario + one persona working first
2. **Test early**: Run small experiments before full matrix
3. **Parallelize**: Run conversations in parallel if possible
4. **Checkpoint**: Save after each conversation
5. **Prioritize**: Focus on core RQs if time runs short

## Getting Help

- Review `STRATEGY.md` for detailed design decisions
- Check `QUICKSTART.md` for implementation examples
- See `plan.txt` for research context

## Progress Tracking

Update this file as you complete tasks:
- [ ] Environment setup
- [ ] Scenarios implemented
- [ ] Personas implemented
- [ ] Feedback simulator working
- [ ] Scorer implemented
- [ ] Baseline complete
- [ ] Full experiment running
- [ ] Analysis complete
- [ ] Visualizations done
- [ ] Report written

---

**Current Phase**: Ready to start implementation
**Next Step**: Set up environment and implement first scenario

