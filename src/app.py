# # app.py
# """
# Streamlit front-end for the Smartphone Sales AI Agent.
# Features:
#  - Enter OpenAI API key in a secure textbox (used for this session).
#  - Shows dataset summary and sample rows.
#  - Improved quick chart: pick numeric column or group by categorical column.
#  - Chat interface that passes the session API key to agent.run_llm_conversation.
# """
#
# import streamlit as st
# import sqlite3
# import pandas as pd
# import logging
# import re
#
# from pathlib import Path
# import os
#
# from agent import get_agg_stats, run_llm_conversation, create_ticket, safe_execute_select, DB_PATH, TABLE_NAME
#
# logging.basicConfig(level=logging.INFO)
# LOG = logging.getLogger("app")
#
# st.set_page_config(page_title="Smartphone Sales AI Agent", layout="wide")
# st.title("Capstone: Smartphone Sales AI Agent")
#
# # Top-right: API key input (store in session_state)
# if "openai_key" not in st.session_state:
#     st.session_state.openai_key = os.environ.get("OPENAI_API_KEY", "")
#
# with st.sidebar:
#     st.header("Settings")
#     st.session_state.openai_key = st.text_input(
#         "OpenAI API Key (optional for LLM)",
#         type="password",
#         value=st.session_state.openai_key,
#         help="Enter your OpenAI API key for model-powered responses. Leaves blank to disable LLM calls."
#     )
#     st.markdown("---")
#     st.write(f"DB path: `{DB_PATH}`")
#     st.write(f"Table: `{TABLE_NAME}`")
#     st.markdown("---")
#     st.header("Sample queries")
#     st.write(
#         "- Show top 5 phones by price\n- Phones under $300\n- Average price by brand\n- Which phone has the largest battery?"
#     )
#     st.markdown("---")
#     st.write("Safety: agent blocks destructive SQL and only allows read-only SELECT/PRAGMA.")
#
# # Dataset summary
# with st.expander("Dataset summary (aggregated info)"):
#     try:
#         stats = get_agg_stats()
#         col1, col2 = st.columns([1, 2])
#         with col1:
#             st.metric("Rows", stats["total_rows"])
#             st.write("Columns:")
#             st.write(stats["columns"])
#         with col2:
#             st.subheader("Top brands (sample)")
#             if stats.get("top_brands_sample"):
#                 df_br = pd.DataFrame(stats["top_brands_sample"])
#                 st.dataframe(df_br)
#             else:
#                 st.write("No 'brand' column detected or top sample not available.")
#     except Exception as e:
#         st.error(f"Error getting aggregated stats: {e}")
#         LOG.exception("Error in get_agg_stats call")
#
# st.markdown("---")
#
# # Sample rows
# st.subheader("Sample rows")
# try:
#     if not DB_PATH.exists():
#         st.warning("Database file not found. Run seed_db.py first.")
#     else:
#         conn = sqlite3.connect(DB_PATH)
#         df_sample = pd.read_sql_query(f"SELECT * FROM {TABLE_NAME} LIMIT 10", conn)
#         st.dataframe(df_sample)
#         conn.close()
# except Exception as e:
#     st.error(f"Could not load sample rows: {e}")
#     LOG.exception("Error loading sample rows")
#
# st.markdown("---")
#
# # Improved Quick Chart (REPLACE existing chart block with this)
# st.subheader("Quick Chart")
# chart_msg = st.empty()
# try:
#     if DB_PATH.exists():
#         conn = sqlite3.connect(DB_PATH)
#         df_all = pd.read_sql_query(f"SELECT * FROM {TABLE_NAME} LIMIT 5000", conn)
#         conn.close()
#
#         # Build a cleaned copy for numeric detection:
#         df_clean = df_all.copy()
#
#         # 1) Normalize column names for display (map original -> safe)
#         orig_to_safe = {}
#         for c in df_clean.columns:
#             safe = re.sub(r"[^0-9a-zA-Z]+", "_", c).strip("_").lower()
#             orig_to_safe[c] = safe
#         # rename columns for working copy
#         df_clean.rename(columns=orig_to_safe, inplace=True)
#
#         # 2) Try to coerce many text columns into numeric by stripping non-numeric chars (preserve decimals)
#         for col in list(df_clean.columns):
#             # produce a candidate numeric by removing anything except digits, dot and minus
#             try:
#                 # If column dtype is object, attempt to parse numbers from strings
#                 if df_clean[col].dtype == "object":
#                     # remove commas, currency signs, words like 'usd' etc., keep digits/dot/minus
#                     cleaned = df_clean[col].astype(str).str.replace(r"[^0-9\.\-]+", "", regex=True)
#                     coerced = pd.to_numeric(cleaned, errors="coerce")
#                     # if a reasonable fraction of values parsed to numbers, keep it as numeric helper
#                     non_null_ratio = coerced.notnull().sum() / max(1, len(coerced))
#                     if non_null_ratio >= 0.05:  # >=5% parse rate -> keep as numeric variant
#                         df_clean[col + "_num"] = coerced
#                 elif pd.api.types.is_numeric_dtype(df_clean[col]):
#                     df_clean[col + "_num"] = df_clean[col]
#             except Exception:
#                 # ignore parsing errors for any column
#                 pass
#
#         # Now collect numeric helpers
#         numeric_cols = [c for c in df_clean.columns if c.endswith("_num")]
#         # Also include integer numeric columns (like launched_year)
#         numeric_cols += [c for c in df_clean.columns if pd.api.types.is_integer_dtype(df_clean[c]) and not c.endswith("_num")]
#         numeric_cols = list(dict.fromkeys(numeric_cols))  # dedupe preserving order
#
#         # Categorical columns on the cleaned DF (exclude _num variants)
#         cat_cols = [c for c in df_clean.columns if not c.endswith("_num") and df_clean[c].dtype == "object"]
#
#         if not numeric_cols and not cat_cols:
#             st.write("No columns available for charting.")
#         else:
#             col_a, col_b = st.columns([2, 1])
#             with col_a:
#                 chart_mode = st.radio("Chart mode", options=["Plot numeric column", "Group by categorical"], index=0)
#                 if chart_mode == "Plot numeric column":
#                     if not numeric_cols:
#                         st.warning("No numeric columns available after parsing.")
#                     else:
#                         num_col = st.selectbox("Numeric column (parsed)", options=numeric_cols, index=0)
#                         # plot a sample (dropna)
#                         st.line_chart(df_clean[num_col].dropna().reset_index(drop=True))
#                 else:
#                     if not cat_cols:
#                         st.warning("No categorical columns available.")
#                     else:
#                         cat_col = st.selectbox("Categorical column (group by)", options=cat_cols, index=0)
#                         agg_choice = st.selectbox("Aggregate numeric column (or count)", options=["count"] + numeric_cols, index=0)
#                         if agg_choice == "count":
#                             grouped = df_clean.groupby(cat_col).size().reset_index(name="count").sort_values("count", ascending=False).head(25)
#                             st.bar_chart(grouped.set_index(cat_col))
#                         else:
#                             grouped = df_clean.groupby(cat_col)[agg_choice].mean().reset_index().sort_values(agg_choice, ascending=False).head(25)
#                             st.bar_chart(grouped.set_index(cat_col))
#     else:
#         st.info("Seed the DB first to see charts.")
# except Exception as e:
#     chart_msg.error("Chart load failed: " + str(e))
#     LOG.exception("Chart load error")
#
#
# st.markdown("---")
#
# # Chat area
# st.subheader("Ask the Agent")
# if "history" not in st.session_state:
#     st.session_state.history = []
#
# user_input = st.text_area("Type your question (e.g., 'Show top 5 phones by price', 'Phones under $300')", height=140)
#
# col1, col2 = st.columns([1, 1])
# with col1:
#     if st.button("Send to Agent"):
#         if not user_input.strip():
#             st.warning("Please type a question.")
#         else:
#             st.session_state.history.append({"role": "user", "content": user_input})
#             with st.spinner("Contacting agent... (see server logs)"):
#                 try:
#                     resp = run_llm_conversation(user_input, api_key=st.session_state.openai_key or None)
#                     assistant_text = resp.get("assistant", "")
#                     st.session_state.history.append({"role": "assistant", "content": assistant_text})
#                 except Exception as e:
#                     LOG.exception("Agent error")
#                     st.session_state.history.append({"role": "assistant", "content": f"Error: {e}"})
# with col2:
#     if st.button("Create Support Ticket"):
#         st.session_state._ticketing = True
#
# if st.session_state.get("_ticketing"):
#     st.markdown("### Create a support ticket")
#     title = st.text_input("Ticket title", value="Data support request")
#     desc = st.text_area("Description", value="Describe the issue or request.")
#     if st.button("Submit Ticket"):
#         try:
#             ticket = create_ticket(title=title, description=desc)
#             st.success(f"Ticket created: #{ticket['id']}")
#             st.session_state._ticketing = False
#         except Exception as e:
#             st.error(f"Failed to create ticket: {e}")
#
# st.markdown("---")
# st.subheader("Conversation history")
# for msg in reversed(st.session_state.history):
#     if msg["role"] == "user":
#         st.markdown(f"**You:** {msg['content']}")
#     else:
#         st.markdown(f"**Agent:** {msg['content']}")
#
# st.sidebar.markdown("---")
# st.sidebar.write("Notes: Enter your OpenAI API key in the sidebar for LLM responses (not stored). The app uses the key only for the current session.")


import streamlit as st
import openai
import time
import json
import pandas as pd
import requests

# Filename of the CSV (assume it's in the same directory)
CSV_FILENAME = "src/Mobiles Dataset (2025).csv"

# Function definition for the support ticket tool
support_ticket_function = {
    "name": "create_support_ticket",
    "description": "Create a support ticket for issues that require human intervention. This should be used when the query cannot be answered using the data or requires manual review.",
    "parameters": {
        "type": "object",
        "properties": {
            "issue_description": {
                "type": "string",
                "description": "A detailed description of the issue or query that needs human support."
            }
        },
        "required": ["issue_description"]
    }
}

st.title("Capstone Project 1 - Chat with Data")

# Sidebar for dataset info
with st.sidebar:
    st.header("Dataset Information")
    try:
        df = pd.read_csv(CSV_FILENAME)
        st.write(f"Total rows: {len(df)}")
        st.write("Number of models per company:")
        company_counts = df['Company Name'].value_counts()
        st.bar_chart(company_counts)
        st.write("Sample Queries:")
        st.write("- What is the average launched price in USA for Apple phones?")
        st.write("- List the top 5 heaviest mobiles.")
        st.write("- Which phones have battery capacity over 5000mAh?")
        st.write("Contact Info: support@datainsights.app")
    except FileNotFoundError:
        st.error(f"Dataset file '{CSV_FILENAME}' not found. Please ensure it's in the same directory.")

api_key = st.text_input("Enter your OpenAI API key", type="password")

if api_key:
    client = openai.OpenAI(api_key=api_key)

    # Upload the CSV file if not already uploaded
    if "file_id" not in st.session_state:
        try:
            with open(CSV_FILENAME, "rb") as f:
                file = client.files.create(file=f, purpose="assistants")
            st.session_state.file_id = file.id
        except FileNotFoundError:
            st.error(f"CSV file '{CSV_FILENAME}' not found.")
            st.stop()

    # Create the assistant if not already created
    if "assistant_id" not in st.session_state:
        assistant = client.beta.assistants.create(
            name="Data Insights Agent",
            instructions="""
You are an AI agent that assists users in getting information from the provided mobile dataset CSV file.
Use the code_interpreter tool to analyze the data by writing Python code.
Do not send the entire dataset to the user; only extract relevant information, summaries, or aggregated data.
Never execute dangerous operations like deleting files, modifying data, or any write operations.
If the query is complex, not related to the data, or cannot be answered confidently, suggest creating a support ticket.
Print logs of your actions in the response if needed.
The CSV columns are: Company Name, Model Name, Mobile Weight, RAM, Front Camera, Back Camera, Processor, Battery Capacity, Screen Size, Launched Price (Pakistan), Launched Price (India), Launched Price (China), Launched Price (USA), Launched Price (Dubai), Launched Year.
Prices are in strings like "PKR 224,999", so clean them for calculations (e.g., remove commas and currency).
""",
            model="gpt-4o",
            tools=[
                {"type": "code_interpreter"},
                {"type": "function", "function": support_ticket_function}
            ],
            tool_resources={
                "code_interpreter": {
                    "file_ids": [st.session_state.file_id]
                }
            }
        )
        st.session_state.assistant_id = assistant.id

    # Create or get thread
    if "thread_id" not in st.session_state:
        thread = client.beta.threads.create()
        st.session_state.thread_id = thread.id

    # Display chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User input
    if prompt := st.chat_input("Ask about the mobile dataset..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Add message to thread
        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=prompt
        )

        # Create run
        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=st.session_state.assistant_id
        )

        # Poll for run completion
        while run.status in ["queued", "in_progress", "requires_action"]:
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id,
                run_id=run.id
            )

            # --------------------------------------------------------------
            # REPLACE the whole “if run.status == "requires_action":” block
            # with the code below (inside the polling loop)
            # --------------------------------------------------------------
            if run.status == "requires_action":
                tool_outputs = []
                for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                    if tool_call.function.name == "create_support_ticket":
                        args = json.loads(tool_call.function.arguments)
                        issue_desc = args["issue_description"]

                        # ---- REAL GITHUB ISSUE CREATION -----------------
                        try:
                            repo = st.secrets.get("GITHUB_REPO")  # e.g. "owner/repo"
                            token = st.secrets.get("GITHUB_TOKEN")  # PAT with repo scope
                            if not repo or not token:
                                raise ValueError("GitHub secrets missing")

                            url = f"https://api.github.com/repos/{repo}/issues"
                            payload = {
                                "title": f"[Support] {issue_desc.splitlines()[0][:100] or 'Untitled'}",
                                "body": issue_desc,
                                "labels": ["support", "capstone"]
                            }
                            headers = {
                                "Authorization": f"token {token}",
                                "Accept": "application/vnd.github+json"
                            }
                            resp = requests.post(url, json=payload, headers=headers, timeout=10)
                            resp.raise_for_status()
                            issue = resp.json()
                            issue_no = issue["number"]
                            issue_url = issue["html_url"]
                            output = f"Support ticket created → [Issue #{issue_no}]({issue_url})"
                        except Exception as e:
                            # ---- FALLBACK to console if anything goes wrong ----
                            fallback_id = int(time.time() * 1000) % 1_000_000
                            print("\n=== SUPPORT TICKET (fallback) ===")
                            print(f"Ticket #{fallback_id}")
                            print(issue_desc)
                            print("================================\n")
                            output = f"Ticket #{fallback_id} created (GitHub error: {e})"
                        # --------------------------------------------------

                        tool_outputs.append({
                            "tool_call_id": tool_call.id,
                            "output": output
                        })

                if tool_outputs:
                    client.beta.threads.runs.submit_tool_outputs(
                        thread_id=st.session_state.thread_id,
                        run_id=run.id,
                        tool_outputs=tool_outputs
                    )

        # Print logs to console (retrieve run steps)
        steps = client.beta.threads.runs.steps.list(
            thread_id=st.session_state.thread_id,
            run_id=run.id
        )
        print("Run Steps:")
        for step in steps.data:
            print(step)

        # Get the latest assistant message
        messages = client.beta.threads.messages.list(
            thread_id=st.session_state.thread_id
        )
        assistant_message = messages.data[0].content[0].text.value
        st.session_state.messages.append({"role": "assistant", "content": assistant_message})
        with st.chat_message("assistant"):
            st.markdown(assistant_message)
else:
    st.info("Please enter your OpenAI API key to start chatting.")