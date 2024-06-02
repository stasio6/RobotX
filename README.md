# RobotX Search and Report Pipeline Documentation

This document will explain the overarching functionality of the code and also explain the individual modules in the code and their functionality.

## Pipeline Overhead View

The pipeline or `capture pipeline` to be precise is the main module of the search and report codebase. 

The goal is to periodically capture the environment, detect the targets, locate them in real GPS coordinates, and then finally report them to the base. 

### 1. Capturing Environment

Our initial strategy was to take a live feed from the jetson usb camera and run a YOLOv8 model on the live feed. The Jetson Nano's compute limitations caused the data to be processed at about 5 seconds per frame (0.2 FPS). This abysmal perfomance forced us to reconsider and pivot. We swapped out the YOLOv8 model with a custom CV image matching algorithm for much better performance.

To control the capture manually, we replaced the live feed with the function `cam/capture_image` to periodically capture a frame when required.

When the frame is captured, we also keep track of the GPS coordinates of the drone and the pose of the drone using the IMU. We save this information for later use and the captured frame is then sent to the target detection section.

### 2. Target Detection

When our pipeline starts, we first load in the target reference images for target detection. This allows us to load them once and keep them in memory which gives us a massive performance boost.

Our target detection CV algorithm is an image matching algorithm, broken down into two steps:

a) **Feature Extraction** <br>
b) **Feature Matching**

For feature extraction, we use the SIFT algorithm. We tested SURF, SIFT, and ORB algorithms. We found out that SIFT offers a nice balance of ease of use, speed, and transformational invariance. 

For feature matching, we use a custom matching algorithm. We initially used a KNN but discovered that it was too slow, it forced us to pivot to a custom algorithm.

Once the features were extracted and the objects were detected, the target detector would return the image coordinates of the detected targets' corners. 

This data is then sent to the localisation pipeline.

### 3. Target Localisation

Using the drone pose from the IMU, the GPS coordinates of the images, the GPS coordinates of the boundary, and the image coordinates of the detected images, we're able to localise the actual GPS coordinates of the targets using 3D view reconstruction. We then aggregate the data for final transmission.

### 4. Data Aggregation & Reporting

We collect a bunch of data points, remove the outliers, and then finally send them to the base.

## Requirements

- Pixhawk
- Python3
- Docker w/ Ubuntu 20.04 (to debug mavlink/optional)
- pip: pymavlink
- pip: opencv
- pip: opencv-contrib
- pip: scipy
- pip: numpy

## Usage Guide

| Argument | Description | Type | Default | Example Value |
|----------|-------------|------|---------|---------------|
| `--pixhawk-url` | The Pixhawk Device URL | String | `PIXHAWK_URL` | /dev/ttyTHS1 |
| `--interval` | Delay between each frame capture | Float | `PIPELINE_INTERVAL_DELAY_S` | 0.5 |
| `--num-captures` | Maximum number of captures | Int | `PIPELINE_NUM_MAX_CAPTURES` | 10 |
| `--image-root` | Root directory to store the captured frames | String | `PIPELINE_IMAGE_PATH_PREFIX` | /images/ |
| `--json-root` | Root directory to store the json metadata for captures (GPS, IMU, etc) | String | `PIPELINE_JSON_PATH_PREFIX` | /json/ |
| `--save-prefix` | Prefix string for each save json/img | String | `PIPELINE_SAVE_PREFIX` | (empty) |
| `--target-n` | Path to the "N" robot target | String | `PIPELINE_TARGET_N_PATH` | /targets/target_n.jpg |
| `--target-r` | Path to the "R" robot target | String | `PIPELINE_TARGET_R_PATH` | /targets/target_r.jpg |
| `--color` | Controls whether the frames are captured in color | Boolean | `PIPELINE_IMAGE_COLOR` | TRUE |
| `--clean` | Clean the previous captured data | Boolean (Positional) | `FALSE` | (positional) |
| `--picture-only` | Only capture the pictures (no target detection/localisation) | Boolean (Positional) | `FALSE` | (positional) |
| `--test-mode` | Process pre-captured image data | Boolean (Positional) | `FALSE` | (positional) |

## Code Documentation

For the purposes of this documentation, `/camera/` will be considered the root of the project. 

If you're unsure of what you're doing, we highly recommend you only interact with the contents of module `/camera/capture_pipeline.py`. It has everything necessary to perform E2E capture to reporting.

Only functions and classes mentioned in this documentation should be interacted with directly, changing other parts of the code can lead to undefined behaviour and thus are not documented.

### Changing Default Values

Constant values like `PIPELINE_JSON_ROOT` can be found under `capture_pipeline.py`. This file is also the root file which should be invoked using python to run the pipeline script.

### Class Descriptions

`SetInterval (interval: Float, action: cb)`

For every `interval` seconds, the `cb` function will be called. If the `cb` needs additional state variables, it needs to be a closure that closes some other function's state. You can invoke the interval from within that function.

### Function Descriptions

**`cam.py`**

- `main`

  - If the module is evoked as a script, then the main function is called. We do not recommend starting this module as a script since it can interfere with some global interval states used in the main pipeline script. To know about the script arguments, the `--help` flag will report the available options with helpful hints.

- `capture_image`

  - By default captures a color 1920x1080 image. You can pass in a `(width: Int, height: Int)` tuple to change the resolution. The captured image is returned as a cv matrix object which can be directly converted into a numpy matrix.

- `save_image(path: String)`

  - Internally calls `capture_image` and saves the image to the path string.


`cv_utilities.py`

These are some useful functions that can be used independently of the pipeline with minor adjustments. This goes into a bit more of a technical detail given its utility.

- `load_target_image(path: String)`
  - Loads a target image from the specified file path. It reads the image in grayscale format using OpenCV's `cv2.imread` function with the `cv2.IMREAD_GRAYSCALE` flag. If `TARGET_IMAGE_SIZES` is not `None`, it resizes the image to the specified dimensions. Finally, it returns the loaded target image.

- `load_camera_image(path: String, useColor: Boolean = False)`
  - Loads a camera image from the specified file path. If `useColor` is `True`, it reads the image in color format using OpenCV's `cv2.imread` function with the `cv2.IMREAD_COLOR` flag. If `useColor` is `False` (default), it reads the image in grayscale format using the `cv2.IMREAD_GRAYSCALE` flag. It returns the loaded camera image.

- `normalize_corners(corners: List)`
  - Normalizes the corners by extracting the first element of each corner if it is a list or a NumPy array. It returns the normalized corners as a list.

- `prepare_target_images(target_images: List, calculate_key_descriptors: Function)`
  - Prepares the target images for localization and object detection. If `TARGET_IMAGES_LOAD_FROM_FILE` is `True`, it loads each target image from the specified file path using `load_target_image`, calculates its key descriptors using the provided `calculate_key_descriptors` function, and stores the descriptors and image shape in the corresponding target image dictionary. If `TARGET_IMAGES_LOAD_FROM_FILE` is `False`, it loads the target images from a pickle file specified by `TARGET_IMAGES_PICKLE_PATH`. It returns the prepared target images.

- `detect_optimal_corners(img: Image, camera_image_path: String = None)`
  - Detects optimal corners in the input image using OpenCV's `cv2.goodFeaturesToTrack` function. It converts the image to grayscale using `cv2.cvtColor` with the `cv2.COLOR_BGR2GRAY` flag, detects corners using `cv2.goodFeaturesToTrack` with the specified parameters `CV_NUMBER_CORNERS_DETECTED`, `CV_CORNERS_QUALITY_LEVEL`, and `CV_CORNERS_MIN_DISTANCE`, refines the detected corners to subpixel accuracy using `corners_to_subpix2`, and returns the normalized corners using `normalize_corners`.

- `corners_to_subpix2(img: Image, corners: List)`
  - Refines the corners to subpixel accuracy using OpenCV's `cv2.cornerSubPix` function. It sets the termination criteria using `cv2.TERM_CRITERIA_EPS` and `cv2.TERM_CRITERIA_MAX_ITER` and returns the refined corners.

- `get_closest_corners(targets: List, corners: List, max_dist: Float = CV_CORNERS_MATCHING_MAX_DISTANCE)`
  - Finds the closest corners to the target points. It iterates over each target point and finds the closest corner within the specified maximum distance `max_dist`. It returns a list of the closest corners corresponding to each target point.

- `detect_polygon_corners(img: Image)`
  - Detects polygon corners in the input image using OpenCV's contour detection. It converts the image to grayscale using `cv2.cvtColor` with the `cv2.COLOR_BGR2GRAY` flag, applies binary thresholding using `cv2.threshold` with the specified `CV_POLYGON_BW_THRESHOLD`, finds contours in the thresholded image using `cv2.findContours`, filters contours based on the number of points and approximates polygons using `cv2.approxPolyDP`, and if a contour has 4 points and its bounding rectangle dimensions exceed `CV_MIN_POLYGON_DETECTED`, considers it a valid polygon and adds its corners to the result. Finally, it returns the detected polygon corners.

`capture_pipeline.py`

- `main`

  - If the module is evoked as a script, the main function is called. The available options were mentioned in the Usage Guide table above. If you still need a reference, you can provide the `--help` flag for a detailed description.

- `pipeline(iter_count: Int, target_objs: Dictionary)`

  - This should primarily be evoked by the `execute_pipeline` function which sets up the required objects and interval timers for the iteration counters. This simply runs one iteration of the pipeline.

- `execute_pipeline`

  - Sets up the Interval timer and preloads the target images for localisation and object detection. It precomputes the features for the target images to save compute time during the pipeline. The `pipeline` function acts as a closure over the state variables defined under `execute_pipeline`, specifically the setup objects for use with the Interval timer.

- `get_cam_metadata`

  - Gets the IMU, GPS, and attitude data from the pixhawk.

`pixhawk_utils.py`

- `get_pixhawk_data(master: MavlinkConnectionObject)`

  - For example of how to get the master object, check out the `get_cam_metadata` function in the pipeline code. This function uses the master object to retrieve the IMU, GPS, and attitude data from the Pixhawk.

`object_detection.py`

- `detect_all_targets(image_data: Dictionary, target_objs: List[Dictionary])`

  - The **image data** should contain the following fields:

    - `image` cv2 Image Object
    - `path` String path where image is stored
    - `gps` GPS data from pixhawk
    - `imu` IMU data from pixhawk
    - `att` attitude data from pixhawk
  
  - Only the `image` field will be used for the purposes of target detection in this function. This iterates through all the preloaded reference target images and then tries to find them in the just captured frame. It then composites the results and returns a list of objects containing `name` of the target, `corners` the list of corners where the match was detected, and `found` indicating whether the target was found in the image.

`localization.py`

- `localize(metadata: PixhawkMetadataObject, detectedObjects: List[DetectedObject])`

  - Uses the camera metadata to perform 3D view reconstruction to get real coordinates of the found targets. Adds a field `real_world_pos` to the `detectedObjects` parameter and then returns it.

`aggregator.py`

- `aggregate_results(detected_objects: List[DetectedObject])`

  - Collects all the captured data and performs **RANSAC** analysis to eliminate the outliers. Returns the list of inlier data points.