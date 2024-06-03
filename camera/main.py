import autopilot as ap
import capture as cap
import localizer as loc

import time

if __name__ == "__main__":
    print("Starting localization sequence.")
    time.sleep(5)
    apm = ap.Autopilot(ap.SERIAL_PORT, ap.DEFAULT_BAUD_RATE)
    apm.set_mode_alt_hold()

    save_dir = "temp"
    sr = cap.SensorReader(apm, save_dir=save_dir)

    target_ids = [
        {
            "name": "target_n",
            "path": "targets/target_n_small.jpg"
        },
        {
            "name": "target_r",
            "path": "targets/target_r_small.jpg"
        }
    ]
    lc = loc.Localizer(sr, target_ids, save_dir)
    lc.localize_while_armed()