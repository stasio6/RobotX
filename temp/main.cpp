#include <opencv2/opencv.hpp>
#include <opencv2/xfeatures2d.hpp>
#include <iostream>

int main(int argc, char** argv) {
    
    if(argc != 3)
    {
        std::cout << "Usage: " << argv[0] << " <small image> <target image>" << std::endl;
        return -1;
    }

    // Read the smaller image and the larger target image
    cv::Mat originalSmall = cv::imread(argv[1], cv::IMREAD_GRAYSCALE);
    cv::Mat targetImage = cv::imread(argv[2], cv::IMREAD_GRAYSCALE);

		cv::Mat smallImage;

		cv::Size newSize(800, 800);
    cv::resize(originalSmall, smallImage, newSize);

    if (smallImage.empty() || targetImage.empty()) {
        std::cout << "Failed to load images!" << std::endl;
        return -1;
    }

    // Create SURF detector
    cv::Ptr<cv::xfeatures2d::SURF> surf = cv::xfeatures2d::SURF::create(400);

    // Detect keypoints and compute descriptors for both images
    std::vector<cv::KeyPoint> smallKeypoints, targetKeypoints;
    cv::Mat smallDescriptors, targetDescriptors;
    surf->detectAndCompute(smallImage, cv::noArray(), smallKeypoints, smallDescriptors);
    surf->detectAndCompute(targetImage, cv::noArray(), targetKeypoints, targetDescriptors);

    // Create FLANN-based matcher
    cv::Ptr<cv::DescriptorMatcher> matcher = cv::DescriptorMatcher::create(cv::DescriptorMatcher::FLANNBASED);
    std::vector<std::vector<cv::DMatch>> matches;
    matcher->knnMatch(smallDescriptors, targetDescriptors, matches, 2);

    // Apply ratio test to filter good matches
    std::vector<cv::DMatch> goodMatches;
    for (size_t i = 0; i < matches.size(); i++) {
        if (matches[i][0].distance < 0.7 * matches[i][1].distance) {
            goodMatches.push_back(matches[i][0]);
        }
    }

    // Estimate homography using RANSAC
    std::vector<cv::Point2f> smallPoints, targetPoints;
    for (size_t i = 0; i < goodMatches.size(); i++) {
        smallPoints.push_back(smallKeypoints[goodMatches[i].queryIdx].pt);
        targetPoints.push_back(targetKeypoints[goodMatches[i].trainIdx].pt);
    }

    if (smallPoints.size() < 4 || targetPoints.size() < 4) {
        std::cout << "Not enough matches to run RANSAC" << std::endl;
        return -1;
    }

    cv::Mat homography = cv::findHomography(smallPoints, targetPoints, cv::RANSAC);

    // Get the corners of the small image
    std::vector<cv::Point2f> smallCorners(4);
    smallCorners[0] = cv::Point2f(0, 0);
    smallCorners[1] = cv::Point2f(smallImage.cols, 0);
    smallCorners[2] = cv::Point2f(smallImage.cols, smallImage.rows);
    smallCorners[3] = cv::Point2f(0, smallImage.rows);

    // Transform the corners using the homography
    std::vector<cv::Point2f> targetCorners(4);
    cv::perspectiveTransform(smallCorners, targetCorners, homography);

    // Draw the matched region on the target image
    cv::Mat resultImage;
    cv::cvtColor(targetImage, resultImage, cv::COLOR_GRAY2BGR);
    cv::line(resultImage, targetCorners[0], targetCorners[1], cv::Scalar(0, 255, 0), 2);
    cv::line(resultImage, targetCorners[1], targetCorners[2], cv::Scalar(0, 255, 0), 2);
    cv::line(resultImage, targetCorners[2], targetCorners[3], cv::Scalar(0, 255, 0), 2);
    cv::line(resultImage, targetCorners[3], targetCorners[0], cv::Scalar(0, 255, 0), 2);
    return 0;
}
