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

def visualization(res):
    # visualization
    className2Schedule = {}
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



def compareWithSameInit():
    totalFitness1 = 0.0
    totalFitness2 = 0.0
    maxBestFitness1 = 0.0
    maxBestFitness2 = 0.0

    totalTime1 = 0.0
    totalTime2 = 0.0
    for i in range(loopCount):
        population, maxBestFitness1, totalFitness1, totalTime1 \
            = CommonGaCal(i, maxBestFitness1, totalFitness1,totalTime1)

        maxBestFitness2, totalFitness2, totalTime2\
            = myGaCal(population, i, maxBestFitness2, totalFitness2, totalTime2)
    return totalFitness1, totalFitness2, maxBestFitness1, maxBestFitness2, totalTime1, totalTime2


def myGaCal(population, i, maxBestFitness2, totalFitness2, totalTime2):
    print("改进后")
    startTime2 = time.time()
    ga = GeneticOptimize(popSize=popSize, mutprob=0.2, crossProb=0.9, maxiter=500)
    ga.setPopulation(population)
    res2, bestFitness2 = ga.evolution()
    print("改后适应值：" + str(bestFitness2))
    totalFitness2 += bestFitness2
    if bestFitness2 > maxBestFitness2:
        maxBestFitness2 = bestFitness2
    endTime2 = time.time()
    wasteTime2 = endTime2 - startTime2
    totalTime2 += wasteTime2
    print("第" + str(i) + "次，2耗时：" + str(wasteTime2))
    visualizationAll(res2)
    return maxBestFitness2, totalFitness2, totalTime2


def CommonGaCal(i, maxBestFitness1, totalFitness1, totalTime1):
    print("改进前")
    startTime1 = time.time()
    commonGA = CommonGeneticOptimize(popSize=popSize, mutprob=0.2, crossProb=0.9, maxiter=500)
    commonGA.init_population(schedules, CommonSchedule.roomRange)
    pupulation = copy.deepcopy(commonGA.population)
    res, bestFitness1 = commonGA.evolution()
    print("改前适应值：" + str(bestFitness1))
    totalFitness1 += bestFitness1
    if bestFitness1 > maxBestFitness1:
        maxBestFitness1 = bestFitness1
    endTime1 = time.time()
    wasteTime1 = endTime1 - startTime1
    totalTime1 += wasteTime1
    print("第" + str(i) + "次，1耗时：" + str(wasteTime1))
    visualizationAll(res)
    return pupulation, maxBestFitness1, totalFitness1, totalTime1


def compare():
    totalFitness1=0.0
    totalFitness2=0.0
    maxBestFitness1=0.0
    maxBestFitness2=0.0

    totalTime1=0.0
    totalTime2=0.0
    for i in range(loopCount):
        # print("改进前")
        # startTime1 = time.time()
        # commonGA = CommonGeneticOptimize(popSize=popSize, mutprob=0.2, crossProb=0.9, maxiter=500)
        # commonGA.init_population(schedules, CommonSchedule.roomRange)
        # res, bestFitness1 = commonGA.evolution()
        # print("改前适应值：" + str(bestFitness1))
        # totalFitness1 += bestFitness1
        # if bestFitness1 > maxBestFitness1:
        #     maxBestFitness1 = bestFitness1
        # endTime1=time.time()
        # wasteTime1=endTime1 - startTime1
        # totalTime1 += wasteTime1
        # print("第" + str(i) + "次，1耗时：" + str(wasteTime1))
        # visualizationAll(res)

        print("改进后")
        startTime2 = time.time()
        ga = GeneticOptimize(popSize=popSize, mutprob=0.2, crossProb=0.9, maxiter=500)
        ga.init_population(schedules, Schedule.roomRange)
        res2, bestFitness2 = ga.evolution()
        print("改后适应值：" + str(bestFitness2))
        totalFitness2 += bestFitness2
        if bestFitness2 > maxBestFitness2:
            maxBestFitness2 = bestFitness2
        endTime2 = time.time()
        wasteTime2 = endTime2 - startTime2
        totalTime2 += wasteTime2
        print("第" + str(i) + "次，2耗时：" + str(wasteTime2))
        visualizationAll(res2)
    return totalFitness1, totalFitness2, maxBestFitness1, maxBestFitness2, totalTime1, totalTime2

maxBestFitness1 = 0.0

maxBestFitness2 = 0.0


def init_data():
    # add schedule  课程，班级，老师
    ## 测试数据，一共5个班，每个班6门课，前3个课，每门课每周上3次，第四门课每周上2次，最后两门课一周上1次，每门课3个老师
    ## 5个班
    ## 6门课
    ## 3门课上3次，3门课上2次， 共15次课
    ## 每门课有2个老师，共12个老师  5*14=60次课，
    classCount = 10
    courseCount = 6
    teacherCount = 30
    preTeacherInCourse = teacherCount / courseCount
    for i in range(classCount):  # 班级
        for j in range(courseCount):  # 课程
            classId = 2101 + i
            courseId = 100 + j
            teacherId = 10000 + 10 * j

            teacherId += int(i % preTeacherInCourse + 1)

            if j < 3:  ##前3门课，每周上3次
                schedules.append(Schedule(classId, courseId, teacherId))
                schedules.append(Schedule(classId, courseId, teacherId))
                schedules.append(Schedule(classId, courseId, teacherId))
            if j >= 3:
                schedules.append(Schedule(classId, courseId, teacherId))
                schedules.append(Schedule(classId, courseId, teacherId))
    print('一周一共有' + str(len(schedules)) + '节课要上')
    Schedule.crossRetryMaxCount = len(schedules)
    CommonSchedule.crossRetryMaxCount = len(schedules)
    # 收集老师
    teacherArray = set()
    for i in schedules:
        teacherArray.add(i.teacherId)
    print('不同老师' + str(len(teacherArray)) + '个')
    ## 收集班级
    classNameSet = set()
    for item in schedules:
        classNameSet.add(item.classId)
    print('不同班级' + str(len(classNameSet)) + '个')


if __name__ == '__main__':

    popSize = 20
    loopCount = 5

    schedules = []

    avgFitness1 = 0.0
    totalFitness1 = 0.0
    avgFitness2 = 0.0
    totalFitness2 = 0.0

    init_data()

    # totalFitness1, totalFitness2, maxBestFitness1, maxBestFitness2, totalTime1, totalTime2 = compareWithSameInit()

    totalFitness1, totalFitness2, maxBestFitness1, maxBestFitness2, totalTime1, totalTime2 = compare()

    print("改进前最大适应值：" + str(maxBestFitness1))
    print("改进后最大适应值：" + str(maxBestFitness2))
    print("改进前耗时：" + str(totalTime1/loopCount))
    print("改进前平均适应值：" + str(totalFitness1 / loopCount))
    print("改进后平均适应值：" + str(totalFitness2 / loopCount))
    print("改进后耗时：" + str(totalTime2/loopCount))
    print('popsize=' + str(popSize))

