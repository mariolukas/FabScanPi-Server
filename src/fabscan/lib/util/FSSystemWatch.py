
def get_cpu_temperature():
    with open("/sys/class/thermal/thermal_zone0/temp") as tmpFile:
        cpu_temp = tmpFile.read()
        cpu_temp = float(cpu_temp) / 1000
        cpu_temp = float("{0:.2f}".format(cpu_temp))
    return cpu_temp