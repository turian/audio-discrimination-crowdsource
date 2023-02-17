# Technical Spec

Note that we expect no more than 10 simultaneous users. This app
will never require scalability, so don't optimize for scale.

## Workflows

### User Auth Workflow

When the user is not authed, they land on an unauthenticated page
and can use Google OAuth to log in.

When the user is authed:

If `user.is_locked`, they are given a screen that says: "Thank you
for contributing." and can do no more work.

Else if first_task_of_this_session_performed_at is over 15 minutes
ago, and under 75 minutes ago, they are given a screen that says:
"Please rest your ears and return in [X] minutes." and cannot do
work at this time.

Else if first_task_of_this_session_performed_at is over 75 minutes
ago, the user is presented with a welcome web-page. (Text for this
web-page will be provided.) When they click the text: "Begin work"
at the end of this page, first_task_of_this_session_performed_at
is set to now and they are dropped into the User Task Workflow.

Else they are dropped into the User Task Workflow.

(In this way, users are allowed to work for 15 minutes and then
must pause for 60 minutes before resuming work.)

### User Task Workflow

Users are given one task per web-page as described below.

One task is selected. Each task takes under 20 seconds to complete.
When the user submits their answer, their time clock is checked as
described above and---if they can do more work---this workflow
repeats with a new task web-page (loops).

There is a 10% chance that a "gold" task is selected. ("gold" tasks
are ones in which we know the correct annotation. There is a batch
workflow that determines if users are providing poor annotations,
in which case the user will be locked from doing more work.)
Randomly select a task where `task.batch == current_batch_gold` and
there is no Annotation for `(user, task)`.

Otherwise (90% chance), randomly select a task where `task.batch
== current_batch_eval` and there is no Annotation for `(user, task)`.

(If there are no tasks left in this batch for the user to annotate,
present a screen that says: "Come back later for more work.")

For the chosen task, call `present_task_for_user(task)`. This method
will be written by the lead dev, but should be mocked for now. It
will return a URL to an mp3 and `task_presentation` ("AAB", "ABA",
"BBA", or "BAB").

The task has a template which has static text, a JS player for the
mp3, and a radio form with two options: "XXY" or "XYX". The User
chooses one of the two options and clicks submit. An Annotation row
is written to the database and the User Task Workflow begins again.

### Batch Admin Jobs

There are certain admin workflows which are done in batch. These
will be implemented by the lead dev. They might need to be mocked
for now:

* User lock batch job: The annotations are read and users that are
performing too poorly are locked.

* Create tasks batch job: One Batch row and many Task rows (with
this Batch) are written to the database. Either
`CurrentBatch.current_batch_gold` or `CurrentBatch.current_batch_eval`
with this Batch are written to the database.

## Admin Dashboard

There are a list of different experiments. (In the first version, we will only have one experiment.) If you click on one, you go to the Admin Experiment View.
There is a link to the Admin User View.

There should be a simple link or something that allows me to view all raw tables.

### Admin User View

There is a table of annotators.

There is a field to add their hourly rate as a float. (This should be added to the User model.)

The columns are: email, experiment name, number of tasks completed, percent of gold correct, interannotator agreement, ROI, lock?, delete?

* Number of tasks completed is the number of tasks in that experiment they did, including gold.
* Percent of gold correct: What percent of gold tasks did they get correct
* Interannotator agreement: Leave this blank for now, I'll spec it later.
* ROI: Compute the number of hours they worked on this experiment. (We might need to consider adding a Sessions table to track this.) ROI = # tasks completed / (# hours * hourly rate)
* lock?: A boolean checkbox allowing me to lock the user, because they were slow.
* delete?: A boolean checkbox allowing me to lock the user AND delete all their annotations from the database, because they were low quality.

Locked annotators are grayed out.
A button should allow me lock all selected users.

### Admin Experiment View

Show experiment name.

Organized in batches. Show latest first. Show gold first.

Each batch table:
* task ID, # annotations, annotations %, reference_url, transform_url, transform_JSON

Annotations % should be blank now. It's a formula computed differently
for each experiment. I'll spec this when I spec the second experiment.

(Later: We might want to have functionality that does not give a user a task if K=3 people have already annotated it. K should be adjustable per experiment.)

## Models

User:
    * Google email address (for Google OAuth)
    * first_task_of_this_session_performed_at: timestamp.
    (default: start of time)
    * is_locked: (default: False)
    * hourly_rate: float (default: None)

Batch:
    * created_at: timestamp.
    * is_gold: boolean.
    * notes: text.

CurrentBatch:
    This is not really a table of rows. It is just two global
    variables for the app.
    * current_batch_gold: foreign key to Batch row.
    * current_batch_eval: foreign key to Batch row.

Task:
    * batch: foreign key to Batch row.
    * reference_url: URL string.
    * transform_url: URL string.
    * transform_metadata: JSON.

Annotation:
    * user: foreign key to User row.
    * task: foreign key to Task row.
    * annotated_at: timestamp.
    * task_presentation: "AAB", "ABA", "BBA", or "BAB".
    * annotation: "XXY" or "XYX".
