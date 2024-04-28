import numpy

def match_car(person):
    eqa = [3,3,1,4,1,3,3,5,5,3,2,3,3,3]
    eqb = [3,3,1,4,2,3,3,5,5,3,3,3,3,3]
    eqel = [4,3,2,3,3,3,3,4,4,3,2,3,3,4]
    eqes = [4,3,3,2,4,3,3,4,3,3,4,3,3,4]
    eqsl = [4,4,4,2,4,3,3,3,3,3,1,3,3,5]
    eqss = [3,3,4,2,4,3,3,4,3,3,3,3,3,5]
    eqg = [3,3,5,3,2,3,3,1,2,3,2,3,3,2]
    eqs_may = [5,4,5,3,5,3,3,2,1,3,1,3,3,4]
    eqv = [2,3,3,3,3,3,3,3,3,3,5,3,3,1]
    eqt = [2,3,1,5,2,3,3,3,5,3,5,3,3,1]


    cars = [
        (numpy.array(eqa), "eqa"),
        (numpy.array(eqb), "eqb"),
        (numpy.array(eqel), "eqel"),
        (numpy.array(eqes), "eqes"),
        (numpy.array(eqsl), "eqsl"),
        (numpy.array(eqss), "eqss"),
        (numpy.array(eqg), "eqg"),
        (numpy.array(eqs_may), "eqs_may"),
        (numpy.array(eqv), "eqv"),
        (numpy.array(eqt), "eqt"),
        ]

    gewichtung = [1,1,1,1,2,1,1,2,2,1,2,1,1,1]

    ret = []
    for car in cars:
        delta = numpy.linalg.norm((car[0]-numpy.array(person))*gewichtung)
        ret.append((delta,car[1]))

    return sorted(ret)



def get_full_name(car_code):
    cars_full_names = {
        "eqa": "Mercedes-Benz EQA (Compact SUV)",
        "eqb": "Mercedes-Benz EQB (Compact SUV)",
        "eqel": "Mercedes-Benz EQE (Electric Sedan)",
        "eqes": "Mercedes-Benz EQE SUV (Electric SUV)",
        "eqsl": "Mercedes-Benz EQS Sedan (High-End Luxury Electric Sedan)",
        "eqss": "Mercedes-Benz EQS SUV (Luxury Electric SUV)",
        "eqg": "Mercedes-Benz EQG (Electric Version of G-Class SUV)",
        "eqs_may": "Mercedes-Benz EQS (Extended Range Version)",
        "eqv": "Mercedes-Benz EQV (Electric Version of V-Class Van)",
        "eqt": "Mercedes-Benz EQT (Compact Van)"
    }

    return cars_full_names.get(car_code, "Unknown car model")
