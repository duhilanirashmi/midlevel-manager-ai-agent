
import re
from collections import Counter
from datetime import date, timedelta

import pandas as pd
import streamlit as st

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

DEFAULTS = {
    "tasks": [],
    "next_id": 1,
    "goals": [],
    "next_goal_id": 1,
    "pending_review": None,
    "review_version": 0,
    "notice": "",
    "goal_input": "",
    "selected_goal_id": "New goal",
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ----------------------------------------
# TEXT COMPARISON
# ----------------------------------------

def normalize(value):
    return " ".join(value.casefold().split())


def words(value):
    stop = {
        "the", "a", "an", "and", "or", "to",
        "of", "by", "for", "with", "while",
        "our", "in", "on", "at", "from",
        "is", "be", "as", "current",
        "improve", "increase", "reduce",
        "achieve", "prioritize", "focus",
        "more", "better", "percent"
    }

    return {
        w for w in re.findall(r"[a-z]+", value.lower())
        if len(w) > 2 and w not in stop
    }


def similarity(a, b):
    wa, wb = words(a), words(b)

    if wa and wb:
        return len(wa & wb) / len(wa | wb)

    return 0.0


# ----------------------------------------
# GOAL ANALYSIS
# ----------------------------------------

def goal_category(goal):
    text = goal.lower()

    if any(term in text for term in (
        "customer",
        "service",
        "support",
        "satisfaction",
        "response time"
    )):
        return "Customer Experience"

    if any(term in text for term in (
        "budget",
        "cost",
        "expense",
        "saving",
        "spending"
    )):
        return "Cost and Resource Management"

    return "Operational Efficiency"


def generate_plan(goal):
    category = goal_category(goal)

    if category == "Customer Experience":
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
            ),
        ]

    elif category == "Cost and Resource Management":
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
            ),
        ]

    else:
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
            ),
        ]

    return category, [
        {
            "name": name,
            "team": team,
            "priority": priority,
            "due_date": date.today() + timedelta(days=days)
        }
        for name, team, priority, days in plan
    ]


# ----------------------------------------
# GOAL MANAGEMENT
# ----------------------------------------

def find_goal(goal_id):
    return next(
        (
            g for g in st.session_state.goals
            if g["id"] == goal_id
        ),
        None
    )


def goal_label(goal):
    return f"Goal #{goal['id']} — {goal['text'][:75]}"


def start_review(text, selected):
    category, proposed = generate_plan(text)

    if selected != "New goal":
        match = find_goal(selected)
    else:
        match = next(
            (
                g for g in st.session_state.goals
                if normalize(g["text"]) == normalize(text)
            ),
            None
        )

    if match and normalize(match["text"]) == normalize(text):
        kind = "Repeated goal"
    elif match:
        kind = "Revised goal"
    else:
        kind = "New goal"

    existing_task_names = {
        normalize(t["name"])
        for t in st.session_state.tasks
    }

    reuse = [
        p["name"] for p in proposed
        if normalize(p["name"]) in existing_task_names
    ]

    new = [
        p["name"] for p in proposed
        if normalize(p["name"]) not in existing_task_names
    ]

    st.session_state.review_version += 1

    st.session_state.pending_review = {
        "text": text,
        "category": category,
        "proposed": proposed,
        "goal_id": match["id"] if match else None,
        "previous_text": match["text"] if match else "",
        "kind": kind,
        "reuse": reuse,
        "new": new,
    }

    st.session_state.notice = ""


def save_goal(review):
    goal_id = review["goal_id"]

    if goal_id is None:
        goal_id = st.session_state.next_goal_id
        st.session_state.next_goal_id += 1

        st.session_state.goals.append({
            "id": goal_id,
            "text": review["text"],
            "category": review["category"],
            "history": [review["text"]],
        })

    else:
        goal = find_goal(goal_id)

        if normalize(goal["text"]) != normalize(review["text"]):
            goal["text"] = review["text"]
            goal["category"] = review["category"]
            goal["history"].append(review["text"])

    return goal_id


# ----------------------------------------
# TASK MANAGEMENT
# ----------------------------------------

def create_task(name, team, priority, due_date, goal_id=None):
    name = name.strip()

    if not name:
        return False

    for task in st.session_state.tasks:
        if normalize(task["name"]) == normalize(name):
            return False

    st.session_state.tasks.append({
        "id": st.session_state.next_id,
        "name": name,
        "team": team,
        "priority": priority,
        "due_date": due_date,
        "status": "Not Started",
        "goal_id": goal_id,
    })

    st.session_state.next_id += 1
    return True


def update_task_status(task_id):
    task = next(
        (
            t for t in st.session_state.tasks
            if t["id"] == task_id
        ),
        None
    )

    if task:
        task["status"] = st.session_state[
            f"status_{task_id}"
        ]


# ----------------------------------------
# PERFORMANCE METRICS
# ----------------------------------------

def get_metrics():
    tasks = st.session_state.tasks

    counts = Counter(
        t["status"] for t in tasks
    )

    overdue = sum(
        t["due_date"] < date.today()
        and t["status"] != "Completed"
        for t in tasks
    )

    return len(tasks), counts, overdue


def show_metrics():
    total, counts, overdue = get_metrics()

    cols = st.columns(4)

    labels = [
        "Total Tasks",
        "In Progress",
        "Completed",
        "Blocked"
    ]

    values = [
        total,
        counts["In Progress"],
        counts["Completed"],
        counts["Blocked"]
    ]

    for col, label, count in zip(cols, labels, values):
        col.metric(label, count)

    st.metric("Overdue Tasks", overdue)

    if total:
        rate = counts["Completed"] / total

        st.progress(
            rate,
            text=f"Completion rate: {rate:.0%}"
        )
    else:
        st.info(
            "No approved tasks yet. Approve a plan "
            "or create a task to see live metrics."
        )


# ----------------------------------------
# RISK DETECTION
# ----------------------------------------

def get_risks():
    tasks = st.session_state.tasks
    risks = []

    for task in tasks:
        if task["status"] == "Completed":
            continue

        title = f"Task #{task['id']} — {task['name']}"

        if task["status"] == "Blocked":
            risks.append((
                "high",
                f"{title}: Blocked; management "
                "intervention may be needed."
            ))

        if task["due_date"] < date.today():
            risks.append((
                "high",
                f"{title}: Overdue since "
                f"{task['due_date'].isoformat()}."
            ))

        elif (
            task["priority"] == "High"
            and task["status"] == "Not Started"
            and task["due_date"] <= date.today() + timedelta(days=2)
        ):
            risks.append((
                "medium",
                f"{title}: High priority, not started, "
                f"due {task['due_date'].isoformat()}."
            ))

    pending = Counter(
        t["team"]
        for t in tasks
        if t["status"] != "Completed"
    )

    for team, count in pending.items():
        if count >= 3:
            risks.append((
                "medium",
                f"{team}: {count} unfinished tasks. "
                "Review workload and capacity."
            ))

    duplicates = Counter(
        normalize(t["name"]) for t in tasks
    )

    for key, count in duplicates.items():
        if count > 1:
            name = next(
                t["name"] for t in tasks
                if normalize(t["name"]) == key
            )

            risks.append((
                "medium",
                f"Existing duplicate records: "
                f"'{name}' appears {count} times."
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
        "Alerts are based on recorded task data "
        "and simple rules. Management should verify "
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

    st.caption(
        "Goals and tasks are tracked separately. "
        "A revised goal does not automatically create new tasks."
    )

    st.markdown("### Goal Selection")

    goal_options = (
        ["New goal"]
        + [g["id"] for g in st.session_state.goals]
    )

    selected = st.selectbox(
        "Create a goal or revise an existing one",
        goal_options,
        format_func=lambda x: (
            "New goal"
            if x == "New goal"
            else goal_label(find_goal(x))
        ),
        key="selected_goal_id",
    )

    if selected != "New goal":
        selected_goal = find_goal(selected)

        st.caption(
            f"Current version: {selected_goal['text']}"
        )

        st.caption(
            f"Revision count: "
            f"{len(selected_goal['history']) - 1}"
        )

    goal = st.text_area(
        "Enter an executive goal or management request",
        placeholder=(
            "Improve customer satisfaction by "
            "reducing response times by 20%."
        ),
        key="goal_input",
    )

    if st.button("Analyze Goal", type="primary"):
        if goal.strip():
            start_review(goal.strip(), selected)
        else:
            st.warning("Please enter a management goal.")

    if st.session_state.notice:
        st.success(st.session_state.notice)

    review = st.session_state.pending_review

    if review:
        st.markdown(
            "### 1. Goal Assessment & Change Detection"
        )

        st.write(
            "**Classification:**",
            review["kind"]
        )

        st.write(
            "**Management Focus:**",
            review["category"]
        )

        if review["goal_id"] is not None:
            st.write(
                "**Linked Goal:**",
                f"Goal #{review['goal_id']}"
            )

            st.write(
                "**Previous version:**",
                review["previous_text"]
            )

            st.write(
                "**Submitted version:**",
                review["text"]
            )

            if review["kind"] == "Repeated goal":
                st.info(
                    "The wording matches the existing goal. "
                    "No goal revision is needed."
                )
            else:
                old_words = words(review["previous_text"])
                new_words = words(review["text"])

                added = sorted(new_words - old_words)
                removed = sorted(old_words - new_words)

                st.write(
                    "**Added wording (keywords):**",
                    ", ".join(added) if added
                    else "None detected"
                )

                st.write(
                    "**Removed wording (keywords):**",
                    ", ".join(removed) if removed
                    else "None detected"
                )

                st.caption(
                    "This is a simple keyword comparison, "
                    "not a semantic interpretation of intent."
                )

        else:
            st.write(
                "**Submitted goal:**",
                review["text"]
            )

            same_category = [
                g for g in st.session_state.goals
                if g["category"] == review["category"]
            ]

            if same_category:
                st.warning(
                    "Other goals already exist in this "
                    "management category. Review them before "
                    "creating a separate goal."
                )

                for g in same_category:
                    st.write(
                        f"Goal #{g['id']}: {g['text']}"
                    )

                st.caption(
                    "Similar categories may represent "
                    "separate goals. STRATIVA does not "
                    "merge them automatically."
                )

        st.markdown(
            "### 2. Task Impact Assessment & Approval"
        )

        st.write(
            "**Existing tasks matching the proposed plan:**",
            len(review["reuse"])
        )

        for name in review["reuse"]:
            st.write(
                f"↪ Reuse existing task: {name}"
            )

        st.write(
            "**Potential new tasks:**",
            len(review["new"])
        )

        st.caption(
            "An existing task is identified by matching "
            "its description. Managers must decide whether "
            "the existing task's priority, team, or deadline "
            "should change."
        )

        version = st.session_state.review_version

        with st.form(f"approval_form_{version}"):
            reviewed = []

            for i, proposed in enumerate(
                review["proposed"]
            ):
                st.markdown(
                    f"**Proposed Task {i + 1}**"
                )

                is_existing = normalize(
                    proposed["name"]
                ) in {
                    normalize(t["name"])
                    for t in st.session_state.tasks
                }

                if is_existing:
                    st.info(
                        "Existing task detected. "
                        "It will be reused, not duplicated."
                    )

                include = st.checkbox(
                    "Include this task",
                    value=not is_existing,
                    key=f"include_{version}_{i}"
                )

                name = st.text_input(
                    "Task description",
                    value=proposed["name"],
                    key=f"name_{version}_{i}"
                )

                team = st.selectbox(
                    "Suggested team",
                    TEAMS,
                    index=TEAMS.index(proposed["team"]),
                    key=f"team_{version}_{i}"
                )

                priority = st.selectbox(
                    "Priority",
                    PRIORITIES,
                    index=PRIORITIES.index(
                        proposed["priority"]
                    ),
                    key=f"priority_{version}_{i}"
                )

                due_date = st.date_input(
                    "Suggested due date",
                    value=proposed["due_date"],
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
                "Approve Goal and Selected Tasks",
                type="primary"
            )

        if approve:
            selected_tasks = [
                item for item in reviewed
                if item["include"]
            ]

            if any(
                not item["name"]
                for item in selected_tasks
            ):
                st.warning(
                    "Every selected task needs a description."
                )

            else:
                goal_id = save_goal(review)

                created = sum(
                    create_task(
                        item["name"],
                        item["team"],
                        item["priority"],
                        item["due_date"],
                        goal_id
                    )
                    for item in selected_tasks
                )

                skipped = len(selected_tasks) - created

                st.session_state.pending_review = None

                st.session_state.notice = (
                    f"Goal #{goal_id} approved "
                    f"({review['kind'].lower()}). "
                    f"Added {created} new task(s); "
                    f"skipped {skipped} duplicate task(s). "
                    "Existing task statuses were preserved."
                )

                st.rerun()

    st.markdown("### Goal Register")

    if not st.session_state.goals:
        st.info(
            "No approved goals yet. Analyze and "
            "approve a goal to start tracking it."
        )

    else:
        st.metric(
            "Total Goals",
            len(st.session_state.goals)
        )

        for g in st.session_state.goals:
            with st.expander(goal_label(g)):
                st.write(
                    "**Management Focus:**",
                    g["category"]
                )

                st.write(
                    "**Revision count:**",
                    len(g["history"]) - 1
                )

                st.write("**Version history:**")

                for n, version_text in enumerate(
                    g["history"], 1
                ):
                    st.write(
                        f"Version {n}: {version_text}"
                    )

                linked = [
                    t for t in st.session_state.tasks
                    if t.get("goal_id") == g["id"]
                ]

                st.write(
                    "**Tasks originally created for this goal:**",
                    len(linked)
                )

    st.markdown(
        "### 3. Performance Metrics & Progress"
    )

    show_metrics()

    st.markdown(
        "### 4. Risks and Human Oversight"
    )

    show_risks()

    st.caption(
        "Goal comparisons and recommendations "
        "are rule-based, not generated by an AI language model."
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

        task_goal = st.selectbox(
            "Link to goal (optional)",
            [None] + [
                g["id"] for g in st.session_state.goals
            ],
            format_func=lambda x: (
                "No linked goal"
                if x is None
                else goal_label(find_goal(x))
            )
        )

        submit_task = st.form_submit_button(
            "Create Task",
            type="primary"
        )

    if submit_task:
        if not task_name.strip():
            st.warning(
                "Please enter a task name."
            )

        elif create_task(
            task_name,
            task_team,
            task_priority,
            task_due,
            task_goal
        ):
            st.success(
                "Task created successfully."
            )

        else:
            st.warning(
                "Duplicate task prevented: a task "
                "with this description already exists."
            )

    st.divider()
    st.markdown("### Task Tracker")

    if not st.session_state.tasks:
        st.info(
            "No tasks have been created yet."
        )

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

            st.write(
                "**Linked Goal:**",
                f"Goal #{task['goal_id']}"
                if task.get("goal_id")
                else "None"
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
        "Tasks and goals are stored only in the "
        "current Streamlit session, not permanently saved."
    )


# ----------------------------------------
# TAB 3: AGENT COORDINATION
# ----------------------------------------

with tab3:
    st.subheader(
        "External Agent Coordination"
    )

    st.write(
        "STRATIVA is designed to coordinate tasks "
        "with specialized agents developed by other students."
    )

    st.markdown(
        "### Planned Coordination Workflow"
    )

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
        st.info(
            "No approved tasks available."
        )


# ----------------------------------------
# TAB 4: PERFORMANCE DASHBOARD
# ----------------------------------------

with tab4:
    st.subheader(
        "Management Performance Dashboard"
    )

    st.metric(
        "Tracked Goals",
        len(st.session_state.goals)
    )

    show_metrics()

    total, status_counts, overdue = get_metrics()

    if total:
        st.markdown(
            "### Task Status Distribution"
        )

        chart = pd.DataFrame({
            "Status": STATUSES,
            "Tasks": [
                status_counts[s]
                for s in STATUSES
            ]
        }).set_index("Status")

        st.bar_chart(chart)

        st.markdown(
            "### Team Workload"
        )

        team_counts = Counter(
            t["team"]
            for t in st.session_state.tasks
            if t["status"] != "Completed"
        )

        if team_counts:
            workload = pd.DataFrame({
                "Team": list(team_counts),
                "Unfinished Tasks": list(
                    team_counts.values()
                )
            }).set_index("Team")

            st.bar_chart(workload)
        else:
            st.info(
                "No unfinished tasks to display."
            )

        st.markdown(
            "### Management Summary"
        )

        st.write(
            f"STRATIVA is tracking "
            f"{len(st.session_state.goals)} goals "
            f"and {total} tasks. "
            f"{status_counts['Completed']} completed, "
            f"{status_counts['In Progress']} in progress, "
            f"{status_counts['Not Started']} not started, "
            f"{status_counts['Blocked']} blocked, "
            f"and {overdue} overdue."
        )

    st.markdown(
        "### Operational Risks"
    )

    show_risks()

    st.caption(
        "Dashboard metrics reflect only this "
        "browser session, not live business systems."
    )


# ----------------------------------------
# FOOTER
# ----------------------------------------

st.divider()

st.caption(
    "STRATIVA | Midlevel Manager Agent | "
    "Academic Project Prototype"
)
