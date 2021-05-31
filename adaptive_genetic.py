import copy
import numpy as np
import math

import adaptive_schedule
from adaptive_schedule import schedule_cost, AdaptiveSchedule, conflict, fitnessFun


class AdaptiveGeneticOptimize:
    """Genetic Algorithm.
        popsize: 初始种群数量
        mutprob: 变异概率
        elite:  种群数量
        maxiter: 最大迭代次数
    """

    maxAppearCount = 400

    Pw1=0.9
    Pw2=0.75
    Pk1=0.2
    Pk2=0.01

    printConflictDetail = False

    def __init__(self, popSize=20, mutprob=0.2, crossProb=0.9, maxiter=500):
        # size of population
        self.popsize = popSize
        # prob of mutation
        self.mutprob = mutprob
        # prob of crossover
        self.crossprob = crossProb
        # iter times
        self.maxiter = maxiter


        ## 记录所有时间插槽 5*6=30个
        self.spaceSet = set()

        ## 记录有多少个班级
        self.classIdSet = set()
        self.classCount = 0

        ## 记录有多少个老师
        self.teacherIdSet = set()
        self.teacherCount = 0

        ## 记录全部空间 roomId->set((周几,节))
        self.room2Space = {}
        self.class2Space = {}
        self.teacher2Space = {}

    def checkIsBetter(self, p):
        roomSet = set()
        slotSet = set()
        weekSet = set()
        for i in p:
            roomSet.add(i.roomId)
            slotSet.add(i.slot)
            weekSet.add(i.weekDay)
        count = 0
        if len(roomSet) / AdaptiveSchedule.roomRange > 0.80:
            count += 1
        if len(slotSet) / AdaptiveSchedule.slotInDay > 0.80:
            count += 1
        if len(weekSet) / AdaptiveSchedule.dayInWeek > 0.80:
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

        self.initAllSpace()

        for item in schedules:
            self.classIdSet.add(item.classId)
            self.teacherIdSet.add(item.teacherId)

        self.classCount = len(self.classIdSet)
        self.teacherCount = len(self.teacherIdSet)

        while len(self.population) < self.popsize:
            entity = []

            for s in schedules:
                s.random_init(roomRange)
                entity.append(copy.deepcopy(s))

            conflictCount, usedSpace, space2Conflict = conflict(entity)

            if conflictCount > 0:
                fixed = self.dealConflict2(entity, conflictCount, usedSpace, space2Conflict)
                if fixed == False:
                    continue

                # conflictCount, usedSpace, space2Conflict = conflict(entity)
                # print('修复后，conflictCount=',conflictCount)

            # while conflictCount > 0 and fixCount < 2000:
            #     entity = self.dealConflict(entity, conflict1, conflict2, conflict3)
            #     conflictCount, conflict1, conflict2, conflict3 = conflict(entity)
            #     fixCount += 1
            # while conflictCount > 0:
            #     print('init fixCount=' + str(fixCount) + " conflictCount="+str(conflictCount))
            #     self.dealConflict2(entity,conflictCount, usedSpace, space2Conflict)
            #     conflictCount, usedSpace, space2Conflict = conflict(entity)
            #     fixCount += 1

            if self.checkIsBetter(entity) == 1:
                print('find item,fitness score=' + str(adaptive_schedule.fitness(entity)))
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

    def initAllSpace(self):

        for x in range(1, AdaptiveSchedule.dayInWeek+1):
            for y in range(1, AdaptiveSchedule.slotInDay+1):
                key = (x, y)
                self.spaceSet.add(key)


    def getPopulation(self):
        return self.population

    def setPopulation(self,population,schedules):
        self.initAllSpace()

        for item in schedules:
            self.classIdSet.add(item.classId)
            self.teacherIdSet.add(item.teacherId)

        self.classCount = len(self.classIdSet)
        self.teacherCount = len(self.teacherIdSet)
        self.population=population
        return

    # usedSpace set结构 (weekDay,slot,'room'或'class'或'teacher',roomId/classId/teacherId)
    # space2Conflict keyValue结构 key=(weekDay,slot,'room'或'class'或'teacher'或'count')   value=set(i,j,k....)
    def dealConflict2(self, entity, conflictCount, usedSpace, space2Conflict):

        # 每一个冲突处理完毕后，需要重置可用列表，防止无解的占用了位置没有释放
        for roomId in range(1, AdaptiveSchedule.roomRange + 1):
            self.room2Space[roomId] = copy.deepcopy(self.spaceSet)

        for classId in self.classIdSet:
            self.class2Space[classId] = copy.deepcopy(self.spaceSet)

        for teacherId in self.teacherIdSet:
            self.teacher2Space[teacherId] = copy.deepcopy(self.spaceSet)


        ## 根据已经占用的插槽，生成未被使用的插槽 self.room2Space, self.class2Space, self.teacher2Space
        for item in usedSpace:
            spaceKey = (item[0],item[1])
            spaceType = item[2]

            if spaceType == 'room':
                roomId = item[3]
                try:
                    self.room2Space[roomId].remove(spaceKey)
                except KeyError:
                    print("error key", roomId)
            elif spaceType == 'class':
                classId = item[3]
                try:
                    self.class2Space[classId].remove(spaceKey)
                except KeyError:
                    print("error key", classId)
            elif spaceType == 'teacher':
                teacherId = item[3]
                try:
                    self.teacher2Space[teacherId].remove(spaceKey)
                except KeyError:
                    print("error key", teacherId)
        self.printSplitStart('beginDeal')
        for item in space2Conflict.keys():
            # item = (weekDay,slot,'room'或'class'或'teacher')

            type = item[2]
            if type == 'count':
                continue
            conflictSet = space2Conflict[item]
            # try:
            #     len(conflictSet)
            # except TypeError:
            #     print("异常数据："+ conflictSet + " item="+ item)

            # 保存冲突处理失败的，value最后value集合大小不能大于1，大于1说明无解，需要回退
            failedSet = set()

            while len(conflictSet) > 0 and len(failedSet) <= 1:

                copyConflicteSet = copy.deepcopy(list(conflictSet))
                randonIndex = int(np.random.randint(0,len(copyConflicteSet), 1)[0])
                changeIndex = copyConflicteSet[randonIndex]
                changeEntity = entity[changeIndex]
                if type == 'room':
                    # 处理教室冲突
                    self.printSplitStart('fix_room')
                    haveFixed = self.fixRoomConflict(changeEntity, changeIndex, usedSpace)
                    self.printSplitEnd('fix_room')
                elif type == 'class':
                    # 处理班级冲突
                    self.printSplitStart('fix_class')
                    haveFixed = self.fixClassConflict(changeEntity, changeIndex, usedSpace)
                    self.printSplitEnd('fix_class')
                else:
                    # 处理老师冲突
                    self.printSplitStart('fix_teacher')
                    haveFixed = self.fixTeacherConflict(changeEntity, changeIndex, usedSpace)
                    self.printSplitEnd('fix_teacher')

                if haveFixed == False:
                    failedSet.add(changeIndex)
                conflictSet.remove(changeIndex)

            if len(conflictSet) == 0 and len(failedSet) <= 1:
                continue
            else:
                return False
        self.printSplitEnd('endDeal')
        return True

    def printSplitEnd(self,part):
        if AdaptiveGeneticOptimize.printConflictDetail == True:
            print('==============endDealConflict--%s==================' %(part))

    def printSplitStart(self,part):
        if AdaptiveGeneticOptimize.printConflictDetail == True:
            print('==============startDealConflict--%s==================' %(part))

    def fixTeacherConflict(self, changeEntity, changeIndex, usedSpace):
        teacherId = changeEntity.teacherId
        findAvailable = False
        while findAvailable == False:

            availableSpaceSet = self.teacher2Space[teacherId]

            copyAvailableTeacherSpaceSet = copy.deepcopy(list(availableSpaceSet))

            while len(copyAvailableTeacherSpaceSet) > 0:
                availableSpaceIndex = int(np.random.randint(0, len(copyAvailableTeacherSpaceSet), 1)[0])
                availableSpace = copyAvailableTeacherSpaceSet[availableSpaceIndex]
                tryUseRoomSpaceKey = (availableSpace[0], availableSpace[1], 'room', changeEntity.roomId)
                tryUseClassSpaceKey = (availableSpace[0], availableSpace[1], 'class', changeEntity.classId)
                if tryUseRoomSpaceKey not in usedSpace and tryUseClassSpaceKey not in usedSpace and availableSpace in self.room2Space[changeEntity.roomId] and availableSpace in self.class2Space[changeEntity.classId]:
                    # 找到可用槽位
                    self.printBefore(changeEntity, changeIndex)
                    changeEntity.weekDay = availableSpace[0]
                    changeEntity.slot = availableSpace[1]
                    self.printAfter(changeEntity, changeIndex)
                    findAvailable = True
                    break
                else:
                    copyAvailableTeacherSpaceSet.remove(availableSpace)
            if findAvailable == True:
                # 将冲突列表中删除，添加占用set，减少可用set ,更新各个数据结构
                needRemovedSpaceKey = (changeEntity.weekDay, changeEntity.slot)
                try:
                    self.room2Space[changeEntity.roomId].remove(needRemovedSpaceKey)
                    self.teacher2Space[changeEntity.teacherId].remove(needRemovedSpaceKey)
                    self.class2Space[changeEntity.classId].remove(needRemovedSpaceKey)
                except KeyError:
                    print("error key",needRemovedSpaceKey)

                usedSpace.add((changeEntity.weekDay, changeEntity.slot, 'teacher', changeEntity.teacherId))
                return True
            else:
                # 未找到
                #print('teacher时间槽位遍历完毕未找到可用位置，无解')
                return False

    def printBefore(self, changeEntity, changeIndex):
        if self.printConflictDetail == False:
            return
        print("before change: classId=%f,roomId=%d,teacherId=%d,weekDay=%d,slot=%d,index=%d" % (
            changeEntity.classId, changeEntity.roomId, changeEntity.teacherId, changeEntity.weekDay,
            changeEntity.slot, changeIndex))

    def printAfter(self, changeEntity, changeIndex):
        if self.printConflictDetail == False:
            return
        print("after change: classId=%f,roomId=%d,teacherId=%d,weekDay=%d,slot=%d,index=%d" % (
            changeEntity.classId, changeEntity.roomId, changeEntity.teacherId, changeEntity.weekDay,
            changeEntity.slot, changeIndex))

    def fixClassConflict(self, changeEntity, changeIndex, usedSpace):
        classId = changeEntity.classId
        findAvailable = False
        while findAvailable == False:

            availableSpaceSet = self.class2Space[classId]

            copyAvailableClassSpaceSet = copy.deepcopy(list(availableSpaceSet))

            while len(copyAvailableClassSpaceSet) > 0:
                availableSpaceIndex = int(np.random.randint(0, len(copyAvailableClassSpaceSet), 1)[0])
                availableSpace = copyAvailableClassSpaceSet[availableSpaceIndex]
                tryUseRoomSpaceKey = (availableSpace[0], availableSpace[1], 'room', changeEntity.roomId)
                tryUseTeacherSpaceKey = (availableSpace[0], availableSpace[1], 'teacher', changeEntity.teacherId)
                if tryUseRoomSpaceKey not in usedSpace and tryUseTeacherSpaceKey not in usedSpace and availableSpace in self.room2Space[changeEntity.roomId] and availableSpace in self.teacher2Space[changeEntity.teacherId]:
                    # 找到可用槽位
                    self.printBefore(changeEntity, changeIndex)
                    changeEntity.weekDay = availableSpace[0]
                    changeEntity.slot = availableSpace[1]
                    self.printAfter(changeEntity, changeIndex)
                    findAvailable = True
                    break
                else:
                    copyAvailableClassSpaceSet.remove(availableSpace)
            if findAvailable == True:
                # 将冲突列表中删除，添加占用set，减少可用set ,更新各个数据结构
                needRemovedSpaceKey = (changeEntity.weekDay, changeEntity.slot)
                try:
                    self.room2Space[changeEntity.roomId].remove(needRemovedSpaceKey)
                    self.teacher2Space[changeEntity.teacherId].remove(needRemovedSpaceKey)
                    self.class2Space[changeEntity.classId].remove(needRemovedSpaceKey)
                except KeyError:
                    print("error key",needRemovedSpaceKey)
                usedSpace.add((changeEntity.weekDay, changeEntity.slot, 'class', changeEntity.classId))
                return True
            else:
                # 未找到
                #print('class时间槽位遍历完毕未找到可用位置，无解')
                return False

    def fixRoomConflict(self, changeEntity, changeIndex, usedSpace):
        oldRoomId = changeEntity.roomId
        roomId = oldRoomId
        exitRoomId = oldRoomId - 1
        if oldRoomId == 1:
            exitRoomId = AdaptiveSchedule.roomRange
        findAvailable = False
        while findAvailable == False:
            availableSpaceSet, newRoomId = self.findAvailableRoom(roomId, exitRoomId)

            copyAvailableRoomSpaceSet = copy.deepcopy(list(availableSpaceSet))

            while len(copyAvailableRoomSpaceSet) > 0:
                availableSpaceIndex = int(np.random.randint(0, len(copyAvailableRoomSpaceSet), 1)[0])
                availableSpace = copyAvailableRoomSpaceSet[availableSpaceIndex]
                tryUseClassSpaceKey = (availableSpace[0], availableSpace[1], 'class', changeEntity.classId)
                tryUseTeacherSpaceKey = (availableSpace[0], availableSpace[1], 'teacher', changeEntity.teacherId)
                if tryUseClassSpaceKey not in usedSpace and tryUseTeacherSpaceKey not in usedSpace and availableSpace in self.class2Space[changeEntity.classId] and availableSpace in self.teacher2Space[changeEntity.teacherId]:
                    # 找到可用槽位
                    self.printBefore(changeEntity, changeIndex)
                    changeEntity.roomId = newRoomId
                    changeEntity.weekDay = availableSpace[0]
                    changeEntity.slot = availableSpace[1]
                    self.printAfter(changeEntity, changeIndex)
                    findAvailable = True
                    break
                else:
                    copyAvailableRoomSpaceSet.remove(availableSpace)
            if findAvailable == True:
                # 将冲突列表中删除，添加占用set，减少可用set ,更新各个数据结构
                needRemovedSpaceKey = (changeEntity.weekDay, changeEntity.slot)
                try:
                    self.room2Space[changeEntity.roomId].remove(needRemovedSpaceKey)
                    self.teacher2Space[changeEntity.teacherId].remove(needRemovedSpaceKey)
                    self.class2Space[changeEntity.classId].remove(needRemovedSpaceKey)
                except KeyError:
                    print("key error ",needRemovedSpaceKey)

                usedSpace.add((changeEntity.weekDay, changeEntity.slot, 'room', changeEntity.roomId))
                return True
            else:
                # 未找到
                if newRoomId == exitRoomId:
                    # 找了一圈没找到可用教室的时间槽位，无解
                    #print('room时间槽位遍历完毕未找到可用位置，无解')
                    return False
                else:
                    if newRoomId + 1 > AdaptiveSchedule.roomRange:
                        roomId = 1
                    else:
                        roomId = newRoomId + 1

    def findAvailableRoom(self, roomId, exitRoomId):

        while True:
            availableSpaceSet = self.room2Space[roomId]
            if roomId!=exitRoomId and len(availableSpaceSet) <= 0:
                # 该教室没有可用空间，更换教室
                roomId += 1
                if roomId > AdaptiveSchedule.roomRange:
                    roomId = 1
            else:
                break
        return availableSpaceSet, roomId

    def dealConflict(self, entity, conflict1, conflict2, conflict3):
        # roomId2UsedSpace = {}  # roomId->已使用坑的二维矩阵
        roomId2FreeSpace = {}  # roomId->记录可使用坑位的数组

        ####### 处理教室冲突
        # 记录所有教室
        roomId2AllSpace = copy.deepcopy(self.room2AllSpace)

        # 收集未被使用的槽
        for i in entity:
            temSet = roomId2AllSpace.get(i.roomId)
            temItem =[i.weekDay, i.slot]
            if temItem in temSet:
                temSet.remove(temItem)

        roomId2FreeSpace = roomId2AllSpace

        # 教室在同一时间只能上一节课
        if len(conflict1) > 0:
            self.fixConflict(conflict1, entity, roomId2FreeSpace)

        ######处理班级时间冲突



        ######处理老师时间冲突

        # 收集各个教室中还能用的坑
        # for roomId in roomId2UsedSpace.keys():
        #     usedMatrix = roomId2UsedSpace[roomId]
        #     freeSpace = []
        #     for i in range(Schedule.dayInWeek):
        #         for j in range(Schedule.slotInDay):
        #             if usedMatrix[i][j] == 0:
        #                 freeSpace.append([i, j])
        #     roomId2FreeSpace[roomId] = freeSpace

        # 老师在同一时间只能上一节课
        if len(conflict3) > 0:
            self.fixConflict(conflict3, entity, roomId2FreeSpace)

        # 班级在一个时间只能上一节课
        if len(conflict2) > 0:
            self.fixConflict(conflict2, entity, roomId2FreeSpace)


        return entity

    def fixConflict(self, conflictList, entity, roomId2FreeSpace):
        for item in conflictList:
            ## 从两个冲突的对象中，随机选择一个进行冲突处理
            fixIndex = int(np.random.randint(0,2,1)[0])
            conflictItem = entity[item[fixIndex]]
            # randomRoomId = np.random.randint(1, Schedule.roomRange + 1, 1)[0]
            # availableRoomId = self.getAvailableRoom(roomId2FreeSpace, randomRoomId, 0)
            # 优先教室不变，选择可用的时间插槽，如果没有，就换教室
            availableRoomId = self.getAvailableRoom(roomId2FreeSpace, conflictItem.roomId, 0)
            if availableRoomId == -1:
                print('没有可用的教室可用')
                exit(-1)
            array = roomId2FreeSpace[availableRoomId]

            # 从可用列表中随机获取一个可用的坑
            availableIndex = int(np.random.randint(0, len(array), 1)[0])
            item = array[availableIndex]
            conflictItem.weekDay = item[0]
            conflictItem.slot = item[1]
            # 可用列表上移除这个坑
            array.remove(item)

    def getAvailableRoom(self, roomId2FreeSpace, nowroomId, deep):
        if deep == AdaptiveSchedule.roomRange:
            # 没有任何一个教室有空间
            return -1
        array = roomId2FreeSpace[nowroomId]
        if len(array) > 0:
            return nowroomId
        else:
            if nowroomId + 1 > AdaptiveSchedule.roomRange:
                nowroomId = 1
            else:
                nowroomId += 1
            return self.getAvailableRoom(roomId2FreeSpace, nowroomId, deep + 1)

    ## 交叉概率
    def crossoverProbFun(self, Fmax, Fmin, Fmean):
        if Fmean<=Fmax/2:
            return AdaptiveGeneticOptimize.Pw1-(AdaptiveGeneticOptimize.Pw1-AdaptiveGeneticOptimize.Pw2) * (Fmax/2-Fmean)/(Fmax/2-Fmin)
        else:
            return AdaptiveGeneticOptimize.Pw1

    ## 变异概率
    def mutateprobFun(self, f, Fmax):
        if f >= Fmax/2:
            return AdaptiveGeneticOptimize.Pk1 - 2*(AdaptiveGeneticOptimize.Pk1-AdaptiveGeneticOptimize.Pk2)*(f-Fmax)/Fmax
        else:
            return AdaptiveGeneticOptimize.Pk1

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

        item = copy.deepcopy(newPopulation[index])
        for p in item:
            pos = int(np.random.randint(0, 3, 1)[0])
            # operation = np.random.rand()

            if pos == 0:
                # p.roomId = self.addSub(p.roomId, operation, roomRange)
                p.roomId = self.randomWithOut(AdaptiveSchedule.roomRange, p.roomId)
            if pos == 1:
                # p.weekDay = self.addSub(p.weekDay, operation, Schedule.dayInWeek)
                p.weekDay = self.randomWithOut(AdaptiveSchedule.dayInWeek, p.weekDay)
            if pos == 2:
                # p.slot = self.addSub(p.slot, operation, Schedule.slotInDay)
                p.slot = self.randomWithOut(AdaptiveSchedule.slotInDay, p.slot)


        # mutateCount = 0
        #
        # while True:
        #     item = copy.deepcopy(newPopulation[index])
        #     for p in item:
        #         pos = np.random.randint(0, 3, 1)[0]
        #         # operation = np.random.rand()
        #
        #         if pos == 0:
        #             # p.roomId = self.addSub(p.roomId, operation, roomRange)
        #             p.roomId = self.randomWithOut(Schedule.roomRange, p.roomId)
        #         if pos == 1:
        #             # p.weekDay = self.addSub(p.weekDay, operation, Schedule.dayInWeek)
        #             p.weekDay = self.randomWithOut(Schedule.dayInWeek, p.weekDay)
        #         if pos == 2:
        #             # p.slot = self.addSub(p.slot, operation, Schedule.slotInDay)
        #             p.slot = self.randomWithOut(Schedule.slotInDay, p.slot)
        #
        #
        #     mutateCount += 1
        #
        #     conflictCount1, conflict1, conflict2, conflict3 = conflict(item)
        #
        #     if conflictCount1 > 0 and mutateCount<Schedule.mutateRetryMaxCount:
        #         # 变异后出现冲突，则重新选取变异位点和变异值
        #         continue
        #     else:
        #         # 没有找到，复原
        #         # item = newPopulation[index]
        #         break

        return item

    def randomWithOut(self, range, nowValue):
        newValue = int(np.random.randint(1, range + 1, 1)[0])
        while nowValue == newValue:
            newValue = int(np.random.randint(1, range + 1, 1)[0])
        return newValue

    ## 交叉操作
    def crossoverOp(self, eiltePopulation, e1, e2):
        """Crossover Operation

        Arguments:
            eiltePopulation: List, population of elite schedules.

        Returns:
            ep: List, population after crossover.
        """

        ep1 = copy.deepcopy(eiltePopulation[e1])
        ep2 = copy.deepcopy(eiltePopulation[e2])

        # 交叉点位随机范围
        pos = int(np.random.randint(0, len(ep1), 1)[0])
        type = int(np.random.randint(0, 2, 1)[0])
        # index = 0
        p1 = ep1[pos]
        p2 = ep2[pos]
        if type == 0:
            p1.weekDay, p2.weekDay = p2.weekDay, p1.weekDay
            p1.slot, p2.slot = p2.slot, p1.slot
        if type == 1:
            p1.roomId, p2.roomId = p2.roomId, p1.roomId

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

            MyFitnessList = np.array(fitnessList)
            Fmax = MyFitnessList.max()
            Fmin = MyFitnessList.min()
            Fmean = MyFitnessList.mean()

            print('Iter: {} | conflict: {} | bestFitness: {}'.format(i + 1, bestConflict, bestFitness))

            # if (bestConflict == 0 and bestFitness == maxFitness and appearCount >= AdaptiveGeneticOptimize.maxAppearCount) or (
            #         i + 1 == self.maxiter):
            if i + 1 == self.maxiter:
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
            self.crossover(newPopulation,Fmax,Fmin,Fmean)

            fixedPopulation = []
            for k in range(len(newPopulation)):
                entity = newPopulation[k]

                conflictCount, usedSpace, space2Conflict = conflict(entity)

                if conflictCount > 0:
                    fixed = self.dealConflict2(entity, conflictCount, usedSpace, space2Conflict)
                    if fixed == True:
                        fixedPopulation.append(entity)
                else:
                    fixedPopulation.append(entity)

            ## 变异运算 随机选取个体，选取位置进行变异
            self.mutate(fixedPopulation)

            fixedPopulation = []
            for k in range(len(newPopulation)):
                entity = newPopulation[k]

                conflictCount, usedSpace, space2Conflict = conflict(entity)

                if conflictCount > 0:
                    fixed = self.dealConflict2(entity, conflictCount, usedSpace, space2Conflict)
                    if fixed == True:
                        fixedPopulation.append(entity)
                else:
                    fixedPopulation.append(entity)

            self.population = fixedPopulation

        return bestSchedule, maxFitness

    def mutate(self, newPopulation):

        finessList=fitnessFun(newPopulation)
        MyFitnessList = np.array(finessList)
        Fmax = MyFitnessList.max()
        for i in range(len(newPopulation)):
            p = np.random.rand()
            if p < self.mutateprobFun(MyFitnessList[i],Fmax):
                newItem = self.mutateOp(newPopulation, i)
                newPopulation.append(newItem)

    def crossover(self, newPopulation, Fmax, Fmin, Fmean):
        # 洗牌
        np.random.shuffle(newPopulation)
        # 根据概率，如果命中，两两配对交叉
        for i in range(int(self.popsize / 2)):
            p = np.random.rand()
            if p < self.crossoverProbFun(Fmax, Fmin, Fmean):
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