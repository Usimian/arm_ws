#
# 3D printed robot arm controller
#
from adafruit_servokit import ServoKit
import board
import busio
import time
import math
from approxeng.input.selectbinder import ControllerResource

# Calculate servo angles from (x,y,z) end position(mm)
# Returns theta1(base angle), theta2(lower arm angle), theta3(upper arm angle)
#
def ComputeAngles(x, y, z):

    a2 = 135
    a3 = 147
    # 1
    t1 = math.atan(x / y) * 57.297 + 90
    # 2
    r1 = math.sqrt(x * x + y * y)
    # 3
    r2 = z - 0
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
    t3 += 90 - t2  # adjust for lower arm linkage to upper arm

    # print(f"x: {x}, y: {y}, z: {z}, p1: {p1}, p2: {p2}, p3: {p3} t1: {t1}, t2: {t2}, t3: {t3}")

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
    while True:
        with ControllerResource() as joystick:
            print(type(joystick).__name__)
            joystick.check_presses()
            while joystick.connected:
                # axis_list = ["l", "lt", "lx", "ly", "r", "rt", "rx", "ry"]    # Full analog control list
                axis_list = ["lx", "ly", "rt", "ry"]    # Controls used
                for axis_name in axis_list:
                    joystick_value = joystick[axis_name]

                    # X - Axis
                    if axis_name == "lx":   # Left stick X
                        x = joystick_value * 100

                    # Y - Axis
                    if axis_name == "ry":   # Right stick Y
                        y = -joystick_value * 100.0 + 147

                    # Z - Axis
                    if axis_name == "ly":   # Left stick Y
                        z = -joystick_value * 100.0 + 107

                    # Gripper
                    if axis_name == "rt":   # Right trigger
                        desired_angle = (1 - joystick_value) * 180
                        desired_angle = max(min(desired_angle, servo_limits_max[GRIPPER]), servo_limits_min[GRIPPER])
                        kit.servo[GRIPPER].angle = desired_angle

                t1, t2, t3 = ComputeAngles(x, y, z)
                t_base = t1
                t_lower_arm = 180 - t2
                t_upper_arm = 180 - t3
                kit.servo[BASE].angle = max(min(t_base, servo_limits_max[BASE]), servo_limits_min[BASE])
                kit.servo[LOWER_ARM].angle = max(min(t_lower_arm, servo_limits_max[LOWER_ARM]), servo_limits_min[LOWER_ARM])
                kit.servo[UPPER_ARM].angle = max(min(t_upper_arm, servo_limits_max[UPPER_ARM]), servo_limits_min[UPPER_ARM])
                # print(f"x: {x:.2f}, y: {y:.2f}, z: {z:.2f}, t1: {t_base:.2f}, t2: {t_lower_arm:.2f}, t3: {t_upper_arm:.2f}")
                # time.sleep(0.1)

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
