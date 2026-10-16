import streamlit as st
from datetime import date, timedelta
from collections import Counter

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="STRATIVA | Midlevel Manager Agent",
    page_icon="🔀",
    layout="wide"
)

TEAMS = [
    "Operations Team",
    "Human Resources",
    "Finance Team",
    "Customer Support",
    "IT Team",
    "Management"
]

STATUSES = [
    "Not Started",
    "In Progress",
    "Completed",
    "Blocked"
]

PRIORITIES = ["High", "Medium", "Low"]


# ============================================================
# SESSION DATA
# ============================================================

if "tasks" not in st.session_state:
    st.session_state.tasks = []

if "next_task_id" not in st.session_state:
    st.session_state.next_task_id = 1

if "proposal" not in st.session_state:
    st.session_state.proposal = []

if "proposal_goal" not in st.session_state:
    st.session_state.proposal_goal = ""

if "analysis_category" not in st.session_state:
    st.session_state.analysis_category = ""

if "analysis_kpis" not in st.session_state:
    st.session_state.analysis_kpis = []

if "proposal_version" not in st.session_state:
    st.session_state.proposal_version = 0


# ============================================================
# MANAGEMENT ANALYSIS RULES
# ============================================================

def build_plan(goal):

    lower = goal.lower()

    if "efficien" in lower or "productiv" in lower:

        category = "Operational Efficiency"

        steps = [
            (
                "Review workflows and identify bottlenecks",
                "Operations Team", "High", 3
            ),
            (
                "Evaluate team workloads and resource capacity",
                "Human Resources", "High", 5
            ),
            (
                "Assess opportunities for process automation",
                "IT Team", "Medium", 7
            ),
            (
                "Measure improvements and report outcomes",
                "Management", "Medium", 14
            )
        ]

        kpis = [
            "Process completion time",
            "Tasks completed",
            "Cost per task",
            "Productivity improvement"
        ]

    elif "customer" in lower or "service" in lower:

        category = "Customer Experience"

        steps = [
            (
                "Review customer feedback and service issues",
                "Customer Support", "High", 3
            ),
            (
                "Identify recurring complaints and bottlenecks",
                "Operations Team", "High", 5
            ),
            (
                "Recommend service process improvements",
                "Customer Support", "Medium", 7
            ),
            (
                "Review satisfaction and resolution metrics",
                "Management", "Medium", 14
            )
        ]

        kpis = [
            "Customer satisfaction",
            "Resolution time",
            "First-contact resolution",
            "Complaint volume"
        ]

    elif "cost" in lower or "budget" in lower:

        category = "Cost Management"

        steps = [
            (
                "Review expenses and budget variance",
                "Finance Team", "High", 3
            ),
            (
                "Identify avoidable operational costs",
                "Operations Team", "High", 5
            ),
            (
                "Evaluate resource allocation options",
                "Management", "Medium", 7
            ),
            (
                "Monitor savings and budget adherence",
                "Finance Team", "Medium", 14
            )
        ]

        kpis = [
            "Budget variance",
            "Cost savings",
            "Resource utilization",
            "Cost per task"
        ]

    else:

        category = "General Business Operations"

        steps = [
            (
                "Clarify success criteria and stakeholders",
                "Management", "High", 3
            ),
            (
                "Assess resources and operational constraints",
                "Operations Team", "High", 5
            ),
            (
                "Develop a practical implementation plan",
                "Management", "Medium", 7
            ),
            (
                "Review progress and report results",
                "Management", "Medium", 14
            )
        ]

        kpis = [
            "Task completion",
            "Milestone achievement",
            "Resource utilization",
            "Goal progress"
        ]

    proposals = [
        {
            "name": name,
            "team": team,
            "priority": priority,
            "due_date": date.today() + timedelta(days=days)
        }
        for name, team, priority, days in steps
    ]

    return category, proposals, kpis


# ============================================================
# TASK MANAGEMENT FUNCTIONS
# ============================================================

def add_task(name, team, priority, due):

    task = {
        "id": st.session_state.next_task_id,
        "name": name.strip(),
        "team": team,
        "priority": priority,
        "due_date": due.isoformat(),
        "status": "Not Started"
    }

    st.session_state.tasks.append(task)
    st.session_state.next_task_id += 1


def update_task_status(task_id):

    new_status = st.session_state[
        f"task_status_{task_id}"
    ]

    for task in st.session_state.tasks:

        if task["id"] == task_id:
            task["status"] = new_status
            break


# ============================================================
# LIVE PERFORMANCE CALCULATIONS
# ============================================================

def calculate_performance():

    tasks = st.session_state.tasks

    total = len(tasks)

    completed = sum(
        task["status"] == "Completed"
        for task in tasks
    )

    in_progress = sum(
        task["status"] == "In Progress"
        for task in tasks
    )

    not_started = sum(
        task["status"] == "Not Started"
        for task in tasks
    )

    blocked = sum(
        task["status"] == "Blocked"
        for task in tasks
    )

    overdue = sum(
        task["status"] != "Completed"
        and date.fromisoformat(
            task["due_date"]
        ) < date.today()
        for task in tasks
    )

    high_priority_pending = sum(
        task["priority"] == "High"
        and task["status"] != "Completed"
        for task in tasks
    )

    completion_rate = (
        completed / total
        if total > 0
        else 0
    )

    return {
        "total": total,
        "completed": completed,
        "in_progress": in_progress,
        "not_started": not_started,
        "blocked": blocked,
        "overdue": overdue,
        "high_priority_pending": high_priority_pending,
        "completion_rate": completion_rate
    }


# ============================================================
# RISK DETECTION
# ============================================================

def detect_risks():

    tasks = st.session_state.tasks

    risks = []

    if not tasks:
        return risks

    overdue_tasks = [
        task for task in tasks
        if task["status"] != "Completed"
        and date.fromisoformat(
            task["due_date"]
        ) < date.today()
    ]

    if overdue_tasks:

        risks.append({
            "level": "High",
            "message": (
                f"{len(overdue_tasks)} task(s) are overdue. "
                "Management should review deadlines "
                "and possible delays."
            )
        })

    blocked_tasks = [
        task for task in tasks
        if task["status"] == "Blocked"
    ]

    if blocked_tasks:

        risks.append({
            "level": "High",
            "message": (
                f"{len(blocked_tasks)} task(s) are blocked. "
                "Management intervention may be required."
            )
        })

    pending_high_priority = [
        task for task in tasks
        if task["priority"] == "High"
        and task["status"] == "Not Started"
    ]

    if pending_high_priority:

        risks.append({
            "level": "Medium",
            "message": (
                f"{len(pending_high_priority)} "
                "high-priority task(s) have not started."
            )
        })

    # Identify potential workload concentration.
    # This is a simple rule-based indicator,
    # not a verified staffing-capacity assessment.

    team_workload = Counter(
        task["team"]
        for task in tasks
        if task["status"] != "Completed"
    )

    for team, count in team_workload.items():

        if count >= 3:

            risks.append({
                "level": "Medium",
                "message": (
                    f"{team} has {count} unfinished tasks. "
                    "Review team capacity and competing "
                    "priorities."
                )
            })

    return risks


# ============================================================
# APPLICATION HEADER
# ============================================================

st.title(":material/account_tree: STRATIVA")

st.caption("Where Strategy Becomes Action.")

st.write(
    "**Midlevel Manager Agent | "
    "Strategy • Coordination • Execution**"
)

st.write(
    "Translate executive goals into operational plans, "
    "approve task assignments, monitor performance, "
    "and identify management risks."
)

st.divider()


# ============================================================
# NAVIGATION
# ============================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "Management Assistant",
    "Task Management",
    "Agent Coordination",
    "Performance Dashboard"
])


# ============================================================
# TAB 1: MANAGEMENT ASSISTANT
# ============================================================

with tab1:

    st.subheader("Executive Goal Analysis")

    goal = st.text_area(
        "Enter an executive goal or management request",
        placeholder=(
            "Improve operational efficiency by 15% "
            "while maintaining the current budget."
        )
    )

    if st.button("Analyze Goal", type="primary"):

        if not goal.strip():

            st.warning(
                "Please enter a management goal."
            )

        else:

            category, proposals, kpis = build_plan(goal)

            st.session_state.proposal = proposals
            st.session_state.proposal_goal = goal.strip()
            st.session_state.analysis_category = category
            st.session_state.analysis_kpis = kpis

            st.session_state.proposal_version += 1

    # --------------------------------------------------------
    # SECTION 1: GOAL ASSESSMENT
    # --------------------------------------------------------

    if st.session_state.proposal_goal:

        st.markdown("### 1. Goal Assessment")

        st.write(
            f"**Executive Goal:** "
            f"{st.session_state.proposal_goal}"
        )

        st.write(
            f"**Management Focus:** "
            f"{st.session_state.analysis_category}"
        )

    # --------------------------------------------------------
    # SECTION 2: MANAGEMENT APPROVAL
    # --------------------------------------------------------

    if st.session_state.proposal:

        st.success(
            "Proposed action plan ready for management "
            "review. No tasks have been assigned yet."
        )

        st.markdown("### 2. Review Proposed Tasks")

        st.caption(
            "Suggested assignments and deadlines are "
            "editable. Approve only the tasks you want "
            "to create."
        )

        version = st.session_state.proposal_version

        with st.form(f"approval_form_{version}"):

            reviewed = []

            for i, item in enumerate(
                st.session_state.proposal
            ):

                st.markdown(
                    f"**Proposed Task {i + 1}**"
                )

                include = st.checkbox(
                    "Include this task",
                    value=True,
                    key=f"include_{version}_{i}"
                )

                name = st.text_input(
                    "Task description",
                    value=item["name"],
                    key=f"name_{version}_{i}"
                )

                team = st.selectbox(
                    "Suggested team",
                    TEAMS,
                    index=TEAMS.index(item["team"]),
                    key=f"team_{version}_{i}"
                )

                priority = st.selectbox(
                    "Priority",
                    PRIORITIES,
                    index=PRIORITIES.index(
                        item["priority"]
                    ),
                    key=f"priority_{version}_{i}"
                )

                due = st.date_input(
                    "Suggested due date",
                    value=item["due_date"],
                    key=f"due_{version}_{i}"
                )

                reviewed.append(
                    (include, name, team, priority, due)
                )

                st.divider()

            approved = st.form_submit_button(
                "Approve Selected Tasks",
                type="primary"
            )

        if approved:

            chosen = [
                item for item in reviewed
                if item[0] and item[1].strip()
            ]

            if not chosen:

                st.warning(
                    "Select at least one task "
                    "with a description."
                )

            else:

                for _, name, team, priority, due in chosen:

                    add_task(
                        name,
                        team,
                        priority,
                        due
                    )

                st.session_state.proposal = []

                st.success(
                    f"Approved and added {len(chosen)} "
                    "task(s) to Task Management."
                )

                st.info(
                    "Open the Task Management tab "
                    "to view your approved tasks."
                )

    # --------------------------------------------------------
    # SECTION 3: LIVE PERFORMANCE METRICS
    # --------------------------------------------------------

    st.markdown(
        "### 3. Performance Metrics & Progress"
    )

    performance = calculate_performance()

    if performance["total"] == 0:

        st.info(
            "No approved or manually created tasks yet. "
            "Performance metrics will appear once "
            "tasks are added."
        )

    else:

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Total Tasks",
            performance["total"]
        )

        col2.metric(
            "In Progress",
            performance["in_progress"]
        )

        col3.metric(
            "Completed",
            performance["completed"]
        )

        col4.metric(
            "Completion Rate",
            f"{performance['completion_rate'] * 100:.1f}%"
        )

        st.progress(
            performance["completion_rate"],
            text=(
                f"{performance['completion_rate'] * 100:.1f}% "
                "of tasks completed"
            )
        )

        st.caption(
            "Metrics update from task records in "
            "the current Streamlit session."
        )

    if st.session_state.analysis_kpis:

        st.markdown("#### Recommended Business KPIs")

        for kpi in st.session_state.analysis_kpis:
            st.write(f"• {kpi}")

        st.caption(
            "Business KPIs above are recommendations. "
            "Actual cost, productivity, and customer "
            "outcomes require additional data sources."
        )

    # --------------------------------------------------------
    # SECTION 4: DYNAMIC RISKS
    # --------------------------------------------------------

    st.markdown(
        "### 4. Risks and Human Oversight"
    )

    risks = detect_risks()

    if performance["total"] == 0:

        st.info(
            "Risk monitoring will begin once "
            "tasks are created."
        )

    elif not risks:

        st.success(
            "No risks detected under the current "
            "monitoring rules."
        )

    else:

        for risk in risks:

            if risk["level"] == "High":

                st.error(
                    f"High Risk: {risk['message']}"
                )

            else:

                st.warning(
                    f"Attention Required: {risk['message']}"
                )

    st.caption(
        "Risk alerts are rule-based indicators. "
        "Managers should verify the circumstances "
        "before taking action."
    )

    st.caption(
        "Prototype: rule-based recommendations, "
        "not AI-model-generated analysis."
    )


# ============================================================
# TAB 2: TASK MANAGEMENT
# ============================================================

with tab2:

    st.subheader("Task Allocation & Tracking")

    st.write(
        "Create tasks manually or review tasks "
        "approved in the Management Assistant."
    )

    # --------------------------------------------------------
    # CREATE TASK
    # --------------------------------------------------------

    with st.form(
        "manual_task_form",
        clear_on_submit=True
    ):

        name = st.text_input("Task Name")

        team = st.selectbox(
            "Assign To",
            TEAMS
        )

        priority = st.selectbox(
            "Priority",
            PRIORITIES
        )

        due = st.date_input(
            "Due Date",
            value=date.today() + timedelta(days=1)
        )

        create = st.form_submit_button(
            "Create Task",
            type="primary"
        )

    if create:

        if not name.strip():

            st.warning(
                "Please enter a task name."
            )

        else:

            add_task(
                name,
                team,
                priority,
                due
            )

            st.success(
                "Task created successfully."
            )

    st.divider()

    # --------------------------------------------------------
    # TASK TRACKER
    # --------------------------------------------------------

    st.markdown("### Task Tracker")

    if not st.session_state.tasks:

        st.info(
            "No tasks yet. Create one above "
            "or approve a proposed plan."
        )

    for task in st.session_state.tasks:

        with st.expander(
            f"Task #{task['id']} — {task['name']}"
        ):

            st.write(
                f"**Assigned Team:** {task['team']}"
            )

            st.write(
                f"**Priority:** {task['priority']}"
            )

            st.write(
                f"**Due Date:** {task['due_date']}"
            )

            st.selectbox(
                "Task Status",
                STATUSES,
                index=STATUSES.index(task["status"]),
                key=f"task_status_{task['id']}",
                on_change=update_task_status,
                args=(task["id"],)
            )

            if task["status"] == "Blocked":

                st.warning(
                    "Management attention required: "
                    "this task is blocked."
                )

            if (
                task["status"] != "Completed"
                and date.fromisoformat(
                    task["due_date"]
                ) < date.today()
            ):

                st.error(
                    "This task is overdue."
                )

    st.caption(
        "Tasks are stored only in the current "
        "Streamlit session. They are not permanently "
        "saved or shared between users."
    )


# ============================================================
# TAB 3: AGENT COORDINATION
# ============================================================

with tab3:

    st.subheader("External Agent Coordination")

    st.write(
        "STRATIVA is designed to coordinate "
        "specialized agents and support "
        "management decisions."
    )

    st.info(
        "No external agents are connected yet. "
        "Automatic agent-reported task status "
        "changes are not implemented."
    )

    st.markdown("### Planned Agent Communication")

    st.write(
        "1. Receive an executive management goal."
    )

    st.write(
        "2. Generate a proposed operational plan."
    )

    st.write(
        "3. Obtain human management approval."
    )

    st.write(
        "4. Send approved work to connected agents."
    )

    st.write(
        "5. Receive progress and completion updates."
    )

    st.write(
        "6. Monitor performance and escalate risks."
    )

    st.caption(
        "External agent communication will be "
        "implemented in a later development stage."
    )


# ============================================================
# TAB 4: PERFORMANCE DASHBOARD
# ============================================================

with tab4:

    st.subheader(
        "Management Performance Dashboard"
    )

    performance = calculate_performance()

    total = performance["total"]
    completed = performance["completed"]
    in_progress = performance["in_progress"]
    blocked = performance["blocked"]
    overdue = performance["overdue"]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Tasks",
        total
    )

        col2.metric(
        "In Progress",
        in_progress
    )

    col3.metric(
        "Completed",
        completed
    )

    col4.metric(
        "Blocked",
        blocked
    )

    st.metric(
        "Overdue Tasks",
        overdue
    )
