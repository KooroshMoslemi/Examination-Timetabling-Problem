import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# rooms=['Room A','Room B', 'Room C', 'Room D', 'Room E']
# colors=['pink', 'lightgreen', 'lightblue', 'wheat', 'salmon']

day_labels=['TIME SCHEDULE']

courses_df = pd.read_excel("data.xlsx", "Courses", engine='openpyxl')
course_time = {}
for row in courses_df.iterrows():
    idx = int(row[1][0]) - 1
    for x in [4, 5]:
        if len(str(row[1][x])) < 4: continue
        tmz = row[1][x].split("]")[0].split("[")[1].split("-")
        def prep_time(tm):
            l = int(tm[0])*60 if not ":" in tm[0] else int(tm[0].split(":")[0]) * 60 + int(tm[0].split(":")[1])
            l -= int(tm[1])*60 if not ":" in tm[1] else int(tm[1].split(":")[0]) * 60 + int(tm[1].split(":")[1])
            duration = l
            start_h = int(tm[1]) if not ":" in tm[1] else int(tm[1].split(":")[0])
            start_m = 0 if not ":" in tm[1] else int(tm[1].split(":")[1])
            return [start_h, start_m, duration]
        [start_h, start_m, duration] = prep_time(tmz)
        xx = None
        T = 7
        if "يک" in row[1][x].split("[")[0]:
            for t in range(T):
                if t % 7 == 1:
                    xx = t
        elif "دو" in row[1][x].split("[")[0]:
            for t in range(T):
                if t % 7 == 2:
                    xx = t
        elif "سه" in row[1][x].split("[")[0]:
            for t in range(T):
                if t % 7 == 3:
                    xx = t
        else:
            for t in range(T):
                if t % 7 == 0:
                    xx = t
        if not idx in course_time:
            course_time[idx] = {}
        course_time[idx][xx] = {}
        course_time[idx][xx]["start_h"] = start_h
        course_time[idx][xx]["start_m"] = start_m
        course_time[idx][xx]["duration"] = duration
        course_time[idx]["code"] = row[1][1]
        course_time[idx]["name"] = row[1][2]
        course_time[idx]["group"] = row[1][3]
        course_time[idx]["prof"] = row[1][6]

log_file = "t5_gams_py_gjo0.lst"
flg = False

cnt = 0
lines = []
for line in open(log_file, "r"):
    if "E q.L" in line:
        flg = True
    if "GAMS" in line or "E c.L" in line:
        flg = False
    if flg and "E q.L" not in line and len(line) > 10:
        if not line in lines:
            lines += [line]
for i in range(1, len(lines)):
    lines[i] = lines[i][:-1] + " " * (len(lines[0]) - len(lines[i])) + "\n"
start = lines[0].find(lines[0].split()[0]) + 1
step = lines[0].find(lines[0].split()[1]) - lines[0].find(lines[0].split()[0])
tmp = []
for x, line in enumerate(lines):
    tmp_line = line
    if x > 0: 
        tmp_line = tmp_line[:3] + "," + tmp_line[4:]
    for i in range(start, len(line), step):
        tmp_line = tmp_line[:i] + "," + tmp_line[i+1:]
    tmp += [tmp_line + "\n"]
lines = tmp
f = open("ff.txt", "w")
for line in lines:
    f.write(line)
f.close()

times = [int(x) for x in ''.join(lines[0].split()).split(",")[:-1]]
f = open("schedule_data.txt", "w")
midterm_sheet = {"course code":[], "group":[], "course title":[], "prof. name":[], "date":[], "start time":[], "duration":[], "ex_id":[]}
for i in range(1, len(lines)):
    idx_exam_date = ''.join(lines[i].split()).split(",")[1:-1].index("1.000")
    idx_exam = int(''.join(lines[i].split()).split(",")[0])
    start_h = course_time[idx_exam][int(times[idx_exam_date]) % 7]['start_h']
    start_m = course_time[idx_exam][int(times[idx_exam_date]) % 7]['start_m']
    duration = course_time[idx_exam][int(times[idx_exam_date]) % 7]['duration']
    f.write(f"{times[idx_exam_date]} {start_h} {start_m} {duration} {idx_exam}\n")
    midterm_sheet["ex_id"].append(idx_exam)
    midterm_sheet["course code"].append(course_time[idx_exam]["code"])
    midterm_sheet["course title"].append(course_time[idx_exam]["name"])
    midterm_sheet["date"].append(times[idx_exam_date])
    midterm_sheet["duration"].append(duration)
    midterm_sheet["group"].append(course_time[idx_exam]["group"])
    midterm_sheet["prof. name"].append(course_time[idx_exam]["prof"])
    midterm_sheet["start time"].append(f"{start_h}:{start_m}")
f.close()

new_shit = {}
for i in range(len(midterm_sheet["date"])):
    if (midterm_sheet["date"][i], midterm_sheet["start time"][i], midterm_sheet["duration"][i]) in new_shit:
        new_shit[(midterm_sheet["date"][i], midterm_sheet["start time"][i], midterm_sheet["duration"][i])] += ",{}".format(midterm_sheet["ex_id"][i])
    else:
        new_shit[(midterm_sheet["date"][i], midterm_sheet["start time"][i], midterm_sheet["duration"][i])] = "{}".format(midterm_sheet["ex_id"][i])

f = open("schedule_data.txt", "w")
for k,v in new_shit.items():
    f.write(f"{k[0]} {k[1].split(':')[0]} {k[1].split(':')[1]} {k[2]} {v}\n")
f.close()

df = pd.DataFrame(midterm_sheet)
# writer = pd.ExcelWriter("/home/ostadgeorge/work/python", engine='xlsxwriter')
df.to_csv("midterm_exam.csv")

for input_file, day_label in zip(["schedule_data.txt"], day_labels):
    fig=plt.figure(figsize=(10,5.89))
    for line in open(input_file, 'r'):
        data=line.split()
        event=data[-1]
        data=list(map(float, data[:-1]))
        room=data[0]-0.48
        start=data[1]+data[2]/60
        end=start+data[3]/60
        # plot event
        plt.fill_between([room, room+0.96], [start, start], [end,end], color="pink", edgecolor='k', linewidth=0.5)
        # plot beginning time
        plt.text(room+0.02, start+0.05 ,'{0}:{1:0>2}'.format(int(data[1]),int(data[2])), va='top', fontsize=4)
        # plot event name
        plt.text(room+0.48, (start+end)*0.5, event, ha='center', va='center',rotation=-45, fontsize=8)

    # Set Axis
    ax=fig.add_subplot(111)
    ax.yaxis.grid()
    ax.set_ylim(19.1, 6.9)
    # ax.set_xticks(range(1,len(rooms)+1))
    ax.set_xlim(-1,13)
    ax.set_xticks(range(-1, 13))
    ax.set_yticks(range(7, 19))
    # ax.set_xticklabels(rooms)
    ax.set_ylabel('Time')

    # Set Second Axis
    ax2=ax.twiny().twinx()
    # ax2.set_xlim(ax.get_xlim())
    # ax2.set_ylim(ax.get_ylim())
    # ax2.set_xticks(ax.get_xticks())
    # ax2.set_xticklabels(rooms)
    ax2.set_ylabel('Time')


    plt.title(day_label,y=1.07)
    plt.savefig('{0}.png'.format(day_label), dpi=200)