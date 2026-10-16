            ]
            st.session_state.analysis_category = category
            st.session_state.analysis_kpis = kpis

    if st.session_state.proposal:
        st.success("Proposed action plan ready for management review. No tasks have been assigned yet.")
        st.markdown("### 1. Goal Assessment")
        st.write(f"**Executive Goal:** {st.session_state.proposal_goal}")
        st.write(f"**Management Focus:** {st.session_state.analysis_category}")
        st.markdown("### 2. Review Proposed Tasks")
        st.caption("Suggested teams, priorities, and deadlines are editable. They are not actual assignments until approved.")
        with st.form("approval_form"):
            reviewed = []
            for i, proposal in enumerate(st.session_state.proposal):
                st.markdown(f"**Proposed Task {i + 1}**")
                include = st.checkbox("Include this task", value=True, key=f"include_{i}")
                name = st.text_input("Task description", value=proposal["name"], key=f"proposal_name_{i}")
                team = st.selectbox("Suggested team", TEAMS, index=TEAMS.index(proposal["team"]), key=f"proposal_team_{i}")
                priority = st.selectbox("Priority", ["High", "Medium", "Low"], index=["High", "Medium", "Low"].index(proposal["priority"]), key=f"proposal_priority_{i}")
                due_date = st.date_input("Suggested due date", value=proposal["due_date"], key=f"proposal_due_{i}")
                reviewed.append((include, name, team, priority, due_date))
                st.divider()
            approve = st.form_submit_button("Approve Selected Tasks", type="primary")
        if approve:
            selected = [item for item in reviewed if item[0]]
            if not selected:
                st.warning("Select at least one task to approve.")
            elif any(not item[1].strip() for item in selected):
                st.warning("Every selected task needs a description.")
            else:
                for _, name, team, priority, due_date in selected:
                    add_task(name.strip(), team, priority, due_date, st.session_state.proposal_goal)
                st.session_state.proposal = []
                st.session_state.approval_notice = f"Approved {len(selected)} task(s). They are now in Task Management."
                st.rerun()

        st.markdown("### 3. Suggested Performance Metrics")
        for kpi in st.session_state.analysis_kpis:
            st.write(f"• {kpi}")
        st.markdown("### 4. Risks and Management Oversight")
        st.warning("Potential risks include resource constraints, competing priorities, implementation delays, and insufficient performance data.")
        st.info("A manager must approve proposed tasks before they enter the tracker. Approval here does not notify real teams.")
        st.caption("Rule-based prototype; AI reasoning is not connected yet.")

with tab2:
    st.subheader("Task Allocation & Tracking")
    st.write("Track approved tasks or create an additional task manually.")
    with st.form("create_task_form", clear_on_submit=True):
        task_name = st.text_input("Task Name", placeholder="Review current operational workflows")
        assigned_team = st.selectbox("Assign To", TEAMS)
        priority = st.selectbox("Priority", ["High", "Medium", "Low"])
        due_date = st.date_input("Due Date", value=date.today() + timedelta(days=1))
        submitted = st.form_submit_button("Create Task", type="primary")
        if submitted:
            if not task_name.strip():
                st.warning("Please enter a task name.")
            else:
                add_task(task_name.strip(), assigned_team, priority, due_date)
                st.success("Task created successfully.")
    st.divider()
    st.markdown("### Task Tracker")
    if not st.session_state.tasks:
        st.info("No tasks yet. Approve proposed tasks in Management Assistant or create one above.")
    else:
        for task in st.session_state.tasks:
            with st.expander(f"Task #{task['id']} — {task['name']}"):
                st.write(f"**Assigned Team:** {task['team']}")
                st.write(f"**Priority:** {task['priority']}")
                st.write(f"**Due Date:** {task['due_date']}")
                st.selectbox(
                    "Task Status", STATUS_OPTIONS,
                    index=STATUS_OPTIONS.index(task["status"]),
                    key=f"task_status_{task['id']}",
                    on_change=update_task_status,
                    args=(task["id"],)
                )
                if task["status"] != "Completed" and date.fromisoformat(task["due_date"]) < date.today():
                    st.error("This task is overdue.")
                if task["status"] == "Blocked":
                    st.warning("Management attention required: this task is blocked.")
    st.caption("Tasks are stored only in this browser session. They are not permanently saved or sent to external teams.")

with tab3:
    st.subheader("External Agent Coordination")
    st.write("Strativa is being designed to coordinate specialized agents and consolidate cross-functional recommendations.")
    st.info("External agent communication is not connected yet. Future integration will require a compatible API, authentication, and shared task storage.")

with tab4:
    st.subheader("Management Performance Dashboard")
    tasks = st.session_state.tasks
    total = len(tasks)
    completed = sum(t["status"] == "Completed" for t in tasks)
    active = sum(t["status"] in ("Not Started", "In Progress") for t in tasks)
    blocked = sum(t["status"] == "Blocked" for t in tasks)
    overdue = sum(t["status"] != "Completed" and date.fromisoformat(t["due_date"]) < date.today() for t in tasks)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Tasks", total)
    col2.metric("Active Tasks", active)
    col3.metric("Completed Tasks", completed)
    col4.metric("Blocked Tasks", blocked)
    st.divider()
    completion_rate = completed / total if total else 0.0
    st.markdown("### Task Completion Progress")
    st.progress(completion_rate, text=f"{completion_rate * 100:.1f}% completed")
    st.markdown("### Operational Alerts")
    if blocked:
        st.warning(f"{blocked} task(s) are blocked and require management attention.")
    if overdue:
        st.error(f"{overdue} task(s) are overdue.")
    if not blocked and not overdue:
        st.success("No blocked or overdue tasks.")
    st.caption("Dashboard metrics reflect the current session only; no live external performance feed is connected.")

st.divider()
st.caption("STRATIVA | Midlevel Manager Agent | Academic Project Prototype")
