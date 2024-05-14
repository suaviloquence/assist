import requests
import json

UCSC = 132
YR = 74

def url(yr, from_id, to_id, dept_id=-1, all=False):
    dept_s = "AllDepartments" if all else f"/Department/{dept_id}/"
    return f"https://assist.org/api/articulation/Agreements?Key={yr}/{from_id}/to/{to_id}/{dept_s}"


def get(i, dept):
    print(i)
    if i == UCSC: return
    al = dept == 'all'
    resp = requests.get(url(YR, i, UCSC, dept, all=al))
    if not resp.ok: return

    js = resp.json()

    # with open(f"{dept}.{i}.res", 'w') as fp:
    #     json.dump(js['result'], fp)

    read(js['result'], al)

def read(res, al=False):
    global arties
    name = res['name']
    receivingInstitution = json.loads(res['receivingInstitution'])
    sendingInstitution = json.loads(res['sendingInstitution'])
    print(f"{sendingInstitution['id']} {sendingInstitution['names'][0]['name']}")

    def get_dept(ars):
        parsed_arties = {}
        for arty in ars:
            def get_item(item):
                if 'type' not in item or item['type'] == "Course":
                    return f"{item['prefix']} {item['courseNumber']} ({item['courseTitle']})"
                if item['type'] == "CourseGroup":
                    a = [get_item(i) for i in item['items']]
                    b = f" {item['courseConjunction']} "
                    return f"({b.join(a)})"
                
                assert False

            # {'type': 'Series', 'series': {'conjunction': 'And', 'name': 'STAT 7, STAT 7L', 'courses': [{'id': 'a17b9d9b-3677-44c3-9171-217ee8ea2781', 'position': 0, 'courseIdentifierParentId': 277266, 'courseTitle': 'Statistical Methods for the Biological, Environmental, and Health Sciences', 'courseNumber': '7', 'prefix': 'STAT', 'prefixParentId': 16616, 'prefixDescription': 'Statistics', 'departmentParentId': 13762, 'department': 'Statistics', 'begin': 'F2019', 'end': '', 'minUnits': 5.0, 'maxUnits': 5.0}, {'id': 'fa6415d6-69c1-41a2-8d6d-8b8672e2878b', 'position': 1, 'courseIdentifierParentId': 128000, 'courseTitle': 'Statistical Methods for the Biological, Environmental, and Health Sciences Laboratory', 'courseNumber': '7L', 'prefix': 'STAT', 'prefixParentId': 16616, 'prefixDescription': 'Statistics', 'departmentParentId': 13762, 'department': 'Statistics', 'begin': 'F2019', 'end': '', 'minUnits': 2.0, 'maxUnits': 2.0}]}, 'visibleCrossListedCourses': [], 'seriesAttributes': None, 'courseAttributes': None, 'sendingArticulation': None, 'templateOverrides': None, 'attributes': None, 'receivingAttributes': None}
            to_course = None
            if 'course' in arty:
                to_course = get_item(arty['course'])
            elif 'series' in arty:
                sr = arty['series']
                to_course = f" {sr['conjunction']} ".join([get_item(i) for i in sr['courses']])
            l = f"{to_course} <- "
            from_courses = ""
            # TODO: this will break on UCSC series courses (e.g., you get credit for FREN 1 and 2 by taking
            # FRENCH 101, 102, and 103 at your cc)
            if arty['sendingArticulation']:
                from_courses = " OR ".join([get_item(item) for item in arty['sendingArticulation']['items']])
                l += from_courses
            else:
                from_courses = None
                l += "None"
            print(l)
            parsed_arties[to_course] = from_courses
        return parsed_arties
        

    articulations = json.loads(res['articulations'])
    parsed_arties = {}
    
    if al:
        for dept in articulations:
            print(dept['name'])
            parsed_arties[dept['name']] = get_dept(dept['articulations'])

            print("\n")
    else:
        parsed_arties = get_dept(articulations)

    print("\n\n")
    arties[sendingInstitution['id']] = parsed_arties

def pad(s):
    return f" {s} "

def get_ge(from_id):
    # TODO: is this uuid constant by year/institution?
    res = requests.get(f"https://assist.org/api/articulation/Agreements?Key={YR}/{from_id}/to/{UCSC}/GeneralEducation/21ec3bad-8a12-407a-b843-89a413ee0729")
    print(from_id)
    if not res.ok: return
    js = res.json()

    parsed = {}
    res = json.loads(js['result']['articulations'])
    for area in res:
        ar = area['articulation']
        name = ar['generalEducationArea']['name']
        classes = [pad(gp['courseConjunction']).join([f"{crs['prefix']} {crs['courseNumber']} ({crs['courseTitle']})" for crs in gp['items']]) for gp in ar['sendingArticulation']['items']]
        print(f"{name} <- {' | '.join(classes)}")
        parsed[name] = classes


    return parsed



        



        
    

arties = {}

# For me the fastest way to get the department ID was to use the inspector tool
# while clicking the agreement between a random CC and UCSC
# you can also use https://assist.org/api/agreements?receivingInstitutionId=132&sendingInstitutionId=58&academicYearId=74&categoryCode=dept
# where 58 is an arbitrary cc
dept = input("dept: ")

try:
    with open(f"dept-{dept}.json", "r") as fp:
        arties = json.load(fp)
except:
    arties = {}

# ranges: https://assist.org/api/institutions
for i in range(int(input("≤: ")), int(input(">: "))):
    if dept == 'ge':
        arties[i] = get_ge(i)
    else:
        get(i, dept)

with open(f"dept-{dept}.json", "w") as fp:
    json.dump(arties, fp, indent=4)
# with open("132.res", "r") as fp:
    # read(json.load(fp))
