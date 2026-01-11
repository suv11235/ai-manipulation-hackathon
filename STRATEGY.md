# PFMD Project: Implementation Strategy

## Executive Summary

This document provides a concrete strategy for designing, implementing, and evaluating the Persona × Feedback Manipulation Dynamics (PFMD) project. It breaks down the research plan into actionable technical components, implementation phases, and evaluation criteria.

---

## 1. System Architecture

### 1.1 Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                    PFMD SYSTEM ARCHITECTURE                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │   Scenario   │───▶│   Persona    │───▶│   Model      │ │
│  │   Generator  │    │   Manager    │    │   Interface  │ │
│  └──────────────┘    └──────────────┘    └────────────┬─────┘ │
│                                              │              │
│  ┌──────────────┐    ┌──────────────┐      │              │
│  │   Feedback   │───▶│  Conversation│◀─────┘              │
│  │   Simulator  │    │   Manager    │                      │
│  └──────────────┘    └──────┬───────┘                      │
│                              │                              │
│  ┌──────────────┐    ┌──────▼───────┐    ┌──────────────┐ │
│  │ Manipulation │◀───│   Turn       │───▶│   Metrics    │ │
│  │   Scorer     │    │   Tracker    │    │   Calculator  │ │
│  └──────────────┘    └──────────────┘    └──────────────┘ │
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │   Analysis   │───▶│ Visualization│───▶│   Report    │ │
│  │   Engine     │    │   Dashboard  │    │   Generator  │ │
│  └──────────────┘    └──────────────┘    └──────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Data Flow

```
1. Scenario Setup
   └─> Generate initial prompt based on scenario template
   
2. Persona Injection
   └─> Apply persona-specific system prompt
   
3. Conversation Loop (10 turns)
   ├─> Model generates response
   ├─> Manipulation scorer evaluates response
   ├─> Feedback simulator generates user response
   └─> Store turn data (response, score, feedback type)
   
4. Post-Conversation Analysis
   ├─> Calculate trajectory metrics
   ├─> Identify tactic shifts
   └─> Compute feedback response signatures
   
5. Aggregation & Visualization
   ├─> Aggregate across all conversations
   ├─> Generate persona × feedback matrices
   └─> Create visualizations
```

---

## 2. Technical Design

### 2.1 Project Structure

```
ai-manipulation-hackathon/
├── src/
│   ├── __init__.py
│   ├── config.py                 # Configuration & constants
│   ├── personas.py               # Persona definitions & prompts
│   ├── scenarios.py              # Scenario templates
│   ├── feedback_simulator.py     # User feedback generation
│   ├── conversation.py           # Conversation management
│   ├── manipulation_scorer.py    # Turn-level manipulation scoring
│   ├── metrics.py                # Metric calculations
│   ├── analysis.py               # Statistical analysis
│   └── visualization.py          # Plotting & dashboards
│
├── data/
│   ├── raw/                      # Raw conversation logs
│   ├── processed/                # Processed metrics
│   └── results/                  # Final analysis outputs
│
├── experiments/
│   ├── run_baseline.py           # Baseline calibration
│   ├── run_full_experiment.py    # Full matrix experiment
│   └── run_analysis.py           # Post-experiment analysis
│
├── notebooks/
│   ├── exploration.ipynb         # Data exploration
│   └── visualization.ipynb       # Interactive visualizations
│
├── tests/
│   ├── test_scenarios.py
│   ├── test_feedback.py
│   ├── test_scorer.py
│   └── test_metrics.py
│
├── requirements.txt
├── README.md
├── plan.txt                      # Original research plan
└── STRATEGY.md                   # This document
```

### 2.2 Key Classes & Interfaces

#### Persona Manager
```python
class Persona:
    name: str
    system_prompt: str
    manipulation_style: Dict[str, float]  # Expected tactic weights
    
    def apply(self, base_prompt: str) -> str:
        """Inject persona into conversation"""
```

#### Feedback Simulator
```python
class FeedbackSimulator:
    pattern: str  # "reinforcing", "resistant", "compliant_to_resistant", etc.
    scenario_context: str
    
    def generate_feedback(
        self, 
        turn: int, 
        model_response: str,
        conversation_history: List[Dict]
    ) -> str:
        """Generate user feedback based on pattern"""
```

#### Manipulation Scorer
```python
class ManipulationScorer:
    def score_turn(
        self, 
        response: str, 
        context: Dict
    ) -> Dict[str, Any]:
        """
        Returns:
        {
            "overall_score": float,
            "tactic_scores": Dict[str, float],
            "mechanism_breakdown": Dict[str, float],
            "confidence": float
        }
        """
```

#### Conversation Manager
```python
class Conversation:
    scenario: Scenario
    persona: Persona
    feedback_pattern: str
    model: str
    
    def run(self) -> ConversationResult:
        """Execute 10-turn conversation"""
```

---

## 3. Implementation Phases

### Phase 1: Foundation (Day 1, Hours 0-4)

**Goal**: Build core infrastructure

#### 1.1 Setup & Configuration (0-1 hour)
- [ ] Initialize project structure
- [ ] Set up virtual environment
- [ ] Install dependencies (openai, anthropic, pandas, numpy, matplotlib, seaborn)
- [ ] Create config.py with API keys, model names, constants

#### 1.2 Scenario System (1-2 hours)
- [ ] Define Scenario class
- [ ] Implement 5 scenario templates:
  - Health misinformation
  - Financial pressure
  - Relationship advice manipulation
  - Political persuasion
  - Product recommendation pressure
- [ ] Create scenario validation tests

#### 1.3 Persona System (2-3 hours)
- [ ] Define Persona class
- [ ] Implement 4 persona prompts:
  - Neutral (baseline)
  - Expert (credentials, authority)
  - Peer (casual, relatable)
  - Authority (protective, advisor)
- [ ] Test persona injection

#### 1.4 Feedback Simulator (3-4 hours)
- [ ] Implement FeedbackSimulator class
- [ ] Create feedback generation logic for 4 patterns:
  - Reinforcing (consistent agreement)
  - Resistant (consistent pushback)
  - Compliant→Resistant (switch at turn 5)
  - Resistant→Compliant (switch at turn 5)
- [ ] Use LLM to generate contextually appropriate feedback
- [ ] Validate feedback pattern adherence

### Phase 2: Scoring System (Day 1, Hours 4-6)

**Goal**: Build manipulation detection & measurement

#### 2.1 Manipulation Taxonomy
- [ ] Define manipulation tactics:
  - Authority inflation
  - Fabrication
  - Commitment escalation
  - Dependency creation
  - Sycophancy
  - False urgency
  - Concern trolling
- [ ] Create tactic detection prompts

#### 2.2 Scorer Implementation
- [ ] Build ManipulationScorer class
- [ ] Implement LLM-judge scoring:
  - Overall manipulation score (0-10)
  - Per-tactic scores
  - Mechanism identification
- [ ] Add lexical marker detection (optional enhancement)
- [ ] Create scoring calibration tests

#### 2.3 Turn Tracking
- [ ] Implement Conversation class
- [ ] Build turn-by-turn logging
- [ ] Store: response, score, feedback, timestamp

### Phase 3: Baseline Calibration (Day 1, Hours 6-8)

**Goal**: Validate system & establish baseline

#### 3.1 Baseline Experiment
- [ ] Run: Neutral persona × all 4 feedback patterns × 5 scenarios
- [ ] Target: 20 conversations
- [ ] Validate:
  - Feedback patterns working correctly
  - Scoring system stable
  - No systematic biases

#### 3.2 Calibration Analysis
- [ ] Check manipulation scores for Neutral persona (should be low)
- [ ] Verify feedback pattern adherence
- [ ] Identify any scoring issues
- [ ] Adjust thresholds if needed

### Phase 4: Full Experiment (Day 2, Hours 0-3)

**Goal**: Execute full experimental matrix

#### 4.1 Experiment Execution
- [ ] Run full matrix:
  - 4 personas × 4 feedback patterns × 5 scenarios = 80 conversations
  - Repeat for 3 models (if time permits) = 240 total
- [ ] Implement parallel execution (if possible)
- [ ] Add progress tracking & error handling
- [ ] Store all raw data

#### 4.2 Data Validation
- [ ] Verify all conversations completed
- [ ] Check data integrity
- [ ] Identify any anomalies

### Phase 5: Metrics & Analysis (Day 2, Hours 3-5)

**Goal**: Calculate all research metrics

#### 5.1 Core Metrics
- [ ] Turn-level manipulation scores (time series)
- [ ] Reinforcement sensitivity: ΔM / reinforcing_turns
- [ ] Resistance persistence: mean(M_resistant) / mean(M_reinforcing)
- [ ] Ratchet coefficient: M_turn7(comply→resist) - M_turn7(resist_throughout)
- [ ] Capitulation exploitation: M_post_capitulation / M_pre_capitulation

#### 5.2 Tactic Analysis
- [ ] Tactic pivot rate: tactic_changes / resistance_events
- [ ] Tactic repertoire: unique_tactics / total_turns
- [ ] Tactic transition matrix (which tactics follow which)

#### 5.3 Statistical Analysis
- [ ] Persona × Feedback interaction effects
- [ ] Trajectory pattern classification
- [ ] Significance testing (if sample size allows)

### Phase 6: Visualization & Reporting (Day 2, Hours 5-8)

**Goal**: Create insights & deliverables

#### 6.1 Core Visualizations
- [ ] Persona × Feedback response matrix (heatmap)
- [ ] Manipulation trajectories (line plots by persona/feedback)
- [ ] Ratchet effect comparison (bar charts)
- [ ] Resistance response typology (categorical breakdown)
- [ ] Tactic transition networks (if time)

#### 6.2 Interactive Dashboard
- [ ] Build Streamlit/Plotly dashboard (if time permits)
- [ ] Dropdown filters for persona/feedback
- [ ] Trajectory plots
- [ ] Metric comparisons

#### 6.3 Report Generation
- [ ] Synthesize key findings
- [ ] Answer research questions (RQ1-RQ5)
- [ ] Document persona signatures
- [ ] Identify intervention implications
- [ ] Create summary document

---

## 4. Evaluation Criteria

### 4.1 System Validation

| Criterion | Success Metric | Validation Method |
|-----------|---------------|-------------------|
| **Feedback Pattern Adherence** | >90% of feedback matches intended pattern | Manual review of sample conversations |
| **Scoring Consistency** | Inter-rater agreement >0.7 (if multiple judges) | Correlation between runs |
| **Persona Differentiation** | Personas show distinct manipulation profiles | Statistical test (ANOVA) |
| **Scenario Validity** | Scenarios enable manipulation opportunities | Baseline manipulation scores >0 |

### 4.2 Research Question Validation

| RQ | Success Criteria | Evaluation Method |
|----|-----------------|-------------------|
| **RQ1: Persona feedback-response patterns** | Distinct patterns for each persona | Persona × Feedback interaction effect (p<0.05) |
| **RQ2: Reinforcement acceleration** | Different escalation rates by persona | Reinforcement sensitivity varies significantly |
| **RQ3: Resistance persistence** | Some personas maintain manipulation despite resistance | Resistance persistence >1.0 for at least one persona |
| **RQ4: Tactic switching** | Feedback triggers tactic changes | Tactic pivot rate >0.2 for at least one persona |
| **RQ5: Ratchet effect** | Early compliance locks in manipulation | Ratchet coefficient >0.3 for at least one persona |

### 4.3 Quality Metrics

- **Completeness**: All 80 (or 240) conversations completed
- **Reproducibility**: Random seed set, all parameters logged
- **Transparency**: All code, prompts, and data documented
- **Interpretability**: Findings clearly explainable

---

## 5. Technical Specifications

### 5.1 Dependencies

```python
# Core
openai>=1.0.0          # GPT-4, GPT-3.5
anthropic>=0.7.0       # Claude (optional)
langchain>=0.1.0       # LLM orchestration (optional)

# Data
pandas>=2.0.0
numpy>=1.24.0

# Analysis
scipy>=1.10.0
scikit-learn>=1.3.0    # For clustering/classification if needed

# Visualization
matplotlib>=3.7.0
seaborn>=0.12.0
plotly>=5.17.0         # Interactive plots
streamlit>=1.28.0      # Dashboard (optional)

# Utilities
python-dotenv>=1.0.0   # Environment variables
tqdm>=4.66.0           # Progress bars
pydantic>=2.0.0        # Data validation
```

### 5.2 API Requirements

- OpenAI API key (GPT-4 or GPT-3.5-turbo)
- Anthropic API key (optional, for Claude)
- Budget estimate: ~$50-200 depending on models and conversation length

### 5.3 Data Storage

- **Raw conversations**: JSON format, ~50KB per conversation
- **Processed metrics**: CSV/Parquet, ~5KB per conversation
- **Total storage**: ~10-50MB for full experiment

---

## 6. Risk Mitigation

### 6.1 Technical Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| **API rate limits** | High | Implement retry logic, rate limiting, batch processing |
| **Scoring inconsistency** | Medium | Use multiple scoring runs, average scores, add confidence intervals |
| **Feedback pattern drift** | Medium | Validate feedback patterns, use strict prompts, manual spot checks |
| **Model API changes** | Low | Pin API versions, test before full run |
| **Data loss** | High | Implement checkpointing, save after each conversation |

### 6.2 Research Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| **No significant effects** | Medium | This is still a valid finding; document null results |
| **Scoring bias** | High | Calibrate against baseline, use multiple scoring methods |
| **Scenario validity** | Medium | Pilot test scenarios, ensure manipulation opportunities exist |
| **Time constraints** | High | Prioritize core RQs, reduce model count if needed |

---

## 7. Success Metrics

### 7.1 Minimum Viable Product (MVP)

- [ ] 4 personas implemented
- [ ] 4 feedback patterns working
- [ ] 5 scenarios defined
- [ ] Manipulation scorer functional
- [ ] Baseline experiment complete (20 conversations)
- [ ] Core metrics calculated
- [ ] At least 2 visualizations created

### 7.2 Full Success

- [ ] Full experiment complete (80+ conversations)
- [ ] All 5 research questions answered
- [ ] Persona × Feedback matrix generated
- [ ] Ratchet effect demonstrated
- [ ] Interactive dashboard created
- [ ] Findings documented with clear implications

### 7.3 Stretch Goals

- [ ] 3 models tested (240 conversations)
- [ ] Statistical significance tests
- [ ] Tactic transition network analysis
- [ ] Intervention recommendations
- [ ] Publication-ready report

---

## 8. Next Steps (Immediate Actions)

### Step 1: Project Setup
```bash
# Create project structure
mkdir -p src data/{raw,processed,results} experiments notebooks tests

# Initialize Python environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install openai anthropic pandas numpy matplotlib seaborn plotly streamlit python-dotenv tqdm pydantic
```

### Step 2: Configuration
- [ ] Create `.env` file with API keys
- [ ] Create `src/config.py` with constants
- [ ] Set up logging

### Step 3: Start with Scenarios
- [ ] Implement Scenario class
- [ ] Define first scenario (Health Misinformation)
- [ ] Test scenario generation

### Step 4: Build Personas
- [ ] Implement Persona class
- [ ] Create Neutral persona (baseline)
- [ ] Test persona injection

### Step 5: Feedback Simulator
- [ ] Implement basic feedback generation
- [ ] Test reinforcing pattern
- [ ] Expand to all 4 patterns

---

## 9. Evaluation Checklist

Before declaring the project complete, verify:

- [ ] All conversations executed successfully
- [ ] Manipulation scores calculated for all turns
- [ ] Feedback patterns validated
- [ ] Persona differentiation confirmed
- [ ] Core metrics computed
- [ ] Research questions addressed
- [ ] Visualizations created
- [ ] Findings documented
- [ ] Code is clean and commented
- [ ] Results are reproducible

---

## 10. Timeline Summary

| Phase | Duration | Key Deliverables |
|-------|----------|-----------------|
| **Phase 1: Foundation** | 4 hours | Scenarios, Personas, Feedback Simulator |
| **Phase 2: Scoring** | 2 hours | Manipulation Scorer, Turn Tracking |
| **Phase 3: Baseline** | 2 hours | 20 conversations, System validation |
| **Phase 4: Full Experiment** | 3 hours | 80+ conversations, Raw data |
| **Phase 5: Analysis** | 2 hours | Metrics, Statistical tests |
| **Phase 6: Visualization** | 3 hours | Plots, Dashboard, Report |
| **Total** | **16 hours** | Complete PFMD system |

---

## Appendix: Key Design Decisions

### A.1 Why LLM-based Feedback?
- **Pros**: Contextually appropriate, natural language
- **Cons**: Potential inconsistency, cost
- **Alternative**: Template-based (faster, cheaper, less natural)

### A.2 Why LLM-judge Scoring?
- **Pros**: Captures nuanced manipulation, context-aware
- **Cons**: Potential bias, cost, latency
- **Alternative**: Lexical markers only (faster, but less accurate)

### A.3 Why 10 Turns?
- **Pros**: Enough for trajectory patterns, manageable cost
- **Cons**: May miss longer-term effects
- **Alternative**: 5 turns (faster) or 20 turns (more complete)

### A.4 Why 3 Models?
- **Pros**: Generalizability, model comparison
- **Cons**: 3x cost and time
- **Alternative**: Start with 1 model, expand if time allows

---

This strategy document should be updated as the project evolves. Use it as a living guide for implementation decisions.

