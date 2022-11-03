# pkd demo

# Introduction
To implement a gamified exercise inference pipeline, which counts the number of tuck jumps completed by individuals within the video feed. Scores can also be aggregated into "zones" that are pre-determined by users, which could introduce some level of team competitiveness into the game. At the very least, the pipeline should still serve as a regular counter for a fitness enthusiast, to track their fitness journey from an easy to set up script. 

The inference pipeline has been implemented on PeekingDuck, an open-source, modular framework in Python, built for Computer Vision (CV) inference. The repository is built and managed by the CV Hub team in AI Singapore. 

<img src="viewer/tuck_jump.gif" alt="drawing" width="300"/>

# Installation
```
> pip install peekingduck
```
For more detailed installation instructions, please refer to the official PeekingDuck [documentations](https://peekingduck.readthedocs.io/en/stable/getting_started/02_standard_install.html#install-peekingduck).

# Usage
## Model
- [YOLOV4-tiny](https://arxiv.org/abs/2004.10934) to first detect the human objects in the video feed. Then, the dabble.tracking node tracks bounding boxes detected by the YOLOV4 model, using the [IoU tracking algorithm](http://elvera.nue.tu-berlin.de/files/1517Bochinski2017.pdf). 

Essentially, the IOU checker associates the current detection with the highest IoU to the last detection in the previous frame. In other words, detections with close proximity to each other in between frames are assumed to be of the same object, and the particular object will be tracked this way. 

## Custom Nodes
1. ### dabble.timer
    Description: Measure time taken object has been in frame
2. ### dabble.jump
    Description: Counts the number of jumps made by detected objects
3. ### dabble.count_in_zone
    Description: Counts the total number of jumps made by objects within a zone

Then, the custom dabble.timer node would track how long (in seconds) since the object was first detected. This is measured by using the time at the current frame, subtracted by the time the object was first detected. 

Next, the custom dabble.jump node would track the number of tuck jumps made by the object, which is a cumulative count since the object was first tracked. A jump is deteced through a helper function which checks if the object has changed directions (upwards or downwards). 

More specifically, the jump node would store information of the heights of the bounding box of each object for each frame. Then, the helper function looks through the past heights to infer if the object is currently moving upwards or downwards. Height is recorded at the height of the bottom mid point of the bounding box predicted. 

If object's previous direction was "up" but height has been decreasing, the direction will be reversed to "down", and vice versa. For every "up" and "down" movement made by the object, the jump counter increases by one. 

For added versatility, the dabble.jump node also has a optional threshold config which represents the the number of frames object has to move in the same direction before it is detected to be travelling upwards/ downwards. Setting a lower threshold would make the node more sensitive to detecting jumps, and vice versa. To record smaller jumps, user should reduce the magnitude of threshold. To only record higher jumps, user should increase the magnitude of threshold instead.  

Finally, the custom dabble.count_in_zone node would classify each detected object into the zones specified in dabble.zone_count. Then, group the jump counts by the zone and sum up to get the total jump count for each zone. 

<img src="viewer/demo_image.png" alt="drawing" width="300"/>

## Demo
<img src="viewer/output_demo.gif" alt="drawing" width="300"/>

[full output](output/jumping_jacks_221103_152704.mp4)

## Possible use cases:
- Army training, where there are many soldiers and limited supervisors. This inference pipeline would make it easy to count if all soldiers have finished the required set of exercises.
- School camp games, where participants are split into groups to compete with one another. 

