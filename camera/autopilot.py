from pymavlink import mavutil
from threading import Thread
import time

SERIAL_PORT = "/dev/ttyTHS1"
USB_PORT = "/dev/ttyACM0"
DEFAULT_BAUD_RATE = 57600
MSG_FREQ_HZ = 20
# MSG_FREQ_HZ = 50

class Autopilot:
    def __init__(self, connection_url, baudrate):
        self.connection_url = connection_url
        self.baudrate = baudrate
        self.init_connection()
        self.set_message_frequency()

    def init_connection(self):
        conn = mavutil.mavlink_connection(self.connection_url, baud=self.baudrate)
        
        conn.mav.heartbeat_send(0, 0, 0, 0, 0)
        print(f"Waiting from heartbeat from {self.connection_url}")
        conn.wait_heartbeat()
        print(f"Heartbeat from system (system {conn.target_system}, component {conn.target_component})")
        self.conn = conn

        self.read_thread = Thread(target=self.update_messages, args=())
        self.read_thread.daemon = True
        self.read_thread.start()

    def update_messages(self):
        while True:
            self.conn.recv_msg()

    def set_message_frequency(self):
        # We need to get GPS, IMU and Attitude data
        msg_ids = [
            mavutil.mavlink.MAVLINK_MSG_ID_GLOBAL_POSITION_INT,
            mavutil.mavlink.MAVLINK_MSG_ID_SCALED_IMU2,
            mavutil.mavlink.MAVLINK_MSG_ID_ATTITUDE
        ]

        for msg_id in msg_ids:
            self.conn.mav.command_long_send(
                self.conn.target_system,
                self.conn.target_component,
                mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,
                0,
                msg_id,
                int(1000000 / MSG_FREQ_HZ),
                0, 0, 0, 0, 0
            )
    
    def get_data(self):
        required_messages = [
            ("gps", "GLOBAL_POSITION_INT"),
            ("imu", "SCALED_IMU2"),
            ("attitude", "ATTITUDE")
        ]
        data = {}
        for name, msg_type in required_messages:
            msg = self.conn.messages[msg_type]
            data[name] = msg.to_dict()
        return data

    def is_armed(self):
        return self.conn.motors_armed()

    def set_mode_alt_hold(self):
        alt_hold_mode = 2
        self.conn.mav.set_mode_send(
            self.conn.target_system,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            alt_hold_mode
        )

        ack = self.conn.recv_match(type="COMMAND_ACK", blocking=True)
        if ack and ack.command == mavutil.mavlink.MAV_CMD_DO_SET_MODE and ack.result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
            print("Mode changed to ALT_HOLD succesfully.")
        else:
            print("Failed to change mode to ALT_HOLD.")
        
if __name__ == "__main__":
    autopilot = Autopilot(SERIAL_PORT, DEFAULT_BAUD_RATE)
    # autopilot = Autopilot(USB_PORT, DEFAULT_BAUD_RATE)
    while True:
        # start = time.time()
        data = autopilot.get_data()
        # end = time.time()
        # print(end - start)
        print(data["gps"])
        time.sleep(1)