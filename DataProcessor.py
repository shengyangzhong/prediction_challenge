import fileinput
import string
import datetime
import math
import numpy as np

def partitionDay(times):
    # tries to partition the day into 10 minute periods, of which there are 144 in a day
    partition = np.array([0] * 144)
    # create a discrete representation of the frequency of times throughout the day
    for time in times:
        segment = int(math.floor((6 * time.hour) + (time.minute / 10)))
        partition[segment] = partition[segment] + 1

    return partition

def processFile(fileName):
    dateToData = {}
    for line in fileinput.input(fileName):
        line = line.split()
        # process this line as a date and a time
        localDateInfo = line[0].split("-")
        localDate = datetime.date(int(localDateInfo[0]), int(localDateInfo[1]), int(localDateInfo[2]))
        localTimeInfo = line[1].split(":")
        localTime = datetime.time(int(localTimeInfo[0]), int(localTimeInfo[1]), int(localTimeInfo[2]))

        # put this entry into the dictionary
        if (not dateToData.has_key(localDate)):
            dateToData[localDate] = []

        dateToData[localDate].append(localTime)

    fileinput.close()

    # convert set of specific times to a discrete representation of frequency
    partitionedData = {}
    for day in dateToData.keys():
        partitionedData[day] = partitionDay(dateToData[day])

    return partitionedData

