
import streamlit as st
from datetime import date, timedelta
from collections import Counter
import pandas as pd

# ----------------------------------------
# PAGE SETTINGS
# ----------------------------------------

st.set_page_config(
    page_title="STRATIVA",
    page_icon="📊",
    layout="wide"
)

TEAMS = [
    "Operations Team",
    "Human Resources",
    "IT Team",
    "Finance Team",
    "Management",
    "Customer Support"
]

PRIORITIES = ["High", "Medium", "Low"]

STATUSES = [
    "Not Started",
    "In Progress",
    "Blocked",
    "Completed"
]

# ----------------------------------------
# SESSION DATA
# ----------------------------------------

defaults = {
    "tasks": [],
    "proposal": [],
    "goal": "",
    "category": "",
    "next_id": 1,
    "proposal_version": 0,
    "notice": ""
}

for key, initial in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = initial


# ----------------------------------------
# DUPLICATE PROTECTION
# ----------------------------------------

def normalized_name(name):
    return " ".join(name.casefold().split())


def existing_names():
    return {
        normalized_name(task["name"])
        for task in st.session_state.tasks
    }


def create_task(name, team, priority, due_date):
    name = name.strip()

    if not name or normalized_name(name) in existing_names():
        return False

    st.session_state.tasks.append({
        "id": st.session_state.next_id,
        "name": name,
        "team": team,
        "priority": priority,
        "due_date": due_date,
        "status": "Not Started"
    })

    st.session_state.next_id += 1
    return True


# ----------------------------------------
# MANAGEMENT PLANNING
# ----------------------------------------

def generate_plan(goal):
    text = goal.lower()

    if any(word in text for word in [
        "customer", "service", "support", "satisfaction"
    ]):
        category = "Customer Experience"

        plan = [
            (
                "Review customer feedback and recurring issues",
                "Customer Support", "High", 4
            ),
            (
                "Evaluate service workloads and response times",
                "Operations Team", "High", 6
            ),
            (
                "Identify improvements to support workflows",
                "IT Team", "Medium", 8
            ),
            (
                "Measure customer experience improvements",
                "Management", "Medium", 14
            )
        ]

    elif any(word in text for word in [
        "budget", "cost", "expense", "saving"
    ]):
        category = "Cost and Resource Management"

        plan = [
            (
                "Review spending and resource allocation",
                "Finance Team", "High", 4
            ),
            (
                "Identify avoidable operational costs",
                "Operations Team", "High", 6
            ),
            (
                "Assess cost-saving automation opportunities",
                "IT Team", "Medium", 8
            ),
            (
                "Measure savings and report outcomes",
                "Management", "Medium", 14
            )
        ]

    else:
        category = "Operational Efficiency"

        plan = [
            (
                "Review workflows and identify bottlenecks",
                "Operations Team", "High", 4
            ),
            (
                "Evaluate workloads and resource capacity",
                "Human Resources", "High", 6
            ),
            (
                "Assess process automation opportunities",
                "IT Team", "Medium", 8
            ),
            (
                "Measure improvements and report outcomes",
                "Management", "Medium", 14
            )
        ]

    proposals = []

    for name, team, priority, days in plan:
        proposals.append({
            "name": name,
            "team": team,
            "priority": priority,
            "due_date": date.today() + timedelta(days=days)
        })

    return category, proposals


# ----------------------------------------
# TASK STATUS UPDATES
# ----------------------------------------

def update_task_status(task_id):
    for task in st.session_state.tasks:
        if task["id"] == task_id:
            task["status"] = st.session_state[
                f"status_{task_id}"
            ]
            break


# ----------------------------------------
# LIVE PERFORMANCE METRICS
# ----------------------------------------

def get_metrics():
    tasks = st.session_state.tasks

    status_counts = Counter(
        task["status"] for task in tasks
    )

    overdue = sum(
        task["due_date"] < date.today()
        and task["status"] != "Completed"
        for task in tasks
    )

    return len(tasks), status_counts, overdue


def show_metrics():
    total, counts, overdue = get_metrics()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Tasks", total)
    col2.metric("In Progress", counts["In Progress"])
    col3.metric("Completed", counts["Completed"])
    col4.metric("Blocked", counts["Blocked"])

    st.metric("Overdue Tasks", overdue)

    if total > 0:
        completion_rate = counts["Completed"] / total

        st.progress(
            completion_rate,
            text=f"Completion rate: {completion_rate:.0%}"
        )

    else:
        st.info(
            "No approved tasks yet. Approve a plan "
            "or create a task to see live metrics."
        )


# ----------------------------------------
# TASK-SPECIFIC RISK DETECTION
# ----------------------------------------

def get_risks():
    tasks = st.session_state.tasks
    risks = []

    for task in tasks:
        if task["status"] == "Completed":
            continue

        if task["status"] == "Blocked":
            risks.append((
                "high",
                f"Task #{task['id']} — {task['name']}: "
                "Blocked; management intervention may be needed."
            ))

        if task["due_date"] < date.today():
            risks.append((
                "high",
                f"Task #{task['id']} — {task['name']}: "
                f"Overdue since {task['due_date'].isoformat()}."
            ))

        elif (
            task["priority"] == "High"
            and task["status"] == "Not Started"
            and task["due_date"] <= date.today() + timedelta(days=2)
        ):
            risks.append((
                "medium",
                f"Task #{task['id']} — {task['name']}: "
                "High priority, not started, "
                f"due {task['due_date'].isoformat()}."
            ))

    pending_by_team = Counter(
        task["team"]
        for task in tasks
        if task["status"] != "Completed"
    )

    for team, count in pending_by_team.items():
        if count >= 3:
            risks.append((
                "medium",
                f"{team}: {count} unfinished tasks. "
                "Review workload and capacity."
            ))

    duplicate_counts = Counter(
        normalized_name(task["name"])
        for task in tasks
    )

    for normalized, count in duplicate_counts.items():
        if count > 1:
            name = next(
                task["name"]
                for task in tasks
                if normalized_name(task["name"]) == normalized
            )

            risks.append((
                "medium",
                f"Existing duplicate records: '{name}' "
                f"appears {count} times. Review manually."
            ))

    return risks


def show_risks():
    if not st.session_state.tasks:
        st.info(
            "No tasks to assess yet. "
            "Approved tasks are required for risk monitoring."
        )
        return

    risks = get_risks()

    if not risks:
        st.success(
            "No blocked, overdue, urgent high-priority, "
            "workload concentration, or duplicate-record "
            "risks detected from current task data."
        )

    for severity, message in risks:
        if severity == "high":
            st.error(message)
        else:
            st.warning(message)

    st.caption(
        "Alerts are based on recorded task data and "
        "simple rules. Management should verify "
        "the context before taking action."
    )


# ----------------------------------------
# APPLICATION HEADER
# ----------------------------------------

st.title(":material/account_tree: STRATIVA")

st.caption("Where Strategy Becomes Action.")

st.markdown(
    "**Midlevel Manager Agent | "
    "Strategy • Coordination • Execution**"
)

st.write(
    "Translate executive goals into operational action plans, "
    "monitor performance, and coordinate specialized agents."
)

st.divider()

tab1, tab2, tab3, tab4 = st.tabs([
    "Management Assistant",
    "Task Management",
    "Agent Coordination",
    "Performance Dashboard"
])


# ----------------------------------------
# TAB 1: MANAGEMENT ASSISTANT
# ----------------------------------------

with tab1:
    st.subheader("Executive Goal Analysis")

    goal = st.text_area(
        "Enter an executive goal or management request",
        value=st.session_state.goal,
        placeholder=(
            "Improve operational efficiency by 15% "
            "while maintaining the current budget."
        )
    )

    if st.button("Analyze Goal", type="primary"):
        if goal.strip():
            category, proposals = generate_plan(goal.strip())

            st.session_state.goal = goal.strip()
            st.session_state.category = category
            st.session_state.proposal = proposals
            st.session_state.proposal_version += 1
            st.session_state.notice = ""

        else:
            st.warning("Please enter a management goal.")

    if st.session_state.notice:
        st.success(st.session_state.notice)

    if st.session_state.proposal:
        st.success(
            "Proposed action plan ready for management review. "
            "No tasks have been assigned yet."
        )

        st.markdown("### 1. Goal Assessment")

        st.write(
            "**Executive Goal:**",
            st.session_state.goal
        )

        st.write(
            "**Management Focus:**",
            st.session_state.category
        )

        st.markdown("### 2. Review Proposed Tasks")

        st.caption(
            "Review and edit proposed tasks before approval. "
            "Existing task descriptions will be skipped "
            "to prevent duplicates."
        )

        version = st.session_state.proposal_version

        with st.form(f"approval_form_{version}"):
            reviewed = []

            for i, proposal in enumerate(
                st.session_state.proposal
            ):
                st.markdown(f"**Proposed Task {i + 1}**")

                include = st.checkbox(
                    "Include this task",
                    value=True,
                    key=f"include_{version}_{i}"
                )

                name = st.text_input(
                    "Task description",
                    value=proposal["name"],
                    key=f"name_{version}_{i}"
                )

                team = st.selectbox(
                    "Suggested team",
                    TEAMS,
                    index=TEAMS.index(proposal["team"]),
                    key=f"team_{version}_{i}"
                )

                priority = st.selectbox(
                    "Priority",
                    PRIORITIES,
                    index=PRIORITIES.index(
                        proposal["priority"]
                    ),
                    key=f"priority_{version}_{i}"
                )

                due_date = st.date_input(
                    "Suggested due date",
                    value=proposal["due_date"],
                    key=f"due_{version}_{i}"
                )

                reviewed.append({
                    "include": include,
                    "name": name.strip(),
                    "team": team,
                    "priority": priority,
                    "due_date": due_date
                })

                st.divider()

            approve = st.form_submit_button(
                "Approve Selected Tasks",
                type="primary"
            )

        if approve:
            selected = [
                item for item in reviewed
                if item["include"]
            ]

            if not selected:
                st.warning("Select at least one task.")

            elif any(not item["name"] for item in selected):
                st.warning(
                    "Every selected task needs a description."
                )

            else:
                created = sum(
                    create_task(
                        item["name"],
                        item["team"],
                        item["priority"],
                        item["due_date"]
                    )
                    for item in selected
                )

                skipped = len(selected) - created

                st.session_state.proposal = []

                st.session_state.notice = (
                    f"Added {created} new task(s). "
                    f"Skipped {skipped} duplicate task(s). "
                    "View Task Management for details."
                )

                st.rerun()

    st.markdown("### 3. Performance Metrics & Progress")
    show_metrics()

    st.markdown("### 4. Risks and Human Oversight")
    show_risks()

    st.caption(
        "Prototype recommendations are rule-based, "
        "not generated by an AI language model."
    )


# ----------------------------------------
# TAB 2: TASK MANAGEMENT
# ----------------------------------------

with tab2:
    st.subheader("Task Allocation & Tracking")

    st.write(
        "Create tasks, assign teams, set priorities, "
        "and monitor operational progress."
    )

    st.markdown("### Create a New Task")

    with st.form("new_task_form", clear_on_submit=True):
        task_name = st.text_input("Task Name")

        task_team = st.selectbox(
            "Assign To",
            TEAMS
        )

        task_priority = st.selectbox(
            "Priority",
            PRIORITIES
        )

        task_due = st.date_input(
            "Due Date",
            value=date.today() + timedelta(days=1)
        )

        submit_task = st.form_submit_button(
            "Create Task",
            type="primary"
        )

    if submit_task:
        if not task_name.strip():
            st.warning("Please enter a task name.")

        elif create_task(
            task_name,
            task_team,
            task_priority,
            task_due
        ):
            st.success("Task created successfully.")

        else:
            st.warning(
                "Duplicate task prevented: "
                "a task with this description already exists."
            )

    st.divider()
    st.markdown("### Task Tracker")

    if not st.session_state.tasks:
        st.info("No tasks have been created yet.")

    for task in st.session_state.tasks:
        with st.expander(
            f"Task #{task['id']} — {task['name']}"
        ):
            st.write(
                "**Assigned Team:**",
                task["team"]
            )

            st.write(
                "**Priority:**",
                task["priority"]
            )

            st.write(
                "**Due Date:**",
                task["due_date"].isoformat()
            )

            st.selectbox(
                "Task Status",
                STATUSES,
                index=STATUSES.index(task["status"]),
                key=f"status_{task['id']}",
                on_change=update_task_status,
                args=(task["id"],)
            )

    st.caption(
        "Task status changes are manual. "
        "Tasks are stored only in the current "
        "Streamlit session, not permanently saved."
    )


# ----------------------------------------
# TAB 3: AGENT COORDINATION
# ----------------------------------------

with tab3:
    st.subheader("External Agent Coordination")

    st.write(
        "STRATIVA is designed to coordinate tasks "
        "with specialized agents developed by other students."
    )

    st.markdown("### Planned Coordination Workflow")

    st.write(
        "1. A manager approves operational tasks."
    )

    st.write(
        "2. STRATIVA sends approved tasks "
        "to authorized external agents."
    )

    st.write(
        "3. External agents acknowledge assignments "
        "and report progress."
    )

    st.write(
        "4. STRATIVA receives updates "
        "and refreshes the management dashboard."
    )

    st.info(
        "External agent communication is planned "
        "but not connected. A shared API and "
        "message format will be required."
    )

    st.markdown("### Current Task Allocation")

    if st.session_state.tasks:
        for task in st.session_state.tasks:
            st.write(
                f"**Task {task['id']}:** "
                f"{task['name']} | "
                f"{task['team']} | "
                f"{task['status']}"
            )
    else:
        st.info("No approved tasks available.")


# ----------------------------------------
# TAB 4: PERFORMANCE DASHBOARD
# ----------------------------------------

with tab4:
    st.subheader("Management Performance Dashboard")

    show_metrics()

    total, status_counts, overdue = get_metrics()

    if total:
        st.markdown("### Task Status Distribution")

        chart = pd.DataFrame({
            "Status": STATUSES,
            "Tasks": [
                status_counts[status]
                for status in STATUSES
            ]
        }).set_index("Status")

        st.bar_chart(chart)

        st.markdown("### Team Workload")

        team_counts = Counter(
            task["team"]
            for task in st.session_state.tasks
            if task["status"] != "Completed"
        )

        workload = pd.DataFrame({
            "Team": list(team_counts.keys()),
            "Unfinished Tasks": list(team_counts.values())
        }).set_index("Team")

        st.bar_chart(workload)

        st.markdown("### Management Summary")

        st.write(
            f"STRATIVA is tracking {total} tasks. "
            f"{status_counts['Completed']} completed, "
            f"{status_counts['In Progress']} in progress, "
            f"{status_counts['Not Started']} not started, "
            f"{status_counts['Blocked']} blocked, "
            f"and {overdue} overdue."
        )

    st.markdown("### Operational Risks")
    show_risks()

    st.caption(
        "Dashboard metrics reflect only this browser "
        "session, not live business systems."
    )


# ----------------------------------------
# FOOTER
# ----------------------------------------

st.divider()

st.caption(
    "STRATIVA | Midlevel Manager Agent | "
    "Academic Project Prototype"
)
