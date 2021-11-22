from gams import *
from time_travel import *
import pandas as pd
import numpy as np
import os

weeks_no = 4 # weeks
T = weeks_no * 7  # days
exclude_problematic_students = False
idx_to_cg = {}
cg_to_idx = {}
idx_students = []
BASE_DIR = os.path.dirname(os.path.realpath(__file__))

def read_problematic_students(n):
    f = open("problematic_students.txt","r")
    mask = np.zeros((n,))
    for line in f.readlines():
        mask[int(line)] = 1
    return mask

if __name__ == "__main__":
    runAsAdmin()
    if isAdmin():
        setTime()

        try:
            courses_df = pd.read_excel("data.xlsx", "Courses", engine='openpyxl')
            R, _ = courses_df.shape

            student_df = pd.read_excel("data.xlsx", "List", engine='openpyxl')#.iloc[:14, :] # Limited Students
            N, _ = student_df.shape

            p = np.zeros([R, T])
            a = np.zeros([N, R])
            idx_courses = np.arange(R)
            idx_times = np.arange(T)

            for row in courses_df.iterrows():
                idx = int(row[1][0]) - 1
                cg_to_idx[(int(row[1][1]), int(row[1][3]))] = idx
                idx_to_cg[idx] = (int(row[1][1]), int(row[1][3]))
                for x in [4, 5]:
                    if len(str(row[1][x])) < 4: continue
                    if "يک" in row[1][x].split("[")[0]:
                        for t in range(T):
                            if t % 7 == 1:
                                p[idx, t] = 1
                    elif "دو" in row[1][x].split("[")[0]:
                        for t in range(T):
                            if t % 7 == 2:
                                p[idx, t] = 1
                    elif "سه" in row[1][x].split("[")[0]:
                        for t in range(T):
                            if t % 7 == 3:
                                p[idx, t] = 1
                    else:
                        for t in range(T):
                            if t % 7 == 0:
                                p[idx, t] = 1

            for row in student_df.iterrows():
                idx = int(row[1][0]) - 1
                idx_students.append(idx)
                course_code = int(row[1][2])
                course_group = int(row[1][3])
                course_idx = cg_to_idx[(course_code, course_group)]
                a[idx, course_idx] = 1

            # Excluding problematic students
            idx_students = np.arange(len(set(idx_students)))
            #print("before",idx_students[-50:])
            if(exclude_problematic_students):
                students_num = idx_students.shape[0]
                mask = read_problematic_students(students_num)
                idx_students = np.ma.array(idx_students,mask=mask)
            #print("after",idx_students[-50:])



            ws = GamsWorkspace(working_directory=BASE_DIR)

            db = ws.add_database()

            i = db.add_set("i", 1, "courses")
            for course in idx_courses:
                i.add_record(str(course))

            j = db.add_set("j", 1, "students")
            for student in idx_students:
                if str(student) != "--":
                    j.add_record(str(student))

            t = db.add_set("t", 1, "times")
            for time in idx_times:
                t.add_record(str(time))

            p_param = db.add_parameter_dc("p", [i, t], "course i in time t")
            for course in idx_courses:
                for time in idx_times:
                    p_param.add_record([str(course), str(time)]).value = p[course, time]

            a_param = db.add_parameter_dc("a", [j, i], "student j takes course i")
            for course in idx_courses:
                for student in idx_students:
                    if str(student) != "--":
                        a_param.add_record([str(student), str(course)]).value = a[student, course]

            job = ws.add_job_from_file("project1.gms")
            opt = ws.add_options()
            opt.defines["gdxincname"] = db.name
            job.run(opt, databases=db)

            q = {}
            for rec in job.out_db["q"]:
                if rec.level > 0:
                    q[(str(rec.key(0)),str(rec.key(1)))] = rec.level

            for j in idx_students: #j
                if str(j) != "--":
                    for t in range(T): #t
                        c = 0
                        for i in idx_courses: #i
                            if a[j, i] == 1 and (str(i),str(t)) in q:
                                c += q[(str(i),str(t))]
                        if c > 0:
                            print(f"C[{j}][{t}] = {c}")
                print("*" * 5)



        except Exception as e:
            print(e)

        finally:
            syncTime()
            input('Press Enter to Exit...')

