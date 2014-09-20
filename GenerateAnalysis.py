#! usr/bin/python

import sys
import math
import matplotlib
# turn off GUI front-end for matplotlib
matplotlib.use("pdf")

import matplotlib.pyplot as pyplot
import numpy as np
import abc
import datetime
import os

import warnings
# ignore warnings on possibly ill-fitting polynomials
warnings.filterwarnings('ignore')

import DataProcessor

class Analysis:

    @abc.abstractmethod
    def chooseDates(self, data, specifiedDate):
        pass

    @staticmethod
    def findHistoricalWeekdays(data, startingDate):
        weekdays = [startingDate]
        # finds one more year than exists in the dataset for checking windows around this data
        # does not work well when specified date is nowhere near the dataset

        years = datetime.timedelta(days = 365)
        days = datetime.timedelta(days = 1)
        yearsAway = 1
        lookaround = 3;
        while (lookaround > 0):
            current = startingDate + yearsAway * years
            yearsAway = yearsAway + 1;

            # make sure that this day is on the same weekday as the starting date
            current = current + (startingDate.weekday() - current.weekday()) * days
            weekdays.append(current)
            if (not data.has_key(current)):
                lookaround = lookaround - 1

        yearsAway = 1
        lookaround = 3;
        while (lookaround > 0):
            current = startingDate - yearsAway * years
            yearsAway = yearsAway + 1;

            # make sure that this day is on the same weekday as the starting date
            current = current + (startingDate.weekday() - current.weekday()) * days
            weekdays.append(current)
            if (not data.has_key(current)):
                lookaround = lookaround - 1

        return weekdays

    def predict(self, time):
        # uses polynomial fit data from analyze to predict for a given time
        time = time.hour + (time.minute / 60.0)
        return np.polyval(self.regression, time)

    def analyze(self, filepath, data, dataMax, specifiedDate, specifiedTime = None):
        # uses the date selection criteria of this class to analyze the dataset

        # create an x-axis of interval 10 minutes
        x = map(lambda x: x / 6.0,np.arange(0,144))
        y1 = np.array([0] * 144)

        daysCounted = 0.0
        workingData = self.chooseDates(data, specifiedDate)
        # sum together the values of all the datapoints
        for d in workingData:
            # numpy arrays add elment-wise
            y1 = y1 + np.array(dataMap[d])
            daysCounted = daysCounted + 1;

        # find the average
        y1 = map(lambda y: (y / daysCounted), y1)
        # try to find some polynomial fit
        regression = np.polyfit(x, y1, 20)
        y2 = np.polyval(regression, x)

        pyplot.plot(x, y1, "ko", x, y2, "k--")
        # plot the estimated value for the specified time, if applicable
        if (specifiedTime == None):
            pass
        else:
            timeVal = int(math.floor((6 * specifiedTime.hour) + (specifiedTime.minute / 10)))
            estX = timeVal / 6.0
            estY = np.polyval(regression, estX)
            pyplot.plot(estX, estY, color = "r", marker = "+", markersize = 20.0)
            pyplot.plot(estX, estY, color = "r", marker = "x", markersize = 20.0)

        # setup the rest of the graph
        pyplot.title(self.title + " (date: " + str(specifiedDate) + " datapoints: " + str(len(workingData)) + ")", fontsize = 16)
        pyplot.xlabel("Time (hours)", fontsize = 12)
        pyplot.xticks(np.arange(0, 25, 1))
        pyplot.ylabel("Orders (per 10 minutes)", fontsize = 12)
        pyplot.axis([0, 24, 0, dataMax + 1])

        # save the graph
        filename = filepath + self.name + ".pdf"
        pyplot.savefig(filename)
        pyplot.clf()

        self.yData = y1
        self.regression = regression
        return self.yData



class AllDays(Analysis):

    def __init__(self):
        self.title = "All days"
        self.name = "_all_days"

    def chooseDates(self, data, specifiedDate):
        return dataMap.keys()



class AllWeekdays(Analysis):

    def __init__(self):
        self.title = "All weekdays"
        self.name = "_all_weekdays"

    def chooseDates(self, data, specifiedDate):
        return [day for day in dataMap.keys() if day.weekday() == specifiedDate.weekday()]



class ThisDate(Analysis):

    def __init__(self):
        self.title = "This Date Historical"
        self.name = "_this_date"

    def chooseDates(self, data, specifiedDate):
        return [day for day in dataMap.keys() if (day.month == specifiedDate.month and day.day == specifiedDate.day)]



class Rolling2Week(Analysis):

    def __init__(self):
        self.title = "2 Week Rolling"
        self.name = "_rolling_2week"

    def chooseDates(self, data, specifiedDate):
        week = datetime.timedelta(days = 7)
        days = Analysis.findHistoricalWeekdays(data, specifiedDate)
        # extends to 2 week behind and ahead of these days
        days = map(lambda x: x - 2 * week, days) + map(lambda x: x - week, days) + days + map(lambda x: x + week, days) + map(lambda x: x + 2 * week, days)
        # return only the ones in the dataset
        return [day for day in days if (data.has_key(day))]



class Rolling1Month(Analysis):

    def __init__(self):
        self.title = "1 Month Rolling"
        self.name = "_rolling_1month"

    def chooseDates(self, data, specifiedDate):
        week = datetime.timedelta(days = 7)
        days = Analysis.findHistoricalWeekdays(data, specifiedDate)
        # extends to 1 month behind and ahead of these days
        # grabs [-3, 0, 3], then adds [-4, -1, 2] and [-2, 1, 4]
        days = map(lambda x: x - 3 * week, days) + days + map(lambda x: x + 3 * week, days)
        days = map(lambda x: x - 1 * week, days) + days + map(lambda x: x + 1 * week, days)
        # return only the ones in the dataset
        return [day for day in days if (data.has_key(day))]



if __name__ == "__main__":
    formatter = "{0:.2f}"

    print("Processing file " + sys.argv[1] + " for " + sys.argv[2])
    dataMap = DataProcessor.processFile(sys.argv[1])
    # find the rational uper bound on graphs
    dataMax = 0
    for values in dataMap.values():
        p = np.percentile(values, 90)
        dataMax = max(dataMax, p)

    givenDate = sys.argv[2].split("-")
    givenDate = datetime.date(int(givenDate[0]), int(givenDate[1]), int(givenDate[2]))

    givenTime = None
    if (len(sys.argv) >= 4):
        givenTime = sys.argv[3].split(":")
        givenTime = datetime.time(int(givenTime[0]), int(givenTime[1]), int(givenTime[2]))

    # grabs the filepath
    filepath = os.path.splitext(sys.argv[1])[0]

    """
    # don't use these; they're terrible predictors
    allDays = AllDays()
    allDays.analyze(filepath, dataMap, dataMax, givenDate, givenTime)
    print(allDays.title + " predicts " + formatter.format(allDays.predict(givenTime)) + " orders every 10 minutes")

    allWeekdays = AllWeekdays()
    allWeekdays.analyze(filepath, dataMap, dataMax, givenDate, givenTime)
    print(allWeekdays.title + " predicts " + formatter.format(allWeekdays.predict(givenTime)) + " orders every 10 minutes")
    """

    thisDate = ThisDate()
    thisDate.analyze(filepath, dataMap, dataMax, givenDate, givenTime)
    if (not givenTime == None):
        print(thisDate.title + " predicts " + formatter.format(thisDate.predict(givenTime)) + " orders every 10 minutes")

    rolling2W = Rolling2Week()
    rolling2W.analyze(filepath, dataMap, dataMax, givenDate, givenTime)
    if (not givenTime == None):
        print(rolling2W.title + " predicts " + formatter.format(rolling2W.predict(givenTime)) + " orders every 10 minutes")

    rolling1M = Rolling1Month()
    rolling1M.analyze(filepath, dataMap, dataMax, givenDate, givenTime)
    if (not givenTime == None):
        print(rolling1M.title + " predicts " + formatter.format(rolling1M.predict(givenTime)) + " orders every 10 minutes")

    if (not givenTime == None):
        predictedData = [thisDate.predict(givenTime), rolling2W.predict(givenTime), rolling1M.predict(givenTime)]
        aggregate = np.mean(predictedData)
        # determine if the historical data for this day is very different from neighboring weekdays
        rollingMean = np.mean(predictedData[1:])
        rollingDiff = (np.absolute((predictedData[0] - rollingMean) / predictedData[0]) + np.absolute((predictedData[0] - rollingMean) / rollingMean)) * 100.0 / 2.0

        # handle if the date does not hit good data
        if np.isnan(predictedData[0]):
            if np.isnan(predictedData[1]):
                if np.isnan(predictedData[2]):
                    # well, there's nothing to do now
                    print("No meaningful data exists for this date")
                else:
                    # the monthly data is all that exists
                    print("Aggregate prediction: " + formatter.format(predictedData[2]))

            else:
                # use the rolling mean data
                print("Aggregate prediction: " + formatter.format(rollingMean))

        else:
            print("Historical data is " + formatter.format(rollingDiff) + "% different from rolling prediction")

            if rollingDiff > 40:
                # just use historical data, because the difference is so large
                print("Aggregate prediction: " + formatter.format(predictedData[0]))
            else:
                # use aggregate data for smoother predictions
                print("Aggregate prediction: " + formatter.format(aggregate))
