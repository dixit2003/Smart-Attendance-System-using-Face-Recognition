import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("C:\\Users\\Sai Dixit\\PycharmProjects\\FacialAttendanceSystem\\serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendancesystem-a2c47-default-rtdb.firebaseio.com/"
})

ref = db.reference('Students')

data = {
    "0128":
        {
            "name": "Sai Dixit Vila",
            "major": "Mtech5 SE",
            "starting_year": 2020,
            "total_attendance": 0,
            "progress": "G",
            "year": 0,
            "last_attendance_time": "2023-11-1 00:00:00"
        },
    "0255":
        {
            "name": "Shashwat",
            "major": "Mtech5 SE",
            "starting_year": 2020,
            "total_attendance": 0,
            "progress": "B",
            "year": 4,
            "last_attendance_time": "2023-11-1 00:00:00"
        },
    "368745":
        {
            "name": "Jennifer",
            "major": "Physics",
            "starting_year": 2021,
            "total_attendance": 0,
            "progress": "G",
            "year": 2,
            "last_attendance_time": "2023-11-1 00:00:00"
        },
    "815283":
        {
            "name": "Jefferson",
            "major": "IT",
            "starting_year": 2019,
            "total_attendance": 0,
            "progress": "B",
            "year": 4,
            "last_attendance_time": "2023-11-1 00:00:00"
        },
    "963852":
        {
            "name": "Elon Musk",
            "major": "BTech CSE",
            "starting_year": 2019,
            "total_attendance": 0,
            "progress": "G",
            "year": 4,
            "last_attendance_time": "2023-11-1 00:00:00"
        },
    # "0116":
    #     {
    #         "name": "Kumar Shivam",
    #         "major": "Mechanical",
    #         "starting_year": 2019,
    #         "total_attendance": 0,
    #         "progress": "G",
    #         "year": 4,
    #         "last_attendance_time": "2023-11-1 00:00:00"
    #     }

}

for key, value in data.items():
    ref.child(key).set(value)
