import numpy as np

"""
    课程类
"""


class Schedule:
    ## 一周上几天课
    dayInWeek = 6
    ## 每天有几个可排课时间段
    slotInDay = 5
    ## 教室个数
    roomRange = 20
    ## finess k
    k = 1

    ## 交叉后冲突最大重试次数
    crossRetryMaxCount = 20

    ## 变异后出现冲突最大重试次数
    mutateRetryMaxCount = 40

    className = 'class'

    roomName = 'room'

    teacherName = 'teacher'

    """Class Schedule.
        classId:  班级ID
        courseId: 课程ID
        teacherId: 老师ID
    """

    def __init__(self, classId, courseId, teacherId):
        """Init
        Arguments:
            courseId: int, unique course id.
            classId: int, unique class id.
            teacherId: int, unique teacher id.
        """
        self.courseId = courseId
        self.classId = classId
        self.teacherId = teacherId

        self.roomId = 0
        self.weekDay = 0
        self.slot = 0

    def random_init(self, roomRange):
        """random init.

        Arguments:
            roomSize: int, number of classrooms.
        """
        self.roomId = np.random.randint(1, 1 + Schedule.roomRange, 1)[0]
        self.weekDay = np.random.randint(1, 1 + Schedule.dayInWeek, 1)[0]
        self.slot = np.random.randint(1, 1 + Schedule.slotInDay, 1)[0]
        # self.roomId = np.random.randint(1, roomRange + 1, 1)[0]
        # self.weekDay = np.random.randint(1, 6, 1)[0]
        # self.slot = np.random.randint(1, 6, 1)[0]


def f1(p):
    classCourse2TimeTable = {}
    for e in p:
        key = str(e.classId) + '#' + str(e.courseId)
        s = classCourse2TimeTable.get(key)
        if s is None:
            s = []
        s.append(e)
        classCourse2TimeTable[key] = s

    count = 0
    sum = 0.0
    while len(classCourse2TimeTable) > 0:
        item = classCourse2TimeTable.popitem()
        groupCourseArray = item[1]
        weekArray = [it.weekDay for it in groupCourseArray]
        slotArray = [it.slot for it in groupCourseArray]
        pre = None
        # 先排周，再排节次
        soredArrayIndex = np.lexsort((slotArray, weekArray))
        for i in soredArrayIndex:
            now = groupCourseArray[i]
            if pre is None:
                sum += 1
            else:
                gap = (now.weekDay - pre.weekDay) * Schedule.slotInDay + now.slot - pre.slot
                sum += gapScore(gap)
            count += 1
            pre = now
    return sum / count


_1set = set([8, 9, 10])
_8set = set([6, 7, 11, 12, 13, 14])
_6set = set([5, 15, 16, 17, 18])
_4set = set([3, 4, 19, 20, 21, 22])
_2set = set([1, 2, 23, 24, 25, 26, 27, 28, 29])

_courseScore = [
    [0.97, 0.9, 0.73, 0.53, 0.33],
    [0.98, 0.95, 0.75, 0.59, 0.31],
    [0.95, 0.89, 0.71, 0.52, 0.36],
    [0.94, 0.87, 0.7, 0.54, 0.37],
    [0.92, 0.84, 0.63, 0.52, 0.31],
    [0.82, 0.76, 0.53, 0.42, 0.22]
]


def max_minNorm(arr):
    arr = np.array(arr)
    x_max = arr.max()  # 数组元素中的最大值
    x_min = arr.min()  # 数组元素中的最小值
    x_mean = arr.mean()
    base = x_mean / len(arr)
    m = x_max - x_min
    if m == 0:
        m = base
    arr = np.around(((arr - x_min + base) / m), decimals=4)
    return arr

def gapScore(gap):
    if gap == 0:
        return 0
    if gap in _1set:
        return 1
    elif gap in _8set:
        return 0.8
    elif gap in _6set:
        return 0.6
    elif gap in _4set:
        return 0.4
    elif gap in _2set:
        return 0.2


def f2(p):
    allRoomSet = set()
    allRoomCount = 0
    for i in p:
        allRoomCount += 1
        allRoomSet.add(i.roomId)
    return allRoomCount / len(allRoomSet)


def f3(p):
    dayCount = 0
    allCount = 0
    for i in p:
        if i.slot < 5:
            dayCount += 1
        allCount += 1
    return dayCount / allCount


# 计算每个班级白天课占当天课的比例,并计算这个比例的平均值，然后计算这个比例序列的方差，然后用平均值/方差
def f32(p):
    # 每个班级白天课占的比率
    classDayRatio = []
    # 每个班中白天课和总课数
    class2DayCountAndAllCount = {}
    for i in p:
        dayCountAndAllCount = class2DayCountAndAllCount.get(i.classId)
        if dayCountAndAllCount is None:
            dayCountAndAllCount = [0, 0]

        dayCountAndAllCount[1] += 1
        if i.slot < 5:
            dayCountAndAllCount[0] += 1

        class2DayCountAndAllCount[i.classId] = dayCountAndAllCount

    while len(class2DayCountAndAllCount) > 0:
        item = class2DayCountAndAllCount.popitem()[1]
        classDayRatio.append(item[0] / item[1])

    mean = np.mean(classDayRatio)
    var = np.var(classDayRatio)

    return mean / var


def f4(p):
    totalScore = 0.0
    for i in p:
        totalScore += _courseScore[i.weekDay - 1][i.slot - 1]
    return totalScore / 100


def fitness(p):
    """ calculate fitness score

    Arguments:
        p: List, single schedules.

    Returns:
        finess score
    """

    # 计算学生接受程度
    s1 = f1(p)
    # 计算教室利用率
    s2 = f2(p) / (Schedule.dayInWeek * Schedule.slotInDay)
    # 计算自习模型
    s3 = f3(p)
    # 节次最优模型
    s4 = f4(p)
    # score= (k1 * s1 + k2 * s2 + k3 * s3 + k4 * s4) * CommonSchedule.k
    # print('s:{} | s1:{} | s2:{} | s3:{} | s4:{}'.format(score,s1, s2, s3,s4))
    return s1, s2, s3, s4
    # return score


def fitness2(p):
    """ calculate fitness score

    Arguments:
        p: List, single schedules.

    Returns:
        finess score
    """

    # 计算学生接受程度
    s1 = f1(p)
    # 计算教室利用率
    s2 = f2(p) / (Schedule.dayInWeek * Schedule.slotInDay)
    # 计算自习模型
    s3 = f3(p)
    # 节次最优模型
    s4 = f4(p)
    score = (k1 * s1 + k2 * s2 + k3 * s3 + k4 * s4) * Schedule.k
    # print('s:{} | s1:{} | s2:{} | s3:{} | s4:{}'.format(score,s1, s2, s3,s4))
    return score


k1 = 400
k2 = 100
k3 = 100
k4 = 400


def conflict(p):
    n = len(p)
    conflictCount = 0

    ## 已使用的插槽 set结构 (weekDay,slot,'room'或'class'或'teacher',roomId/classId/teacherId)
    usedSpace = set()

    ## 已冲突的插槽 keyValue结构 key=(weekDay,slot,'room'或'class'或'teacher'或'count')   value=set(i,j,k....)
    space2Conflict = {}

    for i in range(0, n - 1):
        for j in range(i + 1, n):
            addToUsedSet(p[i], usedSpace)
            addToUsedSet(p[j], usedSpace)
            if p[i].weekDay == p[j].weekDay and p[i].slot == p[j].slot:
                # usedSpace.add((p[i].weekDay, p[i].slot, 'room', p[i].roomId))
                # usedSpace.add((p[i].weekDay, p[i].slot, 'class', p[i].classId))
                # usedSpace.add((p[i].weekDay, p[i].slot, 'teacher', p[i].teacherId))

                count = 0

                # 教室在同一时间只能上一节课
                if p[i].roomId == p[j].roomId:
                    #conflict1.append([i, j])
                    conflictCount += 1
                    count += 1

                    key = (p[i].weekDay, p[i].slot, 'room')
                    putIntoConflictMap(i, j, key, space2Conflict)
                # else:
                #     usedSpace.add((p[j].weekDay, p[j].slot, 'room', p[j].roomId))

                # 班级在一个时间只能上一节课
                if p[i].classId == p[j].classId:
                    #conflict2.append([i, j])
                    conflictCount += 1
                    count += 1

                    key = (p[i].weekDay, p[i].slot, 'class')
                    putIntoConflictMap(i, j, key, space2Conflict)
                # else:
                #     usedSpace.add((p[j].weekDay, p[j].slot, 'class', p[j].classId))

                # 老师在同一时间只能上一节课
                if p[i].teacherId == p[j].teacherId:
                    #conflict3.append([i, j])
                    conflictCount += 1
                    count += 1

                    key = (p[i].weekDay, p[i].slot, 'teacher')
                    putIntoConflictMap(i, j, key, space2Conflict)
                # else:
                #     usedSpace.add((p[j].weekDay, p[j].slot, 'teacher', p[j].teacherId))

                if count > 0:
                    key = (p[i].weekDay, p[i].slot, 'count')
                    space2Conflict[key] = count
            # else:
            #     addToUsedSet(p[i], usedSpace)
            #     addToUsedSet(p[j], usedSpace)

    return conflictCount, usedSpace, space2Conflict


def putIntoConflictMap(i, j, key, space2Conflict):
    value = space2Conflict.get(key)
    if value is None:
        value = set()

    value.add(i)
    value.add(j)
    space2Conflict[key] = value


def addToUsedSet(item, usedSpace):
    usedSpace.add((item.weekDay, item.slot, 'teacher', item.teacherId))
    usedSpace.add((item.weekDay, item.slot, 'class', item.classId))
    usedSpace.add((item.weekDay, item.slot, 'room', item.roomId))


def schedule_cost(population, popSize):
    """calculate conflict of class schedules.

    Arguments:
        population: List, population of class schedules.
        elite: int, number of best result.

    Returns:
        index of best result.
        best conflict score.
    """
    conflicts = []
    n = len(population[0])

    fitnessArray = []

    fc1 = []
    fc2 = []
    fc3 = []
    fc4 = []

    for p in population:
        conflict = 0

        for i in range(0, n - 1):
            for j in range(i + 1, n):
                # check course in same time and same room
                if p[i].roomId == p[j].roomId and p[i].weekDay == p[j].weekDay and p[i].slot == p[j].slot:
                    conflict += 1
                # check course for one class in same time
                if p[i].classId == p[j].classId and p[i].weekDay == p[j].weekDay and p[i].slot == p[j].slot:
                    conflict += 1
                # check course for one teacher in same time
                if p[i].teacherId == p[j].teacherId and p[i].weekDay == p[j].weekDay and p[i].slot == p[j].slot:
                    conflict += 1

        conflicts.append(conflict)

        f1, f2, f3, f4 = fitness(p)
        fc1.append(f1)
        fc2.append(f2)
        fc3.append(f3)
        fc4.append(f4)

    # fc1 = [fc1[i]-50 for i in range(len(fc1))]
    # fc2 = fc2
    # fc3 = [fc3[i]-0.50 for i in range(len(fc1))]
    # fc4 = [fc4[i]-80 for i in range(len(fc1))]

    for i in range(len(fc1)):
        v1 = k1 * fc1[i]
        v2 = k2 * fc2[i]
        v3 = k3 * fc3[i]
        v4 = k4 * fc4[i]
        value = v1 + v2 + v3 + v4
        ## 计算每个个体的适应度（注意这里为了后面的排序，将适应度取的负数）
        fitnessArray.append(-value)

    # index = np.array(conflicts).argsort()
    # 按冲突和适应度排序，先按冲突排序正排序（冲突数少的在前面），再按负的适应度正排序（适应度大的在在前面）
    index = np.lexsort((fitnessArray, conflicts))

    index = index[: popSize]
    # 获取前popSize个元素,并将值转为正数
    fitnessArray = [-fitnessArray[i] for i in index]

    conflicts = [conflicts[i] for i in index]

    # 将适应度再转为正数
    # fitnessArray = [-i for i in fitnessArray]

    return index, conflicts, fitnessArray