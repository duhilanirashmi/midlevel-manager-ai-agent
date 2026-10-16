
import streamlit as st
from datetime import date, timedelta

# PAGE CONFIGURATION

st.set_page_config(
    page_title="Strativa | Midlevel Manager Agent",
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

# SESSION DATA

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


# MANAGEMENT ANALYSIS RULES

def build_plan(goal):
    lower = goal.lower()

    if "efficien" in lower or "productiv" in lower:
        category = "Operational Efficiency"
        steps = [
            ("Review workflows and identify bottlenecks",
             "Operations Team", "High", 3),
            ("Evaluate team workloads and resource capacity",
             "Human Resources", "High", 5),
            ("Assess opportunities for process automation",
             "IT Team", "Medium", 7),
            ("Measure improvements and report outcomes",
             "Management", "Medium", 14),
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
            ("Review customer feedback and service issues",
             "Customer Support", "High", 3),
            ("Identify recurring complaints and bottlenecks",
             "Operations Team", "High", 5),
            ("Recommend service process improvements",
             "Customer Support", "Medium", 7),
            ("Review satisfaction and resolution metrics",
             "Management", "Medium", 14),
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
            ("Review expenses and budget variance",
             "Finance Team", "High", 3),
            ("Identify avoidable operational costs",
             "Operations Team", "High", 5),
            ("Evaluate resource allocation options",
             "Management", "Medium", 7),
            ("Monitor savings and budget adherence",
             "Finance Team", "Medium", 14),
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
            ("Clarify success criteria and stakeholders",
             "Management", "High", 3),
            ("Assess resources and operational constraints",
             "Operations Team", "High", 5),
            ("Develop a practical implementation plan",
             "Management", "Medium", 7),
            ("Review progress and report results",
             "Management", "Medium", 14),
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


# STATUS UPDATE CALLBACK

def update_task_status(task_id):
    new_status = st.session_state[
        f"task_status_{task_id}"
    ]

    for task in st.session_state.tasks:
        if task["id"] == task_id:
            task["status"] = new_status
            break


# APPLICATION HEADER

st.title(":material/account_tree: STRATIVA")
st.caption("Where Strategy Becomes Action.")

st.write(
    "**Midlevel Manager Agent | "
    "Strategy • Coordination • Execution**"
)

st.write(
    "Translate executive goals into operational plans, "
    "approve task assignments, and monitor progress."
)

st.divider()


# NAVIGATION

tab1, tab2, tab3, tab4 = st.tabs([
    "Management Assistant",
    "Task Management",
    "Agent Coordination",
    "Performance Dashboard"
])


# TAB 1: MANAGEMENT ASSISTANT

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
            st.warning("Please enter a management goal.")

        else:
            category, proposals, kpis = build_plan(goal)

            st.session_state.proposal = proposals
            st.session_state.proposal_goal = goal.strip()
            st.session_state.analysis_category = category
            st.session_state.analysis_kpis = kpis

            st.session_state.proposal_version = (
                st.session_state.get("proposal_version", 0) + 1
            )

    if st.session_state.proposal:

        st.success(
            "Proposed action plan ready for management review. "
            "No tasks have been assigned yet."
        )

        st.markdown("### 1. Goal Assessment")

        st.write(
            f"**Executive Goal:** "
            f"{st.session_state.proposal_goal}"
        )

        st.write(
            f"**Management Focus:** "
            f"{st.session_state.analysis_category}"
        )

        st.markdown("### 2. Review Proposed Tasks")

        st.caption(
            "Suggested assignments and deadlines are editable. "
            "Approve only the tasks you want to create."
        )

        version = st.session_state.get(
            "proposal_version", 0
        )

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
                    ["High", "Medium", "Low"],
                    index=[
                        "High", "Medium", "Low"
                    ].index(item["priority"]),
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

                    st.session_state.tasks.append({
                        "id": st.session_state.next_task_id,
                        "name": name.strip(),
                        "team": team,
                        "priority": priority,
                        "due_date": due.isoformat(),
                        "status": "Not Started"
                    })

                    st.session_state.next_task_id += 1

                st.session_state.proposal = []

                st.success(
                    f"Approved and added {len(chosen)} "
                    "task(s) to Task Management."
                )

                st.info(
                    "Open the Task Management tab "
                    "to view your approved tasks."
                )

        st.markdown(
            "### 3. Suggested Performance Metrics"
        )

        for kpi in st.session_state.analysis_kpis:
            st.write(f"• {kpi}")

        st.markdown(
            "### 4. Risks and Human Oversight"
        )

        st.warning(
            "Watch for resource constraints, competing "
            "priorities, delays, and insufficient data."
        )

        st.caption(
            "Prototype: rule-based recommendations, "
            "not AI-model-generated analysis."
        )


# TAB 2: TASK MANAGEMENT

with tab2:

    st.subheader("Task Allocation & Tracking")

    st.write(
        "Create tasks manually or review tasks approved "
        "in the Management Assistant."
    )

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
            ["High", "Medium", "Low"]
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
            st.warning("Please enter a task name.")

        else:

            st.session_state.tasks.append({
                "id": st.session_state.next_task_id,
                "name": name.strip(),
                "team": team,
                "priority": priority,
                "due_date": due.isoformat(),
                "status": "Not Started"
            })

            st.session_state.next_task_id += 1

            st.success("Task created successfully.")

    st.divider()

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
                    "task is blocked."
                )

            if (
                task["status"] != "Completed"
                and date.fromisoformat(
                    task["due_date"]
                ) < date.today()
            ):

                st.error("This task is overdue.")

    st.caption(
        "Tasks are stored only in this browser session. "
        "They are not shared or permanently saved."
    )


# TAB 3: AGENT COORDINATION

with tab3:

    st.subheader("External Agent Coordination")

    st.write(
        "Future integrations will let Strativa send "
        "approved work to specialized agents and "
        "receive status reports."
    )

    st.info(
        "No external agents are connected yet. "
        "Automatic agent-reported status changes "
        "are not implemented."
    )

    st.write(
        "Planned capabilities: request routing, "
        "agent responses, conflict escalation, "
        "and management summaries."
    )


# TAB 4: PERFORMANCE DASHBOARD

with tab4:

    st.subheader(
        "Management Performance Dashboard"
    )

    tasks = st.session_state.tasks

    total = len(tasks)

    completed = sum(
        t["status"] == "Completed"
        for t in tasks
    )

    active = sum(
        t["status"] in (
            "Not Started",
            "In Progress"
        )
        for t in tasks
    )

    blocked = sum(
        t["status"] == "Blocked"
        for t in tasks
    )

    overdue = sum(
        t["status"] != "Completed"
        and date.fromisoformat(
            t["due_date"]
        ) < date.today()
        for t in tasks
    )

    a, b, c, d = st.columns(4)

    a.metric("Total Tasks", total)
    b.metric("Active Tasks", active)
    c.metric("Completed Tasks", completed)
    d.metric("Blocked Tasks", blocked)

    rate = completed / total if total else 0

    st.markdown("### Task Completion Progress")

    st.progress(
        rate,
        text=f"{rate * 100:.1f}% completed"
    )

    st.markdown("### Operational Alerts")

    if blocked:
        st.warning(
            f"{blocked} task(s) blocked "
            "and requiring attention."
        )

    if overdue:
        st.error(
            f"{overdue} task(s) overdue."
        )

    if not blocked and not overdue:
        st.success(
            "No blocked or overdue tasks."
        )

    st.caption(
        "Dashboard reflects tasks "
        "in the current session only."
    )


# FOOTER

st.divider()

st.caption(
    "STRATIVA | Midlevel Manager Agent | "
    "Academic Project Prototype"
)
