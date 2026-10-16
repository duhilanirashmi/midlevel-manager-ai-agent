
import streamlit as st
from datetime import date, datetime

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Strativa | Midlevel Manager Agent",
    page_icon="🔀",
    layout="wide"
)

# --------------------------------------------------
# SESSION DATA
# --------------------------------------------------

# Tasks are temporary and belong to the current session.
# Permanent storage will be added in a later phase.

if "tasks" not in st.session_state:
    st.session_state.tasks = []

if "next_task_id" not in st.session_state:
    st.session_state.next_task_id = 1

# --------------------------------------------------
# APPLICATION HEADER
# --------------------------------------------------

st.title(":material/account_tree: STRATIVA")
st.caption("Where Strategy Becomes Action.")

st.write(
    "**Midlevel Manager Agent | "
    "Strategy • Coordination • Execution**"
)

st.write(
    "Translate executive goals into operational action plans, "
    "coordinate specialized agents, and monitor performance."
)

st.divider()

# --------------------------------------------------
# NAVIGATION
# --------------------------------------------------

tab1, tab2, tab3, tab4 = st.tabs([
    "Management Assistant",
    "Task Management",
    "Agent Coordination",
    "Performance Dashboard"
])

# --------------------------------------------------
# TAB 1: MANAGEMENT ASSISTANT
# --------------------------------------------------

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
            st.success("Management analysis generated.")

            goal_lower = goal.lower()

            st.markdown("### 1. Goal Assessment")
            st.write(f"**Executive Goal:** {goal}")

            if (
                "efficien" in goal_lower
                or "productiv" in goal_lower
            ):

                category = "Operational Efficiency"

                actions = [
                    "Review current workflows and identify bottlenecks.",
                    "Evaluate workload distribution across teams.",
                    "Identify repetitive activities suitable for automation.",
                    "Implement process improvements and track results."
                ]

                kpis = [
                    "Process completion time",
                    "Tasks completed per employee",
                    "Operational cost per task",
                    "Productivity improvement percentage"
                ]

            elif (
                "customer" in goal_lower
                or "service" in goal_lower
            ):

                category = "Customer Experience"

                actions = [
                    "Review customer feedback and service performance.",
                    "Identify common service issues and escalation patterns.",
                    "Develop improvement initiatives with service teams.",
                    "Monitor customer satisfaction and resolution rates."
                ]

                kpis = [
                    "Customer satisfaction score",
                    "Average resolution time",
                    "First-contact resolution rate",
                    "Customer complaint volume"
                ]

            elif (
                "cost" in goal_lower
                or "budget" in goal_lower
            ):

                category = "Cost Management"

                actions = [
                    "Review departmental expenses and resource utilization.",
                    "Identify opportunities to reduce unnecessary spending.",
                    "Prioritize improvements with measurable financial impact.",
                    "Monitor spending against the approved budget."
                ]

                kpis = [
                    "Budget variance",
                    "Cost savings",
                    "Resource utilization rate",
                    "Cost per completed task"
                ]

            else:

                category = "General Business Operations"

                actions = [
                    "Clarify the desired business outcome.",
                    "Identify stakeholders and available resources.",
                    "Break the goal into measurable workstreams.",
                    "Review progress and adjust the action plan."
                ]

                kpis = [
                    "Task completion rate",
                    "Milestone achievement",
                    "Resource utilization",
                    "Overall goal progress"
                ]

            st.write(f"**Management Focus:** {category}")

            st.markdown("### 2. Recommended Action Plan")

            for i, action in enumerate(actions, 1):
                st.write(f"{i}. {action}")

            st.markdown("### 3. Suggested Performance Metrics")

            for kpi in kpis:
                st.write(f"• {kpi}")

            st.markdown("### 4. Risks and Management Oversight")

            st.warning(
                "Potential risks include resource constraints, "
                "competing priorities, implementation delays, "
                "and insufficient performance data."
            )

            st.info(
                "Human approval is recommended before making "
                "staffing, budget, or organizational changes."
            )

            st.caption(
                "Prototype analysis: rule-based recommendations. "
                "AI model integration is planned for a later stage."
            )

# --------------------------------------------------
# TAB 2: TASK MANAGEMENT
# --------------------------------------------------

with tab2:

    st.subheader("Task Allocation & Tracking")

    st.write(
        "Create operational tasks, assign responsibilities, "
        "set priorities, and monitor progress."
    )

    st.markdown("### Create a New Task")

    with st.form("create_task_form", clear_on_submit=True):

        task_name = st.text_input(
            "Task Name",
            placeholder="Review current operational workflows"
        )

        assigned_team = st.selectbox(
            "Assign To",
            [
                "Operations Team",
                "Human Resources",
                "Finance Team",
                "Customer Support",
                "IT Team",
                "Management"
            ]
        )

        priority = st.selectbox(
            "Priority",
            ["High", "Medium", "Low"]
        )

        due_date = st.date_input(
            "Due Date",
            value=date.today()
        )

        submitted = st.form_submit_button(
            "Create Task",
            type="primary"
        )

        if submitted:

            if not task_name.strip():
                st.warning("Please enter a task name.")

            else:
                new_task = {
                    "id": st.session_state.next_task_id,
                    "name": task_name.strip(),
                    "team": assigned_team,
                    "priority": priority,
                    "due_date": due_date.isoformat(),
                    "status": "Not Started",
                    "created_at": datetime.now().isoformat()
                }

                st.session_state.tasks.append(new_task)
                st.session_state.next_task_id += 1

                st.success("Task created successfully.")

    st.divider()

    st.markdown("### Task Tracker")

    if not st.session_state.tasks:

        st.info(
            "No tasks created yet. "
            "Use the form above to add your first task."
        )

    else:

        for task in st.session_state.tasks:

            with st.expander(
                f"Task #{task['id']} — {task['name']}",
                expanded=False
            ):

                st.write(f"**Assigned Team:** {task['team']}")
                st.write(f"**Priority:** {task['priority']}")
                st.write(f"**Due Date:** {task['due_date']}")

                current_status = task["status"]

                status_options = [
                    "Not Started",
                    "In Progress",
                    "Completed",
                    "Blocked"
                ]

                new_status = st.selectbox(
                    "Task Status",
                    status_options,
                    index=status_options.index(current_status),
                    key=f"status_{task['id']}"
                )

                if new_status != current_status:
                    task["status"] = new_status
                    st.success("Task status updated.")

                if (
                    task["status"] != "Completed"
                    and date.fromisoformat(task["due_date"]) < date.today()
                ):
                    st.error("This task is overdue.")

                if task["status"] == "Blocked":
                    st.warning(
                        "Management attention required: "
                        "this task is currently blocked."
                    )

    st.caption(
        "Prototype storage: tasks are stored in the "
        "current Streamlit session and are not permanent."
    )

# --------------------------------------------------
# TAB 3: AGENT COORDINATION
# --------------------------------------------------

with tab3:

    st.subheader("External Agent Coordination")

    st.write(
        "Strativa is designed to coordinate specialized "
        "agents and support cross-functional decisions."
    )

    st.markdown("### Planned Coordination Capabilities")

    st.write(
        "• Connect with external agents developed by other students."
    )

    st.write(
        "• Assign requests to specialized agents."
    )

    st.write(
        "• Collect and consolidate agent recommendations."
    )

    st.write(
        "• Identify conflicting recommendations and escalate decisions."
    )

    st.write(
        "• Provide consolidated management summaries."
    )

    st.info(
        "External agent communication is planned but "
        "has not been implemented yet."
    )

# --------------------------------------------------
# TAB 4: PERFORMANCE DASHBOARD
# --------------------------------------------------

with tab4:

    st.subheader("Management Performance Dashboard")

    tasks = st.session_state.tasks

    total_tasks = len(tasks)

    completed_tasks = sum(
        1 for task in tasks
        if task["status"] == "Completed"
    )

    active_tasks = sum(
        1 for task in tasks
        if task["status"] in ["Not Started", "In Progress"]
    )

    blocked_tasks = sum(
        1 for task in tasks
        if task["status"] == "Blocked"
    )

    overdue_tasks = sum(
        1 for task in tasks
        if (
            task["status"] != "Completed"
            and date.fromisoformat(task["due_date"]) < date.today()
        )
    )

    completion_rate = (
        completed_tasks / total_tasks * 100
        if total_tasks > 0 else 0
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Tasks", total_tasks)
    col2.metric("Active Tasks", active_tasks)
    col3.metric("Completed Tasks", completed_tasks)
    col4.metric("Blocked Tasks", blocked_tasks)

    st.divider()

    st.markdown("### Task Completion Progress")

    st.progress(
        completion_rate / 100,
        text=f"{completion_rate:.1f}% completed"
    )

    st.markdown("### Operational Alerts")

    if blocked_tasks > 0:
        st.warning(
            f"{blocked_tasks} task(s) are blocked "
            "and require management attention."
        )

    if overdue_tasks > 0:
        st.error(
            f"{overdue_tasks} task(s) are overdue."
        )

    if blocked_tasks == 0 and overdue_tasks == 0:
        st.success("No blocked or overdue tasks.")

    st.caption(
        "Dashboard metrics reflect tasks entered "
        "during the current session only."
    )

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "STRATIVA | Midlevel Manager Agent | "
    "Academic Project Prototype"
)
