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

This will be spec'ed later. For now, all tables should be visible.

## Models

User:
    * Google email address (for Google OAuth)
    * first_task_of_this_session_performed_at: timestamp.
    (default: start of time)
    * is_locked: (default: False)

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
    * reference: URL string.
    * transform: JSON.

Annotation:
    * user: foreign key to User row.
    * task: foreign key to Task row.
    * annotated_at: timestamp.
    * task_presentation: "AAB", "ABA", "BBA", or "BAB".
    * annotation: "XXY" or "XYX".
