def get_pixhawk_data(master):
    try:
        gps_data = master.recv_match(type='GLOBAL_POSITION_INT', blocking=True, timeout=1)
        if gps_data is None:
            print("GPS NONE")
        imu_data = master.recv_match(type='SCALED_IMU2', blocking=True, timeout=1)
        if imu_data is None:
            print("IMU NONE")
        att_data = master.recv_match(type='ATTITUDE', blocking=True, timeout=1)
        if att_data is None:
            print("GPS NONE")
        data = {
            "gps_data": gps_data.to_dict(),
            "imu_data": imu_data.to_dict(),
            "att_data": att_data.to_dict()
        }
        return data
    except Exception as e:
        print(e)
        return None
