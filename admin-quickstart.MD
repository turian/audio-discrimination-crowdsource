# Admin Quick Start
Admin users on this software have total control over everything that happens on the software, these includes:
- Creation of experiments
- Data management
- User Locking
- User data management
- Batch creation
To mention just few, before an account can be an admin account, the account needs to have the `is_staff` permission from a superuser.

## Understanding Experiments

Experiments are the most basic part of the application and currently, the software can support two types of experiments, namely:
- A/B Experiments
- 2AFC Experiments

### A/B experiment type
A/B test (experiment type) this is to check if A or B is better. I might have an experiment named "add salt" experiment and then I give annotators two dishes, A and B but I didn't tell them one has more salt and the experiment is to see which one they like better. That's an A/B test.

### 2AFC experiment type
2AFC test (experiment type) this for example is that I give you four dishes, three don't have salt (denoted by "A") [i.e saltless dishes are experiment type A], and the last dish has salt (denoted by "B") [i.e, salted dishes are of experiment type B]. 
I can give the dishes to you in any of these order: "AAB", "ABA", "BBA", "BAB". I didn't explain to you that I added salt or not and the aim of my experiment is determine how much salt you can detect. Maybe under 1g of salt you cannot taste anymore. 
If you answer "XXY", which means that you think the first and second dish are the same and the third is different, or you answer "XYX" which means that you think the first and third dish are the same and the second one is different, through this, I can determine if you really can sense salt in a dish or not.

Thus an A/B test is for determining what people prefer and what would likely be welcomed by them and 2AFC test is for determining what people can sense, dectect or perceive.

However, once you decide to do A/B test in order to create the tastiest dish, you might have your experiment named "salt experiment", "sugar experiment" e.t.c. The same thing applies to 2AFC when determining people's sensitivity.

The above explanation should have give you the clear picture on what A/B and 2AFC means as experiment types.

## Creating Experiment

In order to have any test, admin needs to have create experiments first, if you're an admin user, there is a sidebar to the left of the page with some links to perform different admin tasks.
Click on the link that reads, `Create Experiment`, you should get a page with two input forms the first one to select experiment type, click on it and select either of the two supported experiment types, 2AFC or A/B experiment types.

After selecting an experiment type that suite your case, give your experiment a clear name (please note that experiments name must be unique, no two experiments can have the same name), click the `create experiment` button and you should get a success, indicating that experiment is successfully created.

Screenshot of the `Create experiment` page:


![Screenshot 2023-03-10 232234](https://user-images.githubusercontent.com/68183305/224440437-5101eaa3-119c-4a04-a7fe-ace8f0490866.png)


## Understanding Batch
This software is structured in such a way that after creating experiments, you obviously needs to create a related `Tasks`, but all tasks are tied to a `Batch`, i.e you create tasks in batches.
At times there is need to know if your annotators are actually doing their job or just selecting randomly, so there is room for creation of tow types of batches, namely:
- Batch type Gold
- Batch type Eval

### Batch type Gold
Here, the tasks presented under the batch are tasks where the batch creator already know which audio is "edited" and which is "not edited", so the tasks are presented as normal to annotators and with this, admin can easuly know if they're actually listening or just picking randomely.
Gold tasks descrribe annotators quality and with it it's easy to predict if the annotator would work excellently or not. also, there is chance or admin to make a batch gold even after creating it as Eval.

### Batch type Eval
This type of batch are where real tasks are presented for annotators evaluation, we present all the tasks under the batch and we can know which is better only from annotators responses.

## Batch creation
After creating experiment, the next thing is to get tasks related to the experiment ready, but all tasks area tied to a particular `Batch`, all batch can have multiple tasks and all tasks has just a single Batch.
In order to create a batch of tasks, admin must have determine the batch `name`, if the batch `is gold`, or not, and also a small `note`. And all tasks data which includes `transform_url`, `reference_url` and `transform_metadata` all this data must be formated in JSON.
If admin did not specify if a batch is Gold or not, it would be assumed Eval, and if note is not given it would be assumed none, for tasks, if transform metadata is not given it would be assumed None as well.
Having all this in mind, this is the accepted way of formating the JSON file, read the comments to understand the details and how it's formated:

```
{
    "name": "salt-line batch", // signifying batch name
    "is_gold": true,   // signifies if batch is gold or not
    "notes": "This is a sample JSON data",  // any note at all or None would be supplied
    "tasks": [ // List of tasks go in here
        { # task 1
            "reference_url": "https://www.example.com/reference",
            "transform_url": "https://www.example.com/transform",
            "transform_metadata": {
                "key1": "value1",
                "key2": "value2"
            }
        }, // end of task 1
        { // Task 2, with example of cases where transform_metadata is not supplied
            "reference_url": "https://www.example.com/reference2",
            "transform_url": "https://www.example.com/transform2"
        } // end of task 2
    ] // end tasks list
}
```

In order to create a batch after understanding all this, click on the `batch submit` in the admin side panel and let it load, there are two available inputs in the form, the first one allows you to select an experiment you're creating a batch for and the second allows you to paste your JSON data.

A screenshot of the `Batch Submit` Page:

![Screenshot 2023-03-10 232536](https://user-images.githubusercontent.com/68183305/224440548-dd3b57b8-07ab-432a-a1bc-fad5306c2097.png)


If Batch creation is succesful, you should be redirected to `Admin Dashboard` where a table is presented under each available experiment showing the experimet's Batches, also, the you can toggle between the two batch values by clicking on the True or False value that appears at the `Is Gold` column of each experiments.


## Admin Dashboard

Admin user can reach this page through the sidebar, by clicking on Dashboard tab, or when an admin successfully submit a `Batch`, this page is used to display all experiments created in the database and for each experiment, there is a table below it that displays all batches created under the experiment.
Items on the table includes `Batch ID` which is the identity number of each batch in the database, `Created at`, time stamp showing when each experiment was created, `Name` a unique name given to each batch and this displays None, if no name is attached to the batch, `is gold` this column displays True or False for each batch, True shows that the batch is `Batch type Gold` and False shows that the batch is `Batch type Eval`.
You can toggle between the two values for a batch by clicking on the True or False value displayed in the batch's column, and you'll be prompt with a confirmation message to know if you really want to switch the batch type.

Screenshot of `Admin Dashboard` page:

![Screenshot 2023-03-10 164659](https://user-images.githubusercontent.com/68183305/224489418-ebd4b57e-f335-4949-9a97-f1ac0488878d.png)


## Admin Experiment

Admin can reach this page only by clicking on any of the available experiments in the Admin Dashboard page, by clicking on the experiment name displayed in blue, admin would be redirected to `Experiment View` page.
On this page, details about experiments are displayed, primarily, these details are grouped in batches, and `Batch type Gold` are prioritized in sorting the batch.
For each batch, details about tasks created under it is displayed and this includes `Task id`, which is the unique identification number of that task, `# of Annotations` this shows the number of time annotation has been done on the task, `% of Annotations` which shows percentage of annotations done on the task, `reference url` which is the url of the original audio presented for annotation, `transform url` which is the url of the edited/custom audio annotators are experimenting on, `trasform json` also known as transform metadata in the batch creation JSON.
Experiment name and Experiment type is displayed at the top of the page as well, and this is all about the `Admin Experiment Detail` page.

Screenshot of `Admin Experiment` page:

![Screenshot 2023-03-10 164255](https://user-images.githubusercontent.com/68183305/224489370-8a020c9d-c4be-4043-a4ff-e5e7e0dcb6cf.png)


## Admin User Management

The most essential part of this application is the annotators and how good they're doing on the platform must be accounted for, so as to know their quality score through Gold tasks and use it to evaluate their overall quality.
On this page, admin users have the priviledge to manage and preside over all Annotators as the page displays details of only non admin users, meaning annotators details only.
Data displayed on this page are presented in a table with several column where each annotator on owns a row and the annotator data is presented through each column.
Columns on the table includes, `Annotator` which is the primary name of an annotator, `Email` annotator email address, `Number of tasks completed` showing the computation of all tasks the annotator has completed on the platform, `Percentage of gold` showing the percentage of the completed task that is off Gold batch, `ROI` total worth of work an annotator has done on the platform.
The last two column on the page are special  columns, `Lock` would lock a user outside the platform if clicked by an Admin user, the lock restriction is normally used on annotators with lower quality, and any annotator locked would not be able to perform any task on the platform again.
Last column on the table reads `Delete` on confirmation that you really want to delete the users data after clicking delete on any user column, all tasks undergone by the user would be deleted off the database and the user would also be locked out of the platform immediately, this is a feature that can not be undone, so be careful while using it.

Screenshot of `Admin User Management` page:

![Screenshot 2023-03-10 152102](https://user-images.githubusercontent.com/68183305/224490459-d5e0e649-8588-48a0-ba78-acd70ed6cfea.png)
