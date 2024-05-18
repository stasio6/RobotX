def get_pixhawk_data(master):
    try:
        #pos_data = master.recv_match(type='LOCAL_POSITION_NED', blocking=True, timeout=1)
        #gps_data = master.messages['GLOBAL_POSITION_INT']
        #gps_data = master.messages['SCALED_IMU2']
        #gps_data = master.messages['ATTITUDE']
        print("DBG: GETTING PIXHAWK DATA")       
        pass
        gps_data = master.recv_match(type='GLOBAL_POSITION_INT', blocking=True, timeout=1)
        imu_data = master.recv_match(type='SCALED_IMU2', blocking=True, timeout=1)
        att_data = master.recv_match(type='ATTITUDE', blocking=True, timeout=1)
        data = {
            "gps_data": gps_data.to_dict(),
            "imu_data": imu_data.to_dict(),
            "att_data": att_data.to_dict(),
        }
        return data
    except Exception as e:
        print(e)
        return None
