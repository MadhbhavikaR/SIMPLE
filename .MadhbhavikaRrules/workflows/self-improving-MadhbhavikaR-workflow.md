---
description: "A global workflow to reflect on a task and propose improvements to active rules based on user feedback and multi‑step work."
author: "MadhbhavikaR Team"
version: "1.0"
tags: ["reflection", "rules", "workflow", "process-improvement"]
globs: ["*.*"]
---

This is a manual workflow. Invoke with `/self-improving-MadhbhavikaR.md`. The goal is to propose focused, high‑value improvements to your active .MadhbhavikaRrules (global and/or workspace). No diff scaffolding here — handle mechanics as needed.

<task name="Self-Improving MadhbhavikaR Reflection">

<task_objective>
Reflect on completed tasks to identify opportunities for improving active .MadhbhavikaRrules based on user feedback and multi-step work patterns.
</task_objective>

<detailed_sequence_steps>
####### Self-Improving MadhbhavikaR Reflection — Detailed Sequence of Steps

####### 1. Applicability Check

1. Ask whether reflection is warranted for this task:
   ```xml
   <ask_followup_question>
   <question>Did this task involve user feedback at any point OR multiple non-trivial steps (e.g., several file edits, complex logic generation)?</question>
   <options>["Yes — proceed", "No — end workflow"]</options>
   </ask_followup_question>
   ```

2. If "No — end workflow", conclude briefly and stop.

####### 2. Offer Reflection

1. Confirm the user wants reflection and proposals:
   ```xml
   <ask_followup_question>
   <question>Before I proceed, would you like me to reflect on our interaction and suggest potential improvements to the active .MadhbhavikaRrules?</question>
   <options>["Yes — reflect", "No — end workflow"]</options>
   </ask_followup_question>
   ```

2. If "No — end workflow", conclude and stop.

####### 3. Identify Active Rules (Best-Effort)

1. Check for workspace rules in `.rules/` directory
2. Check for global rules in user's global Rules directory
3. List accessible rule files for review

####### 4. Load Accessible Rule Files

1. Read each accessible rule file that needs consideration
2. Analyze current rule content and structure

####### 5. Review and Synthesize Opportunities

1. Summarize relevant user feedback from the task
2. Identify where rules helped or hindered the workflow
3. Propose targeted improvements focused on:
   - Addressing user feedback directly
   - Improving clarity and conciseness
   - Consolidating overlapping guidance
   - Removing outdated or low-impact sections

####### 6. Present Proposals

1. Provide a concise list of suggested changes per file
2. Keep focus on practical, high-value edits
3. Avoid diff blocks - present clear recommendations

####### 7. Approval to Act

1. Ask how to proceed:
   ```xml
   <ask_followup_question>
   <question>Would you like me to apply these improvements now where possible, or just present recommendations?</question>
   <options>["Apply now", "Show recommendations only", "Cancel"]</options>
   </ask_followup_question>
   ```

####### 8. Execute or Report

1. If "Apply now": implement updates for accessible files
2. If "Show recommendations only": present a clean summary for manual application
3. If "Cancel": make no changes

####### 9. Conclude

1. Summarize what changed or what to change next
2. Provide final summary of improvements
3. Complete the workflow

</detailed_sequence_steps>

<notes>
- Manual workflow; not auto-triggered. Run via `/self-improving-MadhbhavikaR.md` when desired.
- Keep proposals short, specific, and actionable.
- No diff/replace scaffolding in the output; handle mechanics as needed.
</notes>

</task>