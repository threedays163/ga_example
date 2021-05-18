import copy
import numpy as np
import math

import schedule
from schedule import schedule_cost, Schedule, conflict


class GeneticOptimize:
    """Genetic Algorithm.
        popsize: 初始种群数量
        mutprob: 变异概率
        elite:  种群数量
        maxiter: 最大迭代次数
    """

    maxAppearCount = 50

    def __init__(self, popSize=20, mutprob=0.2, crossProb=0.9, maxiter=500):
        # size of population
        self.popsize = popSize
        # prob of mutation
        self.mutprob = mutprob
        # prob of crossover
        self.crossprob = crossProb
        # iter times
        self.maxiter = maxiter


    def checkIsBetter(self, p):
        roomSet = set()
        slotSet = set()
        weekSet = set()
        for i in p:
            roomSet.add(i.roomId)
            slotSet.add(i.slot)
            weekSet.add(i.weekDay)
        count = 0
        if len(roomSet) / Schedule.roomRange > 0.80:
            count += 1
        if len(slotSet) / Schedule.slotInDay > 0.80:
            count += 1
        if len(weekSet) / Schedule.dayInWeek > 0.80:
            count += 1
        if count == 3:
            return 1
        else:
            return 0

    ## 初始化种群
    def init_population(self, schedules, roomRange):
        """Init population

        Arguments:
            schedules: List, population of class schedules.
            roomRange: int, number of classrooms.
        """
        self.population = []

        while len(self.population) < self.popsize:
            entity = []

            for s in schedules:
                s.random_init(roomRange)
                entity.append(copy.deepcopy(s))

            conflictCount, conflict1, conflict2, conflict3 = conflict(entity)

            fixCount=0

            while conflictCount > 0 and fixCount < 2000:
                entity = self.dealConflict(entity, conflict1, conflict2, conflict3)
                conflictCount, conflict1, conflict2, conflict3 = conflict(entity)
                fixCount += 1

            if conflictCount == 0:
                if self.checkIsBetter(entity) == 1:
                    print('find item,fitness score=' + str(schedule.fitness(entity)))
                    self.population.append(entity)

        # for i in range(self.popsize):
        #     entity = []
        #
        #     for s in schedules:
        #         s.random_init(roomRange)
        #         entity.append(copy.deepcopy(s))
        #
        #     self.population.append(entity)

        # 判断初始化多样性是否高
        return

    def getPopulation(self):
        return self.population

    def setPopulation(self,population):
        self.population=population
        return


    def dealConflict(self, entity, conflict1, conflict2, conflict3):
        roomId2UsedSpace = {}  # roomId->已使用坑的二维矩阵
        roomId2FreeSpace = {}  # roomId->记录可使用坑位的数组

        # 记录所有教室
        for i in range(Schedule.roomRange):
            s = [[0 for i in range(Schedule.slotInDay)] for i in range(Schedule.dayInWeek)]
            roomId2UsedSpace[i + 1] = s

        # 收集各个教室中已经占用的坑
        for i in entity:
            s = roomId2UsedSpace.get(i.roomId)
            s[i.weekDay - 1][i.slot - 1] = 1
            roomId2UsedSpace[i.roomId] = s

        # 收集各个教室中还能用的坑
        for roomId in roomId2UsedSpace.keys():
            usedMatrix = roomId2UsedSpace[roomId]
            freeSpace = []
            for i in range(Schedule.dayInWeek):
                for j in range(Schedule.slotInDay):
                    if usedMatrix[i][j] == 0:
                        freeSpace.append([i, j])
            roomId2FreeSpace[roomId] = freeSpace

        # 老师在同一时间只能上一节课
        if len(conflict3) > 0:
            self.fixConflict(conflict3, entity, roomId2FreeSpace)

        # 班级在一个时间只能上一节课
        if len(conflict2) > 0:
            self.fixConflict(conflict2, entity, roomId2FreeSpace)

        # 教室在同一时间只能上一节课
        if len(conflict1) > 0:
            self.fixConflict(conflict1, entity, roomId2FreeSpace)
        return entity

    def fixConflict(self, conflictList, entity, roomId2FreeSpace):
        for item in conflictList:
            conflictItem = entity[item[1]]
            randomRoomId = np.random.randint(1, Schedule.roomRange + 1, 1)[0]
            availableRoomId = self.getAvailableRoom(roomId2FreeSpace, randomRoomId, 0)
            # availableRoomId = self.getAvailableRoom(roomId2FreeSpace, conflictItem.roomId, 0)
            if availableRoomId == -1:
                print('没有可用的教室可用')
                exit(-1)
            array = roomId2FreeSpace[availableRoomId]
            # 从可用列表中随机获取一个可用的坑
            availableIndex = np.random.randint(0, len(array), 1)[0]
            availItem = array[availableIndex]
            conflictItem.weekDay = availItem[0] + 1
            conflictItem.slot = availItem[1] + 1
            # 可用列表上移除这个坑
            array.remove(availItem)

    def getAvailableRoom(self, roomId2FreeSpace, nowroomId, deep):
        if deep == Schedule.roomRange:
            # 没有任何一个教室有空间
            return -1
        array = roomId2FreeSpace[nowroomId]
        if len(array) > 0:
            return nowroomId
        else:
            if nowroomId + 1 > Schedule.roomRange:
                nowroomId = 1
            else:
                nowroomId += 1
            return self.getAvailableRoom(roomId2FreeSpace, nowroomId, deep + 1)

    ## 编译概率
    def mutateprobFun(self, n):
        return 1 / (2 * (1 + math.exp(n / 400)))

    ## 变异操作
    # def mutate(self, eiltePopulation, roomRange, index):
    #     """Mutation Operation
    #
    #     Arguments:
    #         eiltePopulation: List, population of elite schedules.
    #         roomRange: int, number of classrooms.
    #
    #     Returns:
    #         ep: List, population after mutation.
    #     """
    #
    #     e = -1
    #     if index>=0:
    #         e=index
    #     else:
    #         e=np.random.randint(0, self.popsize, 1)[0]
    #
    #     ep = copy.deepcopy(eiltePopulation[e])
    #
    #     for p in ep:
    #         pos = np.random.randint(0, 3, 1)[0]
    #         operation = np.random.rand()
    #
    #         if pos == 0:
    #             p.roomId = self.addSub(p.roomId, operation, roomRange)
    #         if pos == 1:
    #             p.weekDay = self.addSub(p.weekDay, operation, CommonSchedule.dayInWeek)
    #         if pos == 2:
    #             p.slot = self.addSub(p.slot, operation, CommonSchedule.slotInDay)
    #
    #     return ep,e

    ## 变异操作
    def mutateOp(self, newPopulation, index):
        """Mutation Operation

        Arguments:
            eiltePopulation: List, population of elite schedules.

        Returns:
            ep: List, population after mutation.
        """

        mutateCount = 0

        while True:
            item = copy.deepcopy(newPopulation[index])
            for p in item:
                pos = np.random.randint(0, 3, 1)[0]
                # operation = np.random.rand()

                if pos == 0:
                    # p.roomId = self.addSub(p.roomId, operation, roomRange)
                    p.roomId = self.randomWithOut(Schedule.roomRange, p.roomId)
                if pos == 1:
                    # p.weekDay = self.addSub(p.weekDay, operation, Schedule.dayInWeek)
                    p.weekDay = self.randomWithOut(Schedule.dayInWeek, p.weekDay)
                if pos == 2:
                    # p.slot = self.addSub(p.slot, operation, Schedule.slotInDay)
                    p.slot = self.randomWithOut(Schedule.slotInDay, p.slot)


            mutateCount += 1

            conflictCount1, conflict1, conflict2, conflict3 = conflict(item)

            if conflictCount1 > 0 and mutateCount<Schedule.mutateRetryMaxCount:
                # 变异后出现冲突，则重新选取变异位点和变异值
                continue
            else:
                # 没有找到，复原
                # item = newPopulation[index]
                break

        return item

    def randomWithOut(self, range, nowValue):
        newValue = np.random.randint(1, range + 1, 1)[0]
        while nowValue == newValue:
            newValue = np.random.randint(1, range + 1, 1)[0]
        return newValue

    ## 交叉操作
    def crossoverOp(self, eiltePopulation, e1, e2):
        """Crossover Operation

        Arguments:
            eiltePopulation: List, population of elite schedules.

        Returns:
            ep: List, population after crossover.
        """
        if e1 == -1 or e2 == -1:
            e1 = np.random.randint(0, self.popsize, 1)[0]
            e2 = np.random.randint(0, self.popsize, 1)[0]
            while e1==e2:
                e2=np.random.randint(0, self.popsize, 1)[0]

        # 交叉次数
        crossCount = 0

        ## crossover field value
        while True:
            ep1 = copy.deepcopy(eiltePopulation[e1])
            ep2 = copy.deepcopy(eiltePopulation[e2])

            # 交叉点位随机范围
            pos = np.random.randint(0, len(ep1), 1)[0]
            type = np.random.randint(0, 2, 1)[0]
            index = 0
            p1 = ep1[pos]
            p2 = ep2[pos]
            if type == 0:
                p1.weekDay, p2.weekDay = p2.weekDay, p1.weekDay
                p1.slot, p2.slot = p2.slot, p1.slot
            if type == 1:
                p1.roomId, p2.roomId = p2.roomId, p1.roomId
            # for p1, p2 in zip(ep1, ep2):
            #     if index < pos:
            #         index += 1
            #         continue
            crossCount += 1

            conflictCount1, conflict1, conflict2, conflict3 = conflict(ep1)
            conflictCount2, conflict1, conflict2, conflict3 = conflict(ep2)


            if (conflictCount1 > 0 or conflictCount2 > 0) and crossCount<Schedule.crossRetryMaxCount :
                # 交叉后出现冲突，则重新选取交叉位点
                continue
            else:
                break

        return [ep1, ep2]

    ## 演化
    def evolution(self):
        appearCount = 0
        maxFitness = 0
        bestSchedule = None

        for i in range(self.maxiter):
            # eliteIndex记录了根据冲突和适应度排序后的结果，排第一的是冲突最少，适应度最高的
            eliteIndex, conflictList, fitnessList = schedule_cost(self.population, self.popsize)

            bestConflict = conflictList[0]
            bestFitness = fitnessList[0]

            print('Iter: {} | conflict: {} | bestFitness: {}'.format(i + 1, bestConflict, bestFitness))

            if (bestConflict == 0 and bestFitness == maxFitness and appearCount >= GeneticOptimize.maxAppearCount) or (
                    i + 1 == self.maxiter):
                # 结束，输出最优解
                bestSchedule = self.population[0]
                break

            if bestConflict == 0:
                if bestFitness > maxFitness:
                    maxFitness = bestFitness
                    appearCount = 1
                elif bestFitness == maxFitness:
                    appearCount += 1

            self.population = [self.population[i] for i in eliteIndex]
            newPopulation = self.population

            ## 选择运算 将各个个体适应度累计求和为S，将各个个体适应度s/S=P(select) 作为被选中的概率，每个个体有累计概率
            self.select(fitnessList, newPopulation)

            ## 交叉运算
            self.crossover(newPopulation)

            ## 变异运算 随机选取个体，选取位置进行变异
            self.mutate(newPopulation)

            for k in range(len(newPopulation)):
                entity = newPopulation[k]
                conflictCount, conflict1, conflict2, conflict3 = conflict(entity)

                fixCount = 0

                while conflictCount > 0 and fixCount < 2000:
                    entity = self.dealConflict(entity, conflict1, conflict2, conflict3)
                    conflictCount, conflict1, conflict2, conflict3 = conflict(entity)
                    fixCount += 1

                newPopulation[k] = entity

            self.population = newPopulation

        return bestSchedule, maxFitness

    def mutate(self, newPopulation):
        for i in range(len(newPopulation)):
            p = np.random.rand()
            if p < self.mutateprobFun(i):
                newItem = self.mutateOp(newPopulation, i)
                newPopulation.append(newItem)

    def crossover(self, newPopulation):
        # 洗牌
        np.random.shuffle(newPopulation)
        # 根据概率，如果命中，两两配对交叉
        for i in range(int(self.popsize / 2)):
            p = np.random.rand()
            if p < self.crossprob:
                newItem = self.crossoverOp(newPopulation, 2 * i, 2 * i + 1)

                newPopulation.append(newItem[0])
                newPopulation.append(newItem[1])
                # newPopulation[2 * i] = newItem[0]
                # newPopulation[2 * i + 1] = newItem[1]


    def select(self, fitnessList, newPopulation):
        # S为适应度之和
        S = np.sum(fitnessList)
        # PsList为各个个体被选中的概率
        PsList = [i / S for i in fitnessList]
        # 从种群中重新选择个体行程新种群
        # 第一给一定会被选中
        # newPopulation.append(self.population[0])
        haveSelected = set()
        for i in range(self.popsize):
            randomP = np.random.rand()
            sumP = 0

            if i == self.popsize-1:
                if 0 not in haveSelected:
                    newPopulation.append(self.population[0])
                    break

            for j in range(len(PsList)):
                sumP += PsList[j]
                if randomP < sumP:
                    haveSelected.add(j)
                    newPopulation.append(self.population[j])
                    break