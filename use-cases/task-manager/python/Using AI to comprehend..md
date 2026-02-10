Part 1

Notes:
My personal understanding :

The only thing I'm seeing so far is task manager app developed in python. With a some form of database schema implemented in python in the form of class. 
The class is named models.py, and it essentially acts as the parent that Task manager class and its methods inherit from. 

Co-pilot:
Your understanding is close, but one key correction: TaskManager does not inherit from models.py. It uses composition: TaskManager creates and stores Task objects defined in models.py, and persists them via TaskStorage.

High-level flow:

Domain model (data + behavior):

Task, TaskPriority, TaskStatus in models.py
Task has methods like update(), mark_as_done(), is_overdue().
Storage layer:

TaskStorage in storage.py
Reads/writes tasks to JSON, converts enums/datetimes via TaskEncoder/TaskDecoder.
Application/service layer:

TaskManager in app.py
Orchestrates operations: create, list, update, delete, stats by calling TaskStorage and Task.
CLI entry point:

Command-line interface in cli.py
Parses arguments and calls TaskManager.

Take aways - Using Prompt 1

This is a CLI project, CLI (Command Line Interface) is similar to a bash terminal, or like the one found in Kali Linux. Allows the user to interact with the machine at a low level, even though the language in question is a high-level language. From my understanding at least. 


Variations in CLI.py

A large section of the code was made up of a chain of if/elif statements. Which were replaced by a block of helper functions a dispatch dictionary. The dictionary is particularly useful because it can be extended with ease. Making the CLI easier to scale by other developers. 

Take aways - Using Prompt 2

My Personal Understanding:

I tried finding .csv functionality features but they don't seem to exist. So I asked the LLM, if it would even be necessary to add them. The short answer is, unless specified by stakeholders, it is not necessary at all. And since I like to simplify my life, I left things at that.

Co-pilot : 

Short answer: only if stakeholders need CSV (reporting, Excel, integrations). It isn’t required for current JSON persistence.

Best place to add it:

Add export_csv(path) on TaskStorage in storage.py.
Add a TaskManager.export_csv(path) wrapper in app.py.
Wire a new CLI subcommand export in cli.py.
This keeps storage concerns in TaskStorage, business orchestration in TaskManager, and UI/UX in CLI.

Take aways - Using Prompt 3 

My question :
I pretty much asked the LLM, why do we even need to build a task manager CLI. That doesn't seem very user friendly in my personal opinion. From my understanding, this appears to be more of an internal testing tool of sorts. For local workflow development

Co-pilot : 

1. Your understanding is reasonable. The CLI isn’t inherently “user unfriendly”; it’s a common choice for quick internal tools, scripting, automation, and learning exercises. It likely reflects scope, not final UX.

2. Core domain concepts:

Task: unit of work.
TaskStatus: lifecycle state (todo → in_progress → review → done).
TaskPriority: urgency/importance.
Tags: lightweight categorization.
Due dates and completion timestamps.

3. Business relationships:
A task moves through a workflow (status changes) as work progresses.
Priority drives ordering and urgency.
Due dates define time commitments and overdue risk.
Tags group tasks for reporting or focus areas.

4. Domain patterns/terms:
Workflow states (status lifecycle).
SLA/urgency signals (priority, due date).
Completion tracking (completed_at) for reporting.

5. User-facing features mapped to models:
Create task → Task with defaults.
Update status/priority/due date → task workflow and scheduling.
List/Filter/Overdue/Stats → operational reporting and planning.
Tags → categorization for filtering and focus.

Practical Application

Apply auto-abandon logic had to be done across the board, since the CLI as a whole is made up of models, storage, and app.py, all of which are interdepent on one another. 

Not gonna lie, I asked the LLM to add this functionality for me, because this codebase is particularly confusing to me, this doesn't follow the traditional MTV (Model Template View) so its quite tricky for me to decipher which piece of the puzzle fits where and why. Even though I have a rudemenatary understanding of the codebase.



ALGORITHM DECONSTRUCTUION

For this section of the exercises. I pretty much asked the LL, to help me import missing dependencies, because the code did not run when I initially tried to test  it. And then I added this a dictionary above the score checking if-statement code block. So as to make the task of varying score priority in the future, easier to do. 

My addition of code :

 score = priority_weights.get(task.priority, 0) * 10

    heuristic_weights = {
        'OVERDUE': 35,  # Weight for complexity
        'DUE TODAY': 20, 
        'DUE IN A WEEK': 15,     # Weight for impact
        'DUE IN 2 DAYS': 10,     # Negative weight for effort (higher effort reduces score)
    }

    score_array = [heuristic_weights['OVERDUE'], heuristic_weights['DUE TODAY'],
                   heuristic_weights['DUE IN 2 DAYS'], heuristic_weights['DUE IN A WEEK']]

    # Add due date factor (higher score for tasks due sooner)
    if task.due_date:
        days_until_due = (task.due_date - datetime.now()).days
        if days_until_due < 0:  # Overdue tasks
            score += score_array[0]
        elif days_until_due == 0:  # Due today
            score += score_array[1]
        elif days_until_due <= 2:  # Due in next 2 days
            score += score_array[3]
        elif days_until_due <= 7:  # Due in next week
            score += score_array[2]
    # Reduce score for tasks that are completed or in review
    if task.status == TaskStatus.DONE:
        score -= 50
    elif task.status == TaskStatus.REVIEW:
        score -= 15

I then asked the LLM to optimize this section and make it idiomatic 

Co-pilot Optmized Code: 

    due_date_weights = {
        "overdue": 35,
        "today": 20,
        "next_2_days": 15,
        "next_week": 10,
    }

    # Add due date factor (higher score for tasks due sooner)
    if task.due_date:
        days_until_due = (task.due_date - datetime.now()).days
        if days_until_due < 0:  # Overdue tasks
            score += due_date_weights["overdue"]
        elif days_until_due == 0:  # Due today
            score += due_date_weights["today"]
        elif days_until_due <= 2:  # Due in next 2 days
            score += due_date_weights["next_2_days"]
        elif days_until_due <= 7:  # Due in next week
            score += due_date_weights["next_week"]
    # Reduce score for tasks that are completed or in review
    if task.status == TaskStatus.DONE:
        score -= 50
    elif task.status == TaskStatus.REVIEW:
        score -= 15
