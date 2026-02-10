Conversation with Co-pilot : 

What do you think calculate_task_score() does? List the behaviors you believe it implements, in your own words.

GPT-5.2-Codex • 1x
I believe it calculates the priority of a task based on the task class imported from .models, the class has mutliple fields, due date etc

You’ve got the gist. Behaviors you didn’t mention:

Base score uses TaskPriority with weights (LOW=10, MEDIUM=20, HIGH=40, URGENT=60); unknown priority gives 0.
Due date adds tiered boosts (overdue +35, today +20, next 2 days +15, next week +10).
Status penalties (DONE −50, REVIEW −15).
Tag boost if any tag is in {blocker, critical, urgent} (+8).
Recent update boost if updated within 1 day (+5).
Now: what edge cases do you think should be tested?

Whether or not the due date exists, 2. Whether or not the priority is a negative integer
Good starts. Additional edge cases you didn’t mention:

Due date boundary buckets: overdue vs today vs in 1–2 days vs 3–7 days vs >7 days.
task.status being DONE or REVIEW (penalties) vs other statuses.
Tags list empty vs contains one of the trigger tags; case-sensitivity (e.g., "Urgent" vs "urgent").
updated_at within last day vs exactly 1 day ago vs older.
task.priority not in TaskPriority (e.g., None or unknown enum) should yield base score 0, not error.
Now: which test should you write first, and why?



Task list is empty. Because at times a user may enter an empty list. Hence proper error handling should be implemented to ensure that empty list inputs do not crash the software

Empty list applies to sort_tasks_by_importance()/get_top_priority_tasks(), not calculate_task_score() (it takes a single task). For calculate_task_score(), which test would you write first and why?

Negative numbers. If negaive priorties are entered, the proper error handling protocols need to be put in place

Negative priorities aren’t explicitly handled here—task.priority is looked up in priority_weights, so anything not in TaskPriority yields base score 0 (no error). That’s a behavior worth testing.

Which test will you write first for calculate_task_score() and why? For example: “base score from priority only,” “overdue due date adds +35,” or “DONE status subtracts 50.”



I don't know then, help me out

Start with the simplest, most deterministic test: “base score from priority only.”
Why: it isolates the core mapping and makes later tests additive.

Example target: a task with priority=TaskPriority.HIGH, no due date, neutral status, no tags, updated_at older than 1 day → score should be 40.

Want me to help you outline that test case setup?

Yes, please do

Here’s a simple test outline for the “base score from priority only” case:

Create a task with:
priority=TaskPriority.HIGH
due_date=None
status set to a neutral value (not DONE/REVIEW)
tags=[]
updated_at older than 1 day
Call calculate_task_score(task)
Assert score equals 40 (HIGH weight 4 × 10)
If you tell me which test framework you’re using (pytest/unittest), I’ll translate that outline into the exact structure you should use.


If I am being honest, part 2.2 of this exercise makes zero sense to me, I have no idea what we are trying to achieve with the testing. So I asked the AI to document everything regarding the prompt that came from this exercise
---

## Testing the due-date portion (via sort_tasks_by_importance)

### Principles for a good test
- **Freeze time** so the due-date buckets are deterministic.
- **Isolate the due-date effect** by neutralizing other factors (priority, status, tags, updated_at).
- **Assert ordering** (most urgent first), not just length.
- **Use boundary values** for each bucket (overdue, today, in 1–2 days, in 3–7 days, >7 days).

### One example pytest test (with comments)
```python
def test_sort_by_due_date_buckets_only(freezer):
	# Freeze time so bucket boundaries are deterministic
	freezer.move_to("2026-02-08 12:00:00")
	now = datetime.now()

	# Neutralize other factors so only due date affects score
	base_kwargs = dict(
		priority=TaskPriority.MEDIUM,
		status=TaskStatus.TODO,  # not DONE/REVIEW
		tags=[],
		updated_at=now - timedelta(days=2),  # no recent-update boost
	)

	# Create tasks spanning each due-date bucket
	overdue = Task("overdue", due_date=now - timedelta(days=1), **base_kwargs)
	today = Task("today", due_date=now, **base_kwargs)
	in_2 = Task("in_2_days", due_date=now + timedelta(days=2), **base_kwargs)
	in_7 = Task("in_7_days", due_date=now + timedelta(days=7), **base_kwargs)
	later = Task("later", due_date=now + timedelta(days=10), **base_kwargs)

	# Act
	result = sort_tasks_by_importance([later, today, in_7, overdue, in_2])

	# Assert exact ordering by due-date bucket
	assert [t.title for t in result] == ["overdue", "today", "in_2_days", "in_7_days", "later"]
```

### Questions to reflect on
- How will you freeze time in your test environment (freezegun vs monkeypatch)?
- What “neutral” values will you set for `status`, `tags`, and `updated_at`?
- If two tasks fall into the same due-date bucket, should you assert a specific order?

### Edge cases to add next
- `due_date=None` (no due-date bonus)
- Exactly on bucket boundaries (today, +2 days, +7 days)
- Overdue by 1 day vs overdue by 10 days (still same bucket)

### More precise assertions
- Assert **exact order** when you control all inputs.
- For isolated tests of `calculate_task_score()`, assert **exact numeric score**.
- For tie cases, assert **relative grouping** instead of strict order.

---

## TDD: Assignment boost (+12) for current user

### Test idea (proposed)
Tasks assigned to the current user should receive a +12 score boost, with all other factors neutralized.

### Example pytest test (generated)
```python
from datetime import datetime, timedelta

from task_manager.algo import calculate_task_score
from task_manager.models import Task, TaskPriority, TaskStatus

def test_calculate_task_score_boosts_when_assigned_to_current_user():
	task = Task("Assigned", priority=TaskPriority.MEDIUM)
	task.assigned_to = "user-123"
	task.status = TaskStatus.TODO
	task.due_date = None
	task.tags = []
	task.updated_at = datetime.now() - timedelta(days=2)

	score = calculate_task_score(task, current_user_id="user-123")

	assert score == 20 + 12  # base (MEDIUM*10) + assignment boost
```

### Minimal code to make it pass
- Add `current_user_id=None` parameter to `calculate_task_score()`.
- If `current_user_id` matches `task.assigned_to`, add `+12` to the score.
- Use `getattr(task, "assigned_to", None)` to avoid errors if the attribute is missing.

### Next test to add (after passing)
- No boost when assigned to someone else (same setup, different `current_user_id`).

### Refactor vs add functionality (rule of thumb)
- **Refactor** when tests pass but code is hard to read, duplicated, or brittle.
- **Add functionality** when a new behavior is required and you can express it as a failing test.