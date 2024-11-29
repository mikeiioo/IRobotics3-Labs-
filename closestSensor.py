def findClosestSensor(readings):
    max_reading = -1
    sensorIndex = -1

    for i in range(len(readings)):
        if readings[i] >= 20:
            if readings[i] > max_reading:
                max_reading = readings[i]
                sensorIndex = i

    return sensorIndex
