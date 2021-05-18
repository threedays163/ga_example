import prettytable

from schedule import Schedule
from genetic import GeneticOptimize


def vis(schedule):
    """visualization Class Schedule.

    Arguments:
        schedule: List, Class Schedule
    """
    col_labels = ['week/slot', '1', '2', '3', '4', '5']
    table_vals = [[i + 1, '', '', '', '', ''] for i in range(5)]

    table = prettytable.PrettyTable(col_labels, hrules=prettytable.ALL)

    for s in schedule:
        weekDay = s.weekDay
        slot = s.slot
        text = 'course: {} \n class: {} \n room: {} \n teacher: {}'.format(s.courseId, s.classId, s.roomId, s.teacherId)
        table_vals[weekDay - 1][slot] = text

    for row in table_vals:
        table.add_row(row)

    print(table)


if __name__ == '__main__':
    schedules = []

    # add schedule  课程，班级，老师
    ## 测试数据，一共5个班，每个班6门课，前3个课，每门课每周上3次，第四门课每周上2次，最后两门课一周上1次，每门课3个老师
    ## 5个班
    ## 6门课
    ## 3门课上3次，2门课上2次，1门课上一次 共14次课
    ## 每门课有2个老师，共12个老师  5*14=70次课，

    for i in range(5):  # 班级
        for j in range(6):  # 课程
            classId = 2101 + i
            courseId = 100 + j
            teacherId = 10000 + 10 * j
            if i < 3:
                teacherId += 1
            else:
                teacherId += 2
            if j < 3:  ##前3门课，每周上3次
                schedules.append(Schedule(classId, courseId, teacherId))
                schedules.append(Schedule(classId, courseId, teacherId))
                schedules.append(Schedule(classId, courseId, teacherId))
            if j >= 3 and j <= 4:
                schedules.append(Schedule(classId, courseId, teacherId))
                schedules.append(Schedule(classId, courseId, teacherId))
            if j == 5:
                schedules.append(Schedule(classId, courseId, teacherId))

    print(len(schedules))

    for i in schedules:
        print('classId:{} | course:{} | teacherId:{}'.format(i.classId, i.courseId, i.teacherId))

    # schedules = []
    #
    # # add schedule
    # schedules.append(Schedule(201, 1201, 11101))
    # schedules.append(Schedule(201, 1201, 11101))
    # schedules.append(Schedule(202, 1201, 11102))
    # schedules.append(Schedule(202, 1201, 11102))
    # schedules.append(Schedule(203, 1201, 11103))
    # schedules.append(Schedule(203, 1201, 11103))
    # schedules.append(Schedule(206, 1201, 11106))
    # schedules.append(Schedule(206, 1201, 11106))
    #
    # schedules.append(Schedule(202, 1202, 11102))
    # schedules.append(Schedule(202, 1202, 11102))
    # schedules.append(Schedule(204, 1202, 11104))
    # schedules.append(Schedule(204, 1202, 11104))
    # schedules.append(Schedule(206, 1202, 11106))
    # schedules.append(Schedule(206, 1202, 11106))
    #
    # schedules.append(Schedule(203, 1203, 11103))
    # schedules.append(Schedule(203, 1203, 11103))
    # schedules.append(Schedule(204, 1203, 11104))
    # schedules.append(Schedule(204, 1203, 11104))
    # schedules.append(Schedule(205, 1203, 11105))
    # schedules.append(Schedule(205, 1203, 11105))
    # schedules.append(Schedule(206, 1203, 11106))
    # schedules.append(Schedule(206, 1203, 11106))
    #
    # # optimization
    # ga = GeneticOptimize(popsize=50, elite=10, maxiter=500)
    # res = ga.evolution(schedules, 3)
    #
    # # visualization
    # vis_res = []
    # for r in res:
    #     if r.classId == 1203:
    #         vis_res.append(r)
    # vis(vis_res)
