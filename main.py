import prettytable
import copy
import time

from schedule import Schedule
from genetic import GeneticOptimize
from common_schedule import CommonSchedule
from common_genetic import CommonGeneticOptimize


def vis(schedule):
    """visualization Class Schedule.

    Arguments:
        schedule: List, Class Schedule
    """
    # col_labels = ['week/slot', '1', '2', '3', '4', '5']
    # table_vals = [[i + 1, '', '', '', '', ''] for i in range(5)]
    col_labels = []
    col_labels.append('week/slot')
    for i in range(Schedule.dayInWeek):
        col_labels.append(i + 1)
    table_vals = []
    for i in range(Schedule.slotInDay):
        row = []
        row.append(i + 1)
        for j in range(Schedule.dayInWeek):
            row.append('')
        table_vals.append(row)
    # table_vals = [[i + 1, '', '', '', '', ''] for i in range(Schedule.slotInDay)]

    table = prettytable.PrettyTable(col_labels, hrules=prettytable.ALL)

    for s in schedule:
        weekDay = s.weekDay
        slot = s.slot
        text = 'course: {} \n class: {} \n room: {} \n teacher: {}'.format(s.courseId, s.classId, s.roomId, s.teacherId)
        table_vals[slot - 1][weekDay] = text

    for row in table_vals:
        table.add_row(row)

    print(table)


def visualizationAll(res):
    className2Schedule = {}
    vis_res = []
    for r in res:
        s = className2Schedule.get(r.classId)
        if s is None:
            s = []
        s.append(r)
        className2Schedule[r.classId] = s

    while len(className2Schedule)>0:
        item = className2Schedule.popitem()[1]
        vis(item)

def visualization():
    # visualization
    className2Schedule = {}
    vis_res = []
    for r in res:
        s = className2Schedule.get(r.classId)
        if s is None:
            s = []
        s.append(r)
        className2Schedule[r.classId] = s
        # if r.classId == 1203:
        #     vis_res.append(r)
    # vis(vis_res)
    vis(className2Schedule.get(2101))
    # vis(className2Schedule.get(1202))
    # vis(className2Schedule.get(1203))



def compareWithSameInit(totalFitness1,totalFitness2):
    global i, res, maxBestFitness1, maxBestFitness2
    for i in range(loopCount):
        # ga.population = origin
        print("?????????")
        commonGA = CommonGeneticOptimize(popSize=popSize, mutprob=0.2, crossProb=0.9, maxiter=500)
        commonGA.init_population(schedules, CommonSchedule.roomRange)
        res, bestFitness1 = commonGA.evolution()
        print("??????????????????" + str(bestFitness1))
        totalFitness1 += bestFitness1
        if bestFitness1 > maxBestFitness1:
            maxBestFitness1 = bestFitness1
        visualizationAll(res)

        print("?????????")
        ga = GeneticOptimize(popSize=popSize, mutprob=0.2, crossProb=0.9, maxiter=500)
        ga.setPopulation(commonGA.getPopulation())
        res2, bestFitness2 = ga.evolution()
        print("??????????????????" + str(bestFitness2))
        totalFitness2 += bestFitness2
        if bestFitness2 > maxBestFitness2:
            maxBestFitness2 = bestFitness2
        visualizationAll(res2)
    return totalFitness1, totalFitness2


def compare():
    totalFitness1=0.0
    totalFitness2=0.0
    maxBestFitness1=0.0
    maxBestFitness2=0.0

    totalTime1=0.0
    totalTime2=0.0
    for i in range(loopCount):
        # ga.population = origin
        # print("?????????")
        # startTime1 = time.time()
        # commonGA = CommonGeneticOptimize(popSize=popSize, mutprob=0.2, crossProb=0.9, maxiter=500)
        # commonGA.init_population(schedules, CommonSchedule.roomRange)
        # res, bestFitness1 = commonGA.evolution()
        # print("??????????????????" + str(bestFitness1))
        # totalFitness1 += bestFitness1
        # if bestFitness1 > maxBestFitness1:
        #     maxBestFitness1 = bestFitness1
        # endTime1=time.time()
        # wasteTime1=endTime1 - startTime1
        # totalTime1 += wasteTime1
        # print("???" + str(i) + "??????1?????????" + str(wasteTime1))
        # visualizationAll(res)

        print("?????????")
        startTime2 = time.time()
        ga = GeneticOptimize(popSize=popSize, mutprob=0.2, crossProb=0.9, maxiter=500)
        ga.init_population(schedules, CommonSchedule.roomRange)
        res2, bestFitness2 = ga.evolution()
        print("??????????????????" + str(bestFitness2))
        totalFitness2 += bestFitness2
        if bestFitness2 > maxBestFitness2:
            maxBestFitness2 = bestFitness2
        endTime2 = time.time()
        wasteTime2 = endTime2 - startTime2
        totalTime2 += wasteTime2
        print("???" + str(i) + "??????2?????????" + str(wasteTime2))
        visualizationAll(res2)
    return totalFitness1, totalFitness2, maxBestFitness1, maxBestFitness2, totalTime1, totalTime2

maxBestFitness1 = 0.0

maxBestFitness2 = 0.0

if __name__ == '__main__':

    popSize = 5

    schedules = []

    loopCount = 1


    avgFitness1 = 0.0
    totalFitness1 = 0.0


    avgFitness2 = 0.0
    totalFitness2 = 0.0

    # add schedule  ????????????????????????
    ## ?????????????????????5??????????????????6????????????3???????????????????????????3???????????????????????????2??????????????????????????????1???????????????3?????????
    ## 5??????
    ## 6??????
    ## 3?????????3??????3?????????2?????? ???15??????
    ## ????????????2???????????????12?????????  5*14=60?????????

    classCount = 10
    courseCount = 6
    teacherCount = 30

    preTeacherInCourse = teacherCount / courseCount

    for i in range(classCount):  # ??????
        for j in range(courseCount):  # ??????
            classId = 2101 + i
            courseId = 100 + j
            teacherId = 10000 + 10 * j

            teacherId += i % preTeacherInCourse + 1

            if j < 3:  ##???3??????????????????3???
                schedules.append(Schedule(classId, courseId, teacherId))
                schedules.append(Schedule(classId, courseId, teacherId))
                schedules.append(Schedule(classId, courseId, teacherId))
            if j >= 3:
                schedules.append(Schedule(classId, courseId, teacherId))
                schedules.append(Schedule(classId, courseId, teacherId))

    print('???????????????' + str(len(schedules)) + '????????????')

    Schedule.crossRetryMaxCount=len(schedules)
    CommonSchedule.crossRetryMaxCount=len(schedules)

    teacherArray = set()
    for i in schedules:
        teacherArray.add(i.teacherId)

    print('????????????' + str(len(teacherArray)) + '???')
    ## ????????????
    classNameSet = set()

    for item in schedules:
        classNameSet.add(item.classId)

    # totalFitness1, totalFitness2 = compareWithSameInit(totalFitness1,totalFitness2)

    totalFitness1, totalFitness2, maxBestFitness1, maxBestFitness2, totalTime1, totalTime2 = compare()

    print("???????????????????????????" + str(maxBestFitness1))
    print("???????????????????????????" + str(maxBestFitness2))
    print("??????????????????" + str(totalTime1/loopCount))
    print("???????????????????????????" + str(totalFitness1 / loopCount))
    print("???????????????????????????" + str(totalFitness2 / loopCount))
    print("??????????????????" + str(totalTime2/loopCount))
    print('popsize=' + str(popSize))

