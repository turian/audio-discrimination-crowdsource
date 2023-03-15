# Technical Spec

Note that we expect no more than 10 simultaneous users. This app
will never require scalability, so don't optimize for scale.

We should use HTMX not JS.

## Experiment Types

There are currently two types of experiments. The first (2AFC) was
the one originally spec'ed.

* 2AFC
* A/B

For a particular experiment *type*, there might be multiple experiments with different *names*.

Each experiment has a separate landing page.


## A/B experiment type
A/B test (experiment type) is A or B is better. I might have a "add salt" experiment and then I give annotators dishes A and B but I don't tell them one has more salt and I see which they like better. That's an A/B test.

## 2AFC experiment type
2AFC test is I give you four dishes. Three don't have salt (A) and one has salt (B). I give you them like this "AAB", "ABA", "BBA", "BAB". I don't explain to you that I'm adding salt. I am experimenting to see how much salt you can detect. Maybe under 1g of salt you cannot taste anymore. You answer "XXY",, which means that you think the first and second dish are the same and the third is different, or you answer "XYX" which means that you think the first and third dish are the same and the second one is different.

Thus an A/B test is for determining what people prefer and 2AFC test is for determining what people can sense or perceive.

However, once you decide to do A/B test in order to create the tastiest dish, you might have "salt experiment", "sugar experiment" e.t.c. The same thing applies to 2AFC when determining people's sensitivity.

### How the tie up with ExperimentTypeTaskPresentation and ExperimentTypeAnnotation?

For every task we need to know how will this task be presented(task presentations) and what options will the user have(annotations). Every task is associated with an Experiment and every Experiment has an ExperimentType. We can get the task presentations for a specific task from ExperimentTypeTaskPresentation and annotations from ExperimentTypeAnnotation via experiment.

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

For the chosen task, call `present_task_for_user(task, experiment_name)`
(or `experiment_id`). This method will be written by the lead dev,
but should be mocked for now. It will return a URL to an mp3 and
`task_presentation`.

The task has a template which has static text, a JS player for the
mp3, and a radio form with options based upon the experiment type
annnotations. The User chooses one of the two options and clicks
submit. An Annotation row is written to the database and the User
Task Workflow begins again.

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
Just the typical default Django admin functionality.

### Admin User View

There is a table of annotators.

There is a field to add their hourly rate as a float. (This should be added to the User model.)

The columns are: email, experiment name, number of tasks completed, percent of gold correct, interannotator agreement, ROI, lock, delete

* Number of tasks completed is the number of tasks in that experiment they did, including gold.
* Percent of gold correct: What percent of gold tasks did they get correct
* Interannotator agreement: Leave this blank for now, I'll spec it later.
* ROI: Compute the number of hours they worked on this experiment. (We might need to consider adding a Sessions table to track this.) ROI = # tasks completed / (# hours * hourly rate)
* lock: A boolean checkbox allowing me to lock the user, because they were slow.
* delete: A boolean checkbox allowing me to lock the user AND delete all their annotations from the database, because they were low quality. (Delete is permanent. I will typically use lock. But if someone just comes and clicks buttons randomly, it affects the interannotator agreement and makes all the statistics weird, and I just want to remove them entirely and all their work.)

Locked annotators are grayed out.
A button should allow me lock all selected users.

### Admin Experiment View

Show experiment name and experiment type.

Organized in batches. Show latest first. Show gold first.

Each batch table:
* task ID, # annotations, annotations %, reference_url, transform_url, transform_JSON

Annotations % should be blank now. It's a formula computed differently
for each experiment. I'll spec this when I spec the second experiment.

(Later: We might want to have functionality that does not give a user a task if K=3 people have already annotated it. K should be adjustable per experiment.)

### Admin Batch Submit View

To be spec'ed. A way for the admin to add new batches by uploading a CSV.

### Admin TODO

One thing that is missing and maybe I'll spec later is the ability to measure annotator fatigue. i.e. if 15 minutes is too long or too short. How long does the typical person take to get ear fatigue? Alternately I might just do annotation myself and see.

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
    * experiment_type: FK to ExperimentType.

Annotation:
    * user: foreign key to User row.
    * task: foreign key to Task row.
    * annotated_at: timestamp.
    * task_presentation: string.
        Database must verify constraint that task_presentation is in task.experiment_type.task_presentation
    * annotation: string.
        Database must verify constraint that task_presentation is in task.experiment_type.annotations

This table is a fixture.
Experiment:
    * name: string (unique)
    * type: FK to ExperimentType

ExperimentType:
    * type: string (unique)
        2AFC or A/B

This table is a fixture.
ExperimentTypeTaskPresentation:
    * FK to ExperimentType
    * task_presentation: string
For 2AFC: "AAB", "ABA", "BBA", "BAB".
For A/B: "AB", "BA".

ExperimentTypeAnnotation:
    * FK to ExperimentType
    * annotation: string
For 2AFC: "XXY", "XYX".
For 2AFC: "X", "Y".
Note: Future experiment types might have more than two options.

(Alternately, annotation and task_presentation could be Lists in
ExperimentType if it makes it easier to code the constraints in
Annotation. Thoughts? Speed is not important, code simplicity and
lack of bugs is.)