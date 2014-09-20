Shengyang Zhong - University of Texas at Austin
shengyang.zhong@gmail.com

Overview
--------

I approached this problem not as a programming challenge, but a numerical
analysis problem. It was not enough to generate statistics, but to provide
meaningful insights into what the data represented. Without any detailed
knowledge about the merchant itself, I was inherently handicapped when it came
to producing a single authoritative number about something which I had little
knowledge about. Human users are better informed to draw conclusions from the
data. With that in mind, I created an extensible framework for generating
various different views on the data at hand and creating visualizations to show
trends. The idea is to aid a human to make decisions by providing analysis
instead of simply generating results.

I used python because, although not the fastest, it has excellent numerical
analysis packages. I created a data structure that stored a representation of
the activity for each day, and a framework with which I could quickly create
different approaches. Using matplotlib, I could automatically generate graphs of
what a specific dataset represented. I then try to fit the data using a
polynomial regression. Any dataset can be modeled by a polynomial of sufficient
degree if one is careful of overfitting, and through manual testing, I settled
on a value that produced good fits given the sampling interval of 10 minutes
that I settled on.

I soon realized that I knew very little about what underlying trends were
accounting for the patterns that I seeing. Naive models that simply look at all
days that data exists for or all of the same days of the week could only give a
look at general trends such as peak hours and business hours. The beauty of this
implementation is that adding new perspectives is simply a matter of defining a
different way of looking at the overall dataset. I created a model that looks at
a specific month and day, as well as models that use a rolling window that
includes data from adjacent weeks. These models together account for seasonal
variations like daylight savings time that a more holistic approach would not be
able to see. I then combine the results from these models, and try to determine
which datapoints are the most important. If the historical data for that
specific date is wildly different from the rolling window estimates, then that
indicates that this date is an outlier (such as the case with holidays) and my
system will use this more specific data and disregard the rolling windows.

Each model can analyze the data given to it and will generate a report of what
it thinks represents the trends. Once it finishes analyzing the data, it exposes
a way to pass in times for which it will predict the number of orders for every
10 minutes. The main program is simply a wrapper that ties together the data
parsing mechanism with each individual prediction model, and handles producing
meaningful output to standard out.


Usage
-----

This implementation uses Python 2.7, NumPy, and matplotlib. To run, invoke

    python GenerateAnalysis.py <dataset path> <date> <optional time>

It will generate reports and save them to the same location as where the dataset
is. If an optional time is specified, then it will predict transactions for that
date and time, and mark it in the reports. For example, the following command

    python GenerateAnalysis.py data/merchant_a.txt 2014-06-22 19:00:00

will take in the data for Merchant A and predict the number of orders per 10
minutes for June 22 at 7pm.

It will generate graphs that are scaled the same for each analysis model and
place them in the same directory as the data. Each graph will show a plot of the
data as well as a regressed model. If a specific time was provided, then it will
be marked on the graph.

If a specific time was provided, it will output to the console the predictions
from each model. It will try to produce an intelligent aggregate of this data as
a single numerical value for cases where the only requirement is just a single
number. For more in-depth approaches, users should look through the generated
reports.


Limitations
-----------

The current mechanism to collate the different predictions from each model is
rather crude. If more and more perspectives are added, then it needs to grow in
order to curate the result. Producing tons of output is not particularly
meaningful to someone who just wants to know how many customers to expect, and
simply producing a collection of reports is not a great way to present
information. In that sense, this system needs more work in better combining the
analysis produced in order to create a system that provides simple, meaningful
output.

This implementation is very much unoptimized, and in many circumstances, I opted
for code that was quick to implement but not necessarily fast. There is a lot of
work duplicated, but the goal here was to produce a working prototype.

I acknowledge that I do not have a lot of background in statistical analysis,
and so my system was designed to be easily modified if someone else was to want
to implement a better way of predicting trends. All the different models use the
same underlying infrastructure, and only have to provide a way of selecting
datapoints that it thinks is relevant.
