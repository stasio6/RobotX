CXX = g++
CXXFLAGS = -std=c++11 -Wall -Wextra
LDFLAGS = -L/opt/homebrew/Cellar/opencv/4.9.0_8/lib -lopencv_core -lopencv_imgcodecs -lopencv_imgproc -lopencv_highgui -lopencv_ml -lopencv_video -lopencv_features2d -lopencv_calib3d -lopencv_objdetect -lopencv_stitching -lopencv_xfeatures2d
INCLUDES = -I/opt/homebrew/Cellar/opencv/4.9.0_8/include/opencv4

TARGET = image_matching

all: $(TARGET)

$(TARGET): main.cpp
	$(CXX) $(CXXFLAGS) $(INCLUDES) $< -o $@ $(LDFLAGS)

clean:
	rm -f $(TARGET)