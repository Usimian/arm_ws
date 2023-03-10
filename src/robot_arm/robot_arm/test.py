# SDA = pin.SDA_1
# SCL = pin.SCL_1
# SDA_1 = pin.SDA
# SCL_1 = pin.SCL

from adafruit_servokit import ServoKit
import board
import busio
import time
import math
from approxeng.input.selectbinder import ControllerResource

# Calculate servo angles from (x,y,z) end position(mm)
# Returns theta0 (base angle), theta1(lower arm angle), theta2(upper arm angle)
#
def ComputeAngles(x3, y3, z3):

    a2 = 135
    a3 = 147
    # 1
    t1 = math.atan(x3 / y3) * 57.297 + 90
    # 2
    r1 = math.sqrt(x3 * x3 + y3 * y3)
    # 3
    r2 = z3 - 0
    # 4
    p2 = math.atan(r2 / r1) * 57.297
    # 5
    r3 = math.sqrt(r1 * r1 + r2 * r2)
    # 6
    p1 = math.acos((a3 * a3 - a2 * a2 - r3 * r3) / (-2 * a2 * r3)) * 57.297
    # 7
    t2 = p2 + p1
    # 8
    p3 = math.acos((r3 * r3 - a2 * a2 - a3 * a3) / (-2 * a2 * a3)) * 57.297
    # 9
    t3 = 180 - p3

    print(f"x: {x}, y: {y}, z: {z}, p1: {p1}, p2: {p2}, p3: {p3} t1: {t1}, t2: {t2}, t3: {t3}")

    return t1, t2, t3


# On the Jetson Nano
# Bus 0 (pins 28,27) is board SCL_1, SDA_1 in the jetson board definition file
# Bus 1 (pins 5, 3) is board SCL, SDA in the jetson definition file
# Default is to Bus 1; We are using Bus 0, so we need to construct the busio first ...
print("Initializing Servos")
i2c_bus0 = busio.I2C(board.SCL_1, board.SDA_1)
print("Initializing ServoKit")
kit = ServoKit(channels=16, i2c=i2c_bus0)
print("Done initializing")

# Servo numbers
BASE = 3
LOWER_ARM = 2
UPPER_ARM = 1
GRIPPER = 0

# Gripper, UpDown, ForwardBackward, Base swivel
servo_limits_min = [65, 40, 40, -180]  # degrees
servo_limits_max = [180, 120, 175, 180]  # degrees

try:
    # TESTING
    # for y in range(150, 200, 10):
    # y = 200
    # t1, t2, t3 = ComputeAngles(0, y, 100)
    # print(f"x: {0}, y: {y}, z: {0}")
    # print(f"t1: {t1}, t2: {t2}, t3: {t3}")

    v0Old = 0
    v1Old = 0
    v2Old = 0
    v3Old = 0

    while True:
        with ControllerResource() as joystick:
            print(type(joystick).__name__)
            joystick.check_presses()
            while joystick.connected:
                axis_list = ["l", "lt", "lx", "ly", "r", "rt", "rx", "ry"]
                # print(joystick)
                # time.sleep(0.1)
                x = 0
                y = 135
                z = 147
                for axis_name in axis_list:
                    joystick_value = joystick[axis_name]

                    # if axis_name == "ry":
                    #     desired_angle = (-joystick_value + 1) / 2 * 180
                    #     desired_angle = max(min(desired_angle, servo_limits_max[UPPER_ARM]), servo_limits_min[UPPER_ARM])
                    #     kit.servo[UPPER_ARM].angle = desired_angle
                    #     if joystick_value != v1Old:
                    #         print(f"T1: {desired_angle}  UPPER_ARM(ry): {joystick_value}")
                    #         time.sleep(0.1)
                    #         v1Old = joystick_value

                    if axis_name == "ry":
                        # desired_angle = (-joystick_value + 1) / 2 * 180
                        # desired_angle = max(min(desired_angle, servo_limits_max[UPPER_ARM]), servo_limits_min[UPPER_ARM])
                        z = joystick_value / 2.0 * 100 + 135
                        # if joystick_value != v1Old:
                        #     print(f"T1: {desired_angle}  UPPER_ARM(ry): {joystick_value}")
                        #     time.sleep(0.1)
                        #     v1Old = joystick_value

                    if axis_name == "ly":
                        # desired_angle = (-joystick_value + 1) / 2 * 180
                        # desired_angle = max(min(desired_angle, servo_limits_max[UPPER_ARM]), servo_limits_min[UPPER_ARM])
                        y = joystick_value / 2.0 * 100 + 147
                        # if joystick_value != v1Old:
                        #     print(f"T1: {desired_angle}  UPPER_ARM(ry): {joystick_value}")
                        #     time.sleep(0.1)
                        #     v1Old = joystick_value

                    # if axis_name == "ly":
                    #     desired_angle = (-joystick_value + 1) / 2 * 180
                    #     desired_angle = max(min(desired_angle, servo_limits_max[LOWER_ARM]), servo_limits_min[LOWER_ARM])
                    #     kit.servo[LOWER_ARM].angle = desired_angle
                    #     if joystick_value != v2Old:
                    #         print(f"T2: {desired_angle}  LOWER_ARM(ly): {joystick_value}")
                    #         time.sleep(0.1)
                    #         v2Old = joystick_value

                    if axis_name == "lx":
                        # desired_angle = (-joystick_value + 1) / 2 * 180
                        # desired_angle = max(min(desired_angle, servo_limits_max[UPPER_ARM]), servo_limits_min[UPPER_ARM])
                        x = joystick_value / 2.0 * 100
                        # if joystick_value != v1Old:
                        #     print(f"T1: {desired_angle}  UPPER_ARM(ry): {joystick_value}")
                        #     time.sleep(0.1)
                        #     v1Old = joystick_value

                    # if axis_name == "lx":
                    #     desired_angle = (joystick_value + 1) / 2 * 180
                    #     desired_angle = max(min(desired_angle, servo_limits_max[BASE]), servo_limits_min[BASE])
                    #     kit.servo[BASE].angle = desired_angle
                    #     if joystick_value != v3Old:
                    #         print(f"T3: {desired_angle}  BASE(lx): {joystick_value}")
                    #         time.sleep(0.1)
                    #         v3Old = joystick_value

                    if axis_name == "rt":
                        desired_angle = (1 - joystick_value) * 180
                        desired_angle = max(min(desired_angle, servo_limits_max[GRIPPER]), servo_limits_min[GRIPPER])
                        kit.servo[GRIPPER].angle = desired_angle
                        if joystick_value != v0Old:
                            print(f"T0: {desired_angle}  GRIPPER(rt): {joystick_value}")
                            time.sleep(0.1)
                            v0Old = joystick_value

                t1, t2, t3 = ComputeAngles(x, y, z)
                kit.servo[BASE].angle = max(min(t1, servo_limits_max[BASE]), servo_limits_min[BASE])
                kit.servo[LOWER_ARM].angle = max(min(t2, servo_limits_max[LOWER_ARM]), servo_limits_min[LOWER_ARM])
                kit.servo[UPPER_ARM].angle = max(min(t3, servo_limits_max[UPPER_ARM]), servo_limits_min[UPPER_ARM])
                # kit.servo[GRIPPER].angle = max(min(desired_angle, servo_limits_max[GRIPPER]), servo_limits_min[GRIPPER])
                # print(f"x: {0}, y: {147}, z: {120}")
                # print(f"t1: {t1}, t2: {t2}, t3: {t3}")
                time.sleep(0.1)

                # button_list = [
                #     "circle",
                #     "cross",
                #     "ddown",
                #     "dleft",
                #     "dright",
                #     "dup",
                #     "home",
                #     "l1",
                #     "l2",
                #     "ls",
                #     "r1",
                #     "r2",
                #     "rs",
                #     "select",
                #     "square",
                #     "start",
                #     "triangle",
                # ]
                # for button_name in button_list:
                #     button_value = joystick[button_name]

                #     if button_name == "cross":  # close gripper
                #         if button_value:
                #             kit.servo[0].angle = desired_angle = (servo_limits_min[0] + 1) / 2 * 180

                #     if button_name == "circle":  # open gripper
                #         if button_value:
                #             kit.servo[0].angle = desired_angle = (servo_limits_max[0] + 1) / 2 * 180

except KeyboardInterrupt:
    pass

finally:
    print("test has shutdown")
