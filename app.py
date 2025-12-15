"""
CodeMentor - A Pedagogical Coding Assistant

An educational tool that helps users understand AI-generated code by:
1. Assessing their coding level
2. Having them attempt solutions first
3. Providing detailed explanations of improvements
4. Comparing readability vs performance trade-offs
"""

import streamlit as st
import anthropic
import time
import re

# Page configuration
st.set_page_config(
    page_title="CodeMentor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a refined, educational aesthetic
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&family=DM+Sans:wght@400;500;600;700&display=swap');
    
    :root {
        --bg-primary: #0d1117;
        --bg-secondary: #161b22;
        --bg-tertiary: #21262d;
        --text-primary: #e6edf3;
        --text-secondary: #8b949e;
        --accent-green: #3fb950;
        --accent-blue: #58a6ff;
        --accent-purple: #a371f7;
        --accent-orange: #d29922;
        --accent-red: #f85149;
        --border-color: #30363d;
    }
    
    .stApp {
        background: linear-gradient(135deg, var(--bg-primary) 0%, #0a0e14 100%);
    }
    
    /* Main title styling */
    .main-title {
        font-family: 'Source Serif 4', Georgia, serif;
        font-size: 3.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, var(--accent-green) 0%, var(--accent-blue) 50%, var(--accent-purple) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    
    .subtitle {
        font-family: 'DM Sans', sans-serif;
        font-size: 1.15rem;
        color: var(--text-secondary);
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    /* Card styling */
    .mentor-card {
        background: var(--bg-secondary);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
    }
    
    .mentor-card:hover {
        border-color: var(--accent-blue);
        box-shadow: 0 0 20px rgba(88, 166, 255, 0.1);
    }
    
    /* Section headers */
    .section-header {
        font-family: 'DM Sans', sans-serif;
        font-size: 1.3rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Level badges */
    .level-badge {
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-family: 'DM Sans', sans-serif;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .level-beginner {
        background: linear-gradient(135deg, #238636 0%, #2ea043 100%);
        color: white;
    }
    
    .level-intermediate {
        background: linear-gradient(135deg, #1f6feb 0%, #388bfd 100%);
        color: white;
    }
    
    .level-advanced {
        background: linear-gradient(135deg, #8957e5 0%, #a371f7 100%);
        color: white;
    }
    
    /* Explanation boxes */
    .explanation-box {
        background: var(--bg-tertiary);
        border-left: 4px solid var(--accent-blue);
        border-radius: 0 8px 8px 0;
        padding: 1.2rem;
        margin: 1rem 0;
        font-family: 'DM Sans', sans-serif;
    }
    
    .readability-box {
        border-left-color: var(--accent-green);
    }
    
    .performance-box {
        border-left-color: var(--accent-orange);
    }
    
    .tradeoff-box {
        border-left-color: var(--accent-purple);
    }
    
    /* Code comparison styling */
    .code-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        padding: 0.3rem 0.8rem;
        border-radius: 4px;
        margin-bottom: 0.5rem;
        display: inline-block;
    }
    
    .your-code-label {
        background: var(--accent-orange);
        color: var(--bg-primary);
    }
    
    .improved-code-label {
        background: var(--accent-green);
        color: var(--bg-primary);
    }
    
    /* Metric cards */
    .metric-row {
        display: flex;
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .metric-card {
        flex: 1;
        background: var(--bg-tertiary);
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        border: 1px solid var(--border-color);
    }
    
    .metric-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.8rem;
        font-weight: 700;
        color: var(--accent-blue);
    }
    
    .metric-label {
        font-family: 'DM Sans', sans-serif;
        font-size: 0.8rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: var(--bg-secondary);
        border-right: 1px solid var(--border-color);
    }
    
    section[data-testid="stSidebar"] .stMarkdown {
        font-family: 'DM Sans', sans-serif;
    }
    
    /* Input styling */
    .stTextArea textarea {
        font-family: 'JetBrains Mono', monospace !important;
        background: var(--bg-tertiary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
    }
    
    .stTextArea textarea:focus {
        border-color: var(--accent-blue) !important;
        box-shadow: 0 0 0 2px rgba(88, 166, 255, 0.2) !important;
    }
    
    /* Button styling */
    .stButton > button {
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.5rem !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, var(--accent-blue) 0%, var(--accent-purple) 100%) !important;
        border: none !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(88, 166, 255, 0.3);
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 600 !important;
        background: var(--bg-tertiary) !important;
        border-radius: 8px !important;
    }
    
    /* Tips callout */
    .tip-callout {
        background: linear-gradient(135deg, rgba(63, 185, 80, 0.1) 0%, rgba(88, 166, 255, 0.1) 100%);
        border: 1px solid rgba(63, 185, 80, 0.3);
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .tip-callout h4 {
        font-family: 'DM Sans', sans-serif;
        color: var(--accent-green);
        margin: 0 0 0.5rem 0;
        font-size: 0.9rem;
        font-weight: 600;
    }
    
    /* Progress indicator */
    .step-indicator {
        display: flex;
        justify-content: center;
        gap: 2rem;
        margin: 2rem 0;
    }
    
    .step {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.5rem;
    }
    
    .step-number {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        font-size: 1.1rem;
    }
    
    .step-active {
        background: linear-gradient(135deg, var(--accent-blue) 0%, var(--accent-purple) 100%);
        color: white;
    }
    
    .step-complete {
        background: var(--accent-green);
        color: white;
    }
    
    .step-pending {
        background: var(--bg-tertiary);
        color: var(--text-secondary);
        border: 2px solid var(--border-color);
    }
    
    .step-label {
        font-family: 'DM Sans', sans-serif;
        font-size: 0.8rem;
        color: var(--text-secondary);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 500 !important;
        background: var(--bg-tertiary) !important;
        border-radius: 8px 8px 0 0 !important;
        padding: 0.5rem 1.5rem !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--bg-secondary) !important;
        border-bottom: 2px solid var(--accent-blue) !important;
    }
</style>
""", unsafe_allow_html=True)


def get_client():
    """Initialize Anthropic client."""
    return anthropic.Anthropic()


def assess_skill_level(user_code: str, task_description: str) -> dict:
    """Assess the user's coding skill level based on their attempt."""
    client = get_client()
    
    prompt = f"""Analyze this code attempt and assess the programmer's skill level.

Task Description: {task_description}

User's Code Attempt:
```python
{user_code}
```

Provide a JSON response with:
1. "level": one of "beginner", "intermediate", or "advanced"
2. "code_works": boolean - true if the code would work correctly for the task (may have minor issues but fundamentally solves it), false if it has bugs or wouldn't work
3. "code_issues": if code_works is false, list 1-3 specific issues that would prevent it from working
4. "indicators": list of 3-5 specific observations that informed your assessment
5. "strengths": list of 2-3 things they did well (even if basic)
6. "growth_areas": list of 2-3 specific areas for improvement

Consider:
- Code structure and organization
- Use of Python idioms and conventions
- Error handling awareness
- Efficiency considerations
- Naming conventions and readability

Respond ONLY with valid JSON, no markdown formatting."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    try:
        import json
        return json.loads(response.content[0].text)
    except:
        return {
            "level": "intermediate",
            "code_works": False,
            "code_issues": [],
            "indicators": ["Unable to parse assessment"],
            "strengths": ["Attempted the problem"],
            "growth_areas": ["Continue practicing"]
        }


def generate_pedagogical_review(task_description: str, user_code: str, skill_level: str, feedback_mode: str, code_works: bool) -> str:
    """Generate a comprehensive pedagogical code review."""
    client = get_client()
    
    if feedback_mode == "concise":
        prompt = f"""You are CodeMentor, an expert programming educator. A {skill_level}-level programmer has asked you to help them understand code generation.

Their request: "{task_description}"

Their attempt:
```python
{user_code}
```

{"Their code works correctly! Start with congratulations." if code_works else "Their code has issues that need fixing."}

Provide a CONCISE code review with:

1. **{"🎉 CONGRATULATIONS" if code_works else "QUICK ASSESSMENT"}** (1-2 sentences)
   {"Congratulate them - their code works! Note it can still be improved." if code_works else "Briefly note the main issue."}

2. **IMPROVED SOLUTION**
   Provide a clean, improved Python solution with brief inline comments.

3. **LINE-BY-LINE FIXES** (bullet points, max 5)
   For each issue or improvement:
   - `their code` → `improved code`: One sentence explanation
   
   Focus on the most important changes. Be direct and brief.

4. **KEY TAKEAWAY** (1 sentence)
   The single most important lesson from this review.

Keep the entire response under 400 words. Be direct, no fluff."""

    else:  # detailed mode
        prompt = f"""You are CodeMentor, an expert programming educator. A {skill_level}-level programmer has asked you to help them understand code generation.

Their request: "{task_description}"

Their attempt:
```python
{user_code}
```

{"Their code works correctly! Start with congratulations before suggesting improvements." if code_works else "Their code has issues that need fixing."}

Provide a comprehensive, educational response that:

1. **{"🎉 CONGRATULATIONS!" if code_works else "ACKNOWLEDGE THEIR EFFORT"}** (2-3 sentences)
   {"Congratulate them warmly - their code works! Then mention you'll show some refinements." if code_works else "Recognize what they tried to do and point out something specific they did reasonably well."}

2. **IMPROVED SOLUTION**
   - Provide a well-crafted Python solution
   - Include helpful comments explaining key decisions
   - Match complexity to their {skill_level} level

3. **LINE-BY-LINE LEARNING** (for 3-5 key improvements)
   For each improvement, explain:
   - WHAT changed (be specific about the code)
   - WHY it's better (the reasoning)
   - THE TRADEOFF between readability and performance
   
   Use this format for each:
   
   **Improvement: [Name of the improvement]**
   
   *Your code:* `[their specific code snippet]`
   
   *Improved:* `[the improved version]`
   
   *Why this is better:*
   [Explanation tailored to their level]
   
   *Readability vs Performance:*
   - 📖 Readability: [Score 1-5 stars] - [Brief explanation]
   - ⚡ Performance: [Score 1-5 stars] - [Brief explanation]
   - 🎯 Recommendation: [Which to prioritize for this case and why]

4. **PYTHONIC PATTERNS LEARNED**
   List 2-3 Python idioms or patterns demonstrated, with simple explanations

5. **NEXT CHALLENGE**
   Suggest one way they could extend or improve this code to practice further

Tailor your language to a {skill_level} programmer:
- Beginner: Use analogies, avoid jargon, be encouraging
- Intermediate: Balance explanation with efficiency, introduce best practices
- Advanced: Focus on nuances, edge cases, and optimization strategies

Be warm, encouraging, and genuinely helpful. Use emojis sparingly for visual breaks."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.content[0].text


def generate_starter_code(task_description: str) -> str:
    """Generate a basic starter template based on the task."""
    client = get_client()
    
    prompt = f"""Given this coding task: "{task_description}"

Generate a minimal Python code SKELETON that:
1. Has the basic structure (function definition, main variables)
2. Includes TODO comments showing what needs to be implemented
3. Is intentionally incomplete - the user needs to fill in the logic
4. Uses descriptive placeholder variable names

The goal is to give them a starting point without solving it for them.

Return ONLY the code, no explanations. Keep it under 15 lines."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.content[0].text


# Initialize session state
if "step" not in st.session_state:
    st.session_state.step = 1
if "task_description" not in st.session_state:
    st.session_state.task_description = ""
if "user_code" not in st.session_state:
    st.session_state.user_code = ""
if "skill_assessment" not in st.session_state:
    st.session_state.skill_assessment = None
if "review" not in st.session_state:
    st.session_state.review = None
if "feedback_mode" not in st.session_state:
    st.session_state.feedback_mode = "detailed"
if "task_mode" not in st.session_state:
    st.session_state.task_mode = "generate"  # "generate" or "review"


# Sidebar
with st.sidebar:
    st.markdown("### 🎓 CodeMentor")
    st.markdown("---")
    
    st.markdown("""
    **How it works:**
    
    1️⃣ **Describe** what you want to code
    
    2️⃣ **Attempt** your own solution first
    
    3️⃣ **Learn** from detailed feedback
    
    ---
    
    **Why attempt first?**
    
    Research shows that *productive struggle* before receiving help leads to deeper understanding and better retention.
    
    Even an imperfect attempt activates your brain's problem-solving circuits!
    
    ---
    """)
    
    st.markdown("#### Learning Philosophy")
    st.info("""
    🎯 **We focus on:**
    - Understanding *why* code works
    - Readability vs Performance tradeoffs
    - Pythonic patterns & idioms
    - Building intuition, not just copying
    """)
    
    if st.button("🔄 Start New Task", use_container_width=True):
        st.session_state.step = 1
        st.session_state.task_description = ""
        st.session_state.user_code = ""
        st.session_state.skill_assessment = None
        st.session_state.review = None
        st.session_state.feedback_mode = "detailed"
        st.session_state.task_mode = "generate"
        st.rerun()


# Main content
st.markdown('<h1 class="main-title">CodeMentor</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Learn to code by doing, then understanding. AI-powered education that makes you a better programmer.</p>', unsafe_allow_html=True)

# Progress indicator
if st.session_state.task_mode == "review":
    # Two-step flow for review mode
    step_states_review = ["complete" if st.session_state.step > 1 else "active" if st.session_state.step == 1 else "pending",
                          "active" if st.session_state.step == 3 else "pending"]
    st.markdown(f"""
    <div class="step-indicator">
        <div class="step">
            <div class="step-number step-{step_states_review[0]}">1</div>
            <span class="step-label">Paste Code</span>
        </div>
        <div class="step">
            <div class="step-number step-{step_states_review[1]}">2</div>
            <span class="step-label">Learn & Improve</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    # Three-step flow for generate mode
    step_states = ["complete" if st.session_state.step > i else "active" if st.session_state.step == i else "pending" for i in range(1, 4)]
    st.markdown(f"""
    <div class="step-indicator">
        <div class="step">
            <div class="step-number step-{step_states[0]}">1</div>
            <span class="step-label">Describe Task</span>
        </div>
        <div class="step">
            <div class="step-number step-{step_states[1]}">2</div>
            <span class="step-label">Your Attempt</span>
        </div>
        <div class="step">
            <div class="step-number step-{step_states[2]}">3</div>
            <span class="step-label">Learn & Improve</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Step 1: Task Description
if st.session_state.step == 1:
    st.markdown('<div class="section-header">📝 Step 1: What would you like to do?</div>', unsafe_allow_html=True)
    
    # Task mode selection
    st.markdown("**Choose your mode:**")
    
    col_gen, col_rev = st.columns(2)
    
    with col_gen:
        gen_selected = st.session_state.task_mode == "generate"
        if st.button(
            "🆕 Generate New Code" + (" ✓" if gen_selected else ""),
            use_container_width=True,
            type="primary" if gen_selected else "secondary"
        ):
            st.session_state.task_mode = "generate"
            st.rerun()
        st.caption("Describe a task, attempt it yourself, then learn from feedback")
    
    with col_rev:
        rev_selected = st.session_state.task_mode == "review"
        if st.button(
            "🔍 Review Existing Code" + (" ✓" if rev_selected else ""),
            use_container_width=True,
            type="primary" if rev_selected else "secondary"
        ):
            st.session_state.task_mode = "review"
            st.rerun()
        st.caption("Paste code you've already written for a pedagogical review")
    
    st.markdown("---")
    
    if st.session_state.task_mode == "generate":
        # Original generate flow
        st.markdown("""
        <div class="tip-callout">
            <h4>💡 Tip: Be specific!</h4>
            Instead of "sort a list", try "Generate code that sorts a list of dictionaries by a specific key in descending order"
        </div>
        """, unsafe_allow_html=True)
        
        task_input = st.text_area(
            "Describe your coding task",
            placeholder="Generate code that...\n\nExample: Generate code that finds all prime numbers up to N using an efficient algorithm",
            height=120,
            label_visibility="collapsed"
        )
        
    else:
        # Review existing code flow
        st.markdown("""
        <div class="tip-callout">
            <h4>🔍 Code Review Mode</h4>
            Paste your existing code below. Optionally describe what it's supposed to do for more targeted feedback.
        </div>
        """, unsafe_allow_html=True)
        
        task_input = st.text_area(
            "What does this code do? (optional but recommended)",
            placeholder="This code is supposed to...\n\nExample: This code reads a CSV file and calculates the average of a column",
            height=80,
            label_visibility="collapsed"
        )
        
        st.markdown("**Paste your code:**")
        existing_code = st.text_area(
            "Your existing code",
            placeholder="# Paste your Python code here\n\ndef my_function():\n    ...",
            height=200,
            label_visibility="collapsed"
        )
    
    st.markdown("---")
    st.markdown("**Choose your feedback style:**")
    
    col_mode1, col_mode2 = st.columns(2)
    
    with col_mode1:
        detailed_selected = st.session_state.feedback_mode == "detailed"
        if st.button(
            "📚 Detailed Feedback" + (" ✓" if detailed_selected else ""),
            use_container_width=True,
            type="primary" if detailed_selected else "secondary"
        ):
            st.session_state.feedback_mode = "detailed"
            st.rerun()
        st.caption("In-depth explanations with readability vs performance analysis")
    
    with col_mode2:
        concise_selected = st.session_state.feedback_mode == "concise"
        if st.button(
            "⚡ Concise Feedback" + (" ✓" if concise_selected else ""),
            use_container_width=True,
            type="primary" if concise_selected else "secondary"
        ):
            st.session_state.feedback_mode = "concise"
            st.rerun()
        st.caption("Quick line-by-line fixes, straight to the point")
    
    st.markdown("---")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.session_state.task_mode == "generate":
            if st.button("Continue →", type="primary", use_container_width=True):
                if task_input.strip():
                    st.session_state.task_description = task_input.strip()
                    st.session_state.step = 2
                    st.rerun()
                else:
                    st.error("Please describe what you want to code")
        else:
            # Review mode - skip step 2 and go directly to feedback
            if st.button("Get Review →", type="primary", use_container_width=True):
                if existing_code.strip():
                    st.session_state.task_description = task_input.strip() if task_input.strip() else "Review and improve this code"
                    st.session_state.user_code = existing_code.strip()
                    st.session_state.step = 3  # Skip to review
                    st.rerun()
                else:
                    st.error("Please paste your code to review")
    
    with col2:
        with st.expander("📚 Example tasks to try"):
            st.markdown("""
            - Generate code that **reverses words in a sentence** while preserving punctuation
            - Generate code that **validates email addresses** using regex
            - Generate code that **finds the longest palindromic substring** in a string
            - Generate code that **merges two sorted lists** efficiently
            - Generate code that **implements a simple LRU cache** using a dictionary
            - Generate code that **flattens a nested list** of arbitrary depth
            """)

# Step 2: User's Attempt
elif st.session_state.step == 2:
    st.markdown('<div class="section-header">💻 Step 2: Give it a try!</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="mentor-card">
        <strong>Your task:</strong> {st.session_state.task_description}
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="tip-callout">
        <h4>🧠 Why attempt first?</h4>
        Writing your own solution—even if imperfect—helps you:
        <ul>
            <li>Identify what you already know</li>
            <li>Recognize gaps in your understanding</li>
            <li>Better appreciate the improvements later</li>
        </ul>
        <em>There's no wrong answer here. Any attempt helps you learn!</em>
    </div>
    """, unsafe_allow_html=True)
    
    # Option to get a starter template
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("🎯 Get Starter Template", use_container_width=True):
            with st.spinner("Generating starter code..."):
                starter = generate_starter_code(st.session_state.task_description)
                st.session_state.user_code = starter
                st.rerun()
    
    with col2:
        st.caption("Stuck? Get a basic structure to fill in (won't give away the solution)")
    
    user_code = st.text_area(
        "Your code attempt",
        value=st.session_state.user_code,
        placeholder="# Write your Python code here\n# Don't worry about making it perfect!\n\ndef your_function():\n    pass",
        height=300,
        label_visibility="collapsed"
    )
    
    col1, col2, col3 = st.columns([1, 1, 3])
    
    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state.step = 1
            st.rerun()
    
    with col2:
        if st.button("Get Feedback →", type="primary", use_container_width=True):
            if user_code.strip() and user_code.strip() != "# Write your Python code here\n# Don't worry about making it perfect!\n\ndef your_function():\n    pass":
                st.session_state.user_code = user_code.strip()
                st.session_state.step = 3
                st.rerun()
            else:
                st.error("Please write some code first—even a partial attempt helps!")

# Step 3: Pedagogical Review
elif st.session_state.step == 3:
    st.markdown('<div class="section-header">🎓 Step 3: Let\'s learn together!</div>', unsafe_allow_html=True)
    
    # Assess skill level if not done
    if st.session_state.skill_assessment is None:
        with st.spinner("🔍 Analyzing your coding style..."):
            st.session_state.skill_assessment = assess_skill_level(
                st.session_state.user_code,
                st.session_state.task_description
            )
    
    # Display skill assessment
    level = st.session_state.skill_assessment.get("level", "intermediate")
    code_works = st.session_state.skill_assessment.get("code_works", False)
    code_issues = st.session_state.skill_assessment.get("code_issues", [])
    
    level_colors = {
        "beginner": "level-beginner",
        "intermediate": "level-intermediate", 
        "advanced": "level-advanced"
    }
    
    # Congratulations banner if code works
    if code_works:
        st.success("🎉 **Congratulations!** Your code works! It solves the task correctly. Below are some refinements to make it even better.")
    
    # Task and profile row
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown(f"""
        <div class="mentor-card">
            <div class="section-header">📊 Your Profile</div>
            <p style="margin-bottom: 1rem;">
                <span class="level-badge {level_colors.get(level, 'level-intermediate')}">{level}</span>
            </p>
            <p style="color: #8b949e; font-size: 0.9rem;">
                {st.session_state.feedback_mode.title()} feedback mode
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="mentor-card">
            <div class="section-header">📝 Your Task</div>
            <p>{st.session_state.task_description}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Always show: Strengths, Growth Areas, and Code (not in expanders)
    st.markdown("---")
    
    col_str, col_grow = st.columns(2)
    
    with col_str:
        st.markdown("#### 💪 Your Strengths")
        for strength in st.session_state.skill_assessment.get("strengths", []):
            st.markdown(f"✅ {strength}")
    
    with col_grow:
        st.markdown("#### 🌱 Growth Areas")
        for area in st.session_state.skill_assessment.get("growth_areas", []):
            st.markdown(f"🎯 {area}")
    
    # Show code issues if code doesn't work
    if not code_works and code_issues:
        st.markdown("#### ⚠️ Issues to Fix")
        for issue in code_issues:
            st.markdown(f"❌ {issue}")
    
    st.markdown("---")
    
    # Always show user's code
    st.markdown("#### 👀 Your Code")
    st.code(st.session_state.user_code, language="python")
    
    st.markdown("---")
    
    # Generate review if not done
    if st.session_state.review is None:
        with st.spinner("🎓 Preparing your personalized learning experience..."):
            st.session_state.review = generate_pedagogical_review(
                st.session_state.task_description,
                st.session_state.user_code,
                level,
                st.session_state.feedback_mode,
                code_works
            )
    
    # Display the pedagogical review (only once, as markdown)
    st.markdown('<div class="section-header">📚 Your Personalized Code Review</div>', unsafe_allow_html=True)
    st.markdown(st.session_state.review)
    
    st.markdown("---")
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Try Another Task", use_container_width=True):
            st.session_state.step = 1
            st.session_state.task_description = ""
            st.session_state.user_code = ""
            st.session_state.skill_assessment = None
            st.session_state.review = None
            st.rerun()
    
    with col2:
        if st.session_state.task_mode == "generate":
            if st.button("✏️ Revise My Code", use_container_width=True):
                st.session_state.step = 2
                st.session_state.skill_assessment = None
                st.session_state.review = None
                st.rerun()
        else:
            if st.button("✏️ Edit & Re-review", use_container_width=True):
                st.session_state.step = 1
                st.session_state.skill_assessment = None
                st.session_state.review = None
                st.rerun()
    
    with col3:
        if st.button("🔀 Switch to " + ("Concise" if st.session_state.feedback_mode == "detailed" else "Detailed"), use_container_width=True):
            st.session_state.feedback_mode = "concise" if st.session_state.feedback_mode == "detailed" else "detailed"
            st.session_state.review = None
            st.rerun()


# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: var(--text-secondary); font-size: 0.85rem; padding: 1rem;">
    <p>🎓 <strong>CodeMentor</strong> — Learn by doing, understand by reflecting</p>
    <p style="font-size: 0.75rem; margin-top: 0.5rem;">
        Powered by Claude • Built for learners who want to truly understand their code
    </p>
</div>
""", unsafe_allow_html=True)
