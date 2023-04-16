from flask import Flask, jsonify

from supabase import create_client, Client

import yaml
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

with open('config.yaml') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

url: str = config['SUPABASE_URL']
key: str = config['SUPABASE_KEY']
supabase: Client = create_client(url, key)

"""
The fetch functions return a list of dictionaries which contain row values
"""
def fetch_schools() -> list:
    res = supabase.table('Schools').select('*').execute()
    return list(res.data)

def fetch_majors(school: int) -> list:
    res = supabase.table('Curriculum').select('*').eq('school', school).eq('type', "major").execute()
    return list(res.data)

def fetch_minors(school: int) -> list:
    res = supabase.table('Curriculum').select('*').eq('school', school).eq('type', "minor").execute()
    return list(res.data)
def fetch_major_by_name(school: int, name: str) -> dict:
    res = supabase.table('Curriculum').select('*').eq('school', school).eq('type', "major").eq('name', name).execute()
    return list(res.data)[0]

def fetch_major_by_id(id: int) -> dict:
    res = supabase.table('Curriculum').select('*').eq('id', id).execute()
    return list(res.data)[0]

def fetch_unique_courses(school: int) -> list:
    res = supabase.table('Courses').select('*').eq('school', school).execute()
    return list(res.data)
def fetch_group(id: int) -> list:
    res = supabase.table('CourseGroups').select('*').eq('id', id).execute()
    return list(res.data)
# Retrieve course from course id (found in curriculum for example)
def get_course(school: int, id: int) -> dict:
    res = supabase.table('Courses').select('*').eq('school', school).eq('id', id).execute()
    return list(res.data)[0]


def corequisites_satisfied(course: dict, current_classes: list, previous_classes: list) -> bool:
    print(course['corequisite'])
    if not course['corequisite']:
        return True
    return all(x in current_classes or x in previous_classes for x in course['corequisite'])

def prerequisites_satisfied(course: dict, passed_classes: list, current_classes: list) -> bool:

    if not course['prerequisite_ids']:
        course['prerequisite_ids'] = []

    if len(course['prerequisite_ids']) == 0:
        return True

    return all(x in passed_classes for x in course['prerequisite_ids'])

def create_schedule(curriculum: dict) -> dict:
    print("test")
    # curriculum:
    # {
    #     name: string,
    #     class_ids: int[],
    #     group_ids: int[],
    #     school: int,
    #     type: string,
    # }

    classes = []
    passed_groups = False
    
    for i in curriculum['class_ids']:
        current = get_course(curriculum['school'], i)
        classes.append(current)
        
    groups = []
    for gid in curriculum['group_ids']:
        groups.append(fetch_group(gid)[0])
    sorted_classes = sorted(
        classes+groups, 
        key=lambda x: int(x['abbr_name'].split(" ")[1] if 'abbr_name' in x else x['level'])
    )
    print(sorted_classes)
    # return {}
    max_iterations = 1000
    passed_classes = []
    semester = 0
    credit_total = 0
    semester_classes = []
    res = []
    while len(sorted_classes) > 0:
        max_iterations -= 1
            
        for cl in sorted_classes:
            if max_iterations == 0:
                semester_classes.append(cl['id'])
                sorted_classes.remove(cl)
                max_iterations = 100
                res.append({
                        "full_name": cl['full_name'],
                        "abbr_name": cl['abbr_name'],
                        "credits": cl['credits'],
                        "semester": semester,
                        "type": "class"
                    })
                print("dumping: ", str(cl))
            if credit_total >= 14:
                semester += 1
                credit_total = 0
                passed_classes += semester_classes
                semester_classes = []

            if 'abbr_name' in cl: # actual class
                # print(cl['abbr_name'])
                if cl['semester'] and "spring" in cl['semester'] and semester % 2 == 0: # wrong semester
                    continue
                if cl['semester'] and "fall" in cl['semester'] and semester % 2 == 1: # wrong semester
                    continue
                # if cl['abbr_name'] == "EECS 581":
                #     print(semester, cl['semester'])
                if prerequisites_satisfied(cl, passed_classes, semester_classes) and corequisites_satisfied(cl, semester_classes, passed_classes):
                    semester_classes.append(cl['id'])
                    sorted_classes.remove(cl)
                    res.append({
                        "full_name": cl['full_name'],
                        "abbr_name": cl['abbr_name'],
                        "credits": cl['credits'],
                        "semester": semester,
                        "type": "class"
                    })
                    credit_total += cl['credits']
                    break
                else:
                    continue
            else: # group
                # print(cl['name'])
                sorted_classes.remove(cl)
                res.append({
                        "full_name": "",
                        "abbr_name": cl['name'],
                        "credits": 3,
                        "semester": semester,
                        "type": "group"
                    })
                # if prerequisites_satisfied(cl, passed_classes)
                credit_total += 3
                break
    # print(sorted_classes)
    return res


@app.route('/')
@cross_origin()
def root_page():
    return 'root'
    # curr = fetch_major_by_name(1, "Computer Science")
    
    # return create_schedule(curriculum=curr)

@app.route('/api/schools')    
@cross_origin()
def get_all_schools():
    return jsonify(fetch_schools())

@app.route('/api/schools/<int:school_id>/majors')
@cross_origin()
def get_school_majors(school_id: int):
    return jsonify(fetch_majors(school_id))

@app.route('/api/schools/<int:school_id>/minors')
@cross_origin()
def get_school_minors(school_id: int):
    return jsonify(fetch_minors(school_id))

@app.route('/api/schedule/<int:school>/<int:major>')
@cross_origin()
def get_schedule(school, major):
    curr = fetch_major_by_id(id=major)
    return jsonify(create_schedule(curr))

if __name__ == "__main__":
    app.run(debug=True)
