from z_uart import Mars_UART
import time
# 二、定义全局变量
# 1. 定义总线ID号
car_motor_fl = 1  # 小车左前轮电机ID
car_motor_fr = 2  # 小车右前轮电机ID
car_motor_bl = 3  # 小车左后轮电机ID
car_motor_br = 4  # 小车右后轮电机ID

car_servo_fl = 11  # 小车左前轮舵机ID
car_servo_fr = 12  # 小车右前轮舵机ID
car_servo_bl = 13  # 小车左后轮舵机ID
car_servo_br = 14  # 小车右后轮舵机ID

# 2. 定义小车运动参数
car_run_speed = 800  # 小车直行运动速度，范围0~1000us 此数值是PWM输出数值，范围为500us-2500us之间，其中1500us电机停止，大于1500us正转，小于1500us反转
car_run_time = 5000  # 小车直行时间，小车直行时间1000=1s	#运行时间，范围为0000-9999，单位为ms

car_turn_speed = 400  # 小车转弯时的速度
car_turn_angle = 200  # 小车转弯角度，范围0~1000us 此数值是PWM输出数值，偏转PWM=200us，270/2000*200=27度
car_turn_time = 2000  # 小车转弯时间，小车直行时间1000=1s

# 3. 定义底盘转向舵机的初始位置PWM数值，并将测试得到数值对以下数值进行更新
car_servo_fl_init = 1400
car_servo_fr_init = 1600
car_servo_bl_init = 1500
car_servo_br_init = 1500

car_motor_fl_init =1500
car_motor_fr_init =1500
car_motor_bl_init =1500
car_motor_br_init =1500
# 测试底盘转向舵机的初始值 在Z_uart.py程序中运行。先运行整个Z_uart.py，再在命令栏中不断测试。找到舵机对中位置时的PWM数值，在1500附近

# 三、定义函数 
# 1.定义底盘舵机初始化函数，即再一次对中
def car_servos_init():
    Srt = f'#{car_servo_fl:03d}P{car_servo_fl_init:04d}T{1000:04d}!#{car_servo_fr:03d}P{car_servo_fr_init:04d}T{1000:04d}!#{car_servo_bl:03d}P{car_servo_bl_init:04d}T{1000:04d}!#{car_servo_br:03d}P{car_servo_br_init:04d}T{1000:04d}!'
    print(Srt)
    print("Car servos are tunning")
    uart.uart_send_str(Srt)


# 2.小车直行运动函数
def car_run(run_speed, run_time):
    Srt = f'#{car_motor_fl:03d}P{car_motor_fl_init - run_speed:04d}T{run_time:04d}!#{car_motor_fr:03d}P{car_motor_fr_init + run_speed:04d}T{run_time:04d}!#{car_motor_bl:03d}P{car_motor_bl_init - run_speed:04d}T{run_time:04d}!#{car_motor_br:03d}P{car_motor_br_init + run_speed:04d}T{run_time:04d}!'
    print(Srt)
    print("Car is running")
    uart.uart_send_str(Srt)


# 3.定义小车转弯运动  
def car_turn(turn_angle, turn_time):
    Srt = f'#{car_servo_fl:03d}P{car_servo_fl_init - turn_angle:04d}T{turn_time:04d}!#{car_servo_fr:03d}P{car_servo_fr_init - turn_angle:04d}T{turn_time:04d}!#{car_servo_bl:03d}P{car_servo_bl_init + turn_angle:04d}T{turn_time:04d}!#{car_servo_br:03d}P{car_servo_br_init + turn_angle:04d}T{turn_time:04d}!'
    print(Srt)
    print("Car is turning")
    uart.uart_send_str(Srt)


# 4.小车运动+转向
def car_run_and_turn(run_speed, turn_angle, run_time):
    Srt = f'#{car_motor_fl:03d}P{car_motor_fl_init - run_speed:04d}T{run_time:04d}!#{car_motor_fr:03d}P{car_motor_fr_init + run_speed:04d}T{run_time:04d}!#{car_motor_bl:03d}P{car_motor_bl_init - run_speed:04d}T{run_time:04d}!#{car_motor_br:03d}P{car_motor_br_init + run_speed:04d}T{run_time:04d}!#{car_servo_fl:03d}P{car_servo_fl_init - turn_angle:04d}T{run_time:04d}!#{car_servo_fr:03d}P{car_servo_fr_init - turn_angle:04d}T{run_time:04d}!#{car_servo_bl:03d}P{car_servo_bl_init + turn_angle:04d}T{run_time:04d}!#{car_servo_br:03d}P{car_servo_br_init + turn_angle:04d}T{run_time:04d}!'
    print(Srt)
    print("Car is running and turning")
    uart.uart_send_str(Srt)


# 5.小车停止函数 #停止车轮和转向
def car_stop():
    Srt = f'#{car_motor_fl:03d}P{car_motor_fl_init}T1000!#{car_motor_fr:03d}P{car_motor_fr_init}T1000!#{car_motor_bl:03d}P{car_motor_bl_init}T1000!#{car_motor_br:03d}P{car_motor_br_init}T1000!#{car_servo_fl:03d}P{car_servo_fl_init}T1000!#{car_servo_fr:03d}P{car_servo_fr_init}T1000!#{car_servo_bl:03d}P{car_servo_bl_init}T1000!#{car_servo_br:03d}P{car_servo_br_init}T1000!'
    print(Srt)
    print("Car is stopping")
    uart.uart_send_str(Srt)


if __name__ == "__main__":
    #     global uart,car_run_speed,car_run_time,car_turn_angle,car_turn_time
    uart = Mars_UART()  # 实例化串口对象

    # 先对底盘舵机初始值-程序对中
    car_servos_init()

    car_stop()
    time.sleep(2)

    # 小车前进运动
    car_run(car_run_speed, car_run_time)  # 前进
    time.sleep(2)

    car_stop()
    time.sleep(2)

    # 小车后退运动
    car_run(-car_run_speed, car_run_time)  # 后退
    time.sleep(2)

    car_stop()
    time.sleep(2)

    # 小车仅转向运动
    car_turn(car_turn_angle, car_turn_time)
    time.sleep(2)

    car_stop()
    time.sleep(2)

    # 小车仅转向运动
    car_turn(-car_turn_angle, car_turn_time)
    time.sleep(2)

    car_stop()
    time.sleep(2)

    # 小车运动+转向运动
    car_run_and_turn(car_run_speed, car_turn_angle, car_turn_time)
    time.sleep(2)

    car_stop()
    time.sleep(2)

    car_run_and_turn(car_run_speed, -car_turn_angle, car_turn_time)
    time.sleep(2)

    car_stop()
    time.sleep(2)
