"""Counts the number of jumps made by detected objects"""

import numpy as np
from typing import Any, Dict

from peekingduck.pipeline.nodes.abstract_node import AbstractNode


class Node(AbstractNode):
    """Uses the tracking id given by dabble.tracking node to track the number 
    of jumps made by each object, starting from when it was first detected.
    
    Inputs:
        |btm_midpoint|
        |obj_attrs|
    Outputs:
        |obj_attrs|

    Configs:
        threshold (:obj:`int`): **default = 5**.
            This will be used when determining if the object is traveling 
            upwards or downwards. The number of frames object has to move in 
            the same direction before it is detected to be travelling 
            upwards/ downwards is given by threshold. Setting a lower threshold 
            would make the node more sensitive to detecting jumps, and vice 
            versa.
            
            To record smaller jumps, user should reduce the magnitude of 
            threshold. To only record higher jumps, user should increase the 
            magnitude of threshold.  

    """

    def __init__(self, config: Dict[str, Any] = None, **kwargs: Any) -> None:
        super().__init__(config, node_path=__name__, **kwargs)
        self.tracked_ids = {}
        # helper dict to flip the directions when needed
        self.direction_reverse = {"up": "down",
                                  "down": "up"}

    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]: 
        """This node traacks the number of jumps made by each object and return 
        this number. 

        Args:
            inputs (dict): Dictionary with keys "btm_midpoint", "obj_attrs".

        Returns:
            outputs (dict): Dictionary with additional key "jumps", "directions"
            and "heights". 
        """
        threshold = self.config["threshold"]
        ids = inputs["obj_attrs"]["ids"]
        btm_midpoints = inputs["btm_midpoint"]
        
        for i in range(len(btm_midpoints)):
            # for new object, instntiate a dict to hold their details
            if ids[i] not in self.tracked_ids:
                 self.tracked_ids[ids[i]] = {"jump_count": 0, 
                                             "direction": "down", 
                                             "threshold": 0, 
                                             "previous_heights": [btm_midpoints[i][1]]}
            else:
                curr_height = btm_midpoints[i][1]
                direction = self.tracked_ids[ids[i]]["direction"]
                previous_heights = self.tracked_ids[ids[i]]["previous_heights"]
                
                previous_heights.append(curr_height)
                
                # if object has changed direction:
                if self.change_direction(threshold, previous_heights, direction):
                    self.tracked_ids[ids[i]]["direction"] = self.direction_reverse[direction]
                    # increment jump counter by 1 only when direction changes from
                    # down to up
                    if direction == "up":
                        self.tracked_ids[ids[i]]["jump_count"] += 1
                
        heights_list = [midpt[1] for midpt in btm_midpoints]
        directions_list = []
        jumps_list = []        
        for current_id in ids:
            jumps_list.append(self.tracked_ids[current_id]["jump_count"])
            directions_list.append(self.tracked_ids[current_id]["direction"])
            
            # keep only the most recent previous heights, otherwise list will 
            # become infinitely long over time
            if len(self.tracked_ids[current_id]["previous_heights"]) > threshold:
                self.tracked_ids[current_id]["previous_heights"] = self.tracked_ids[current_id]["previous_heights"][-threshold:]
        
        inputs["obj_attrs"]["jumps"] = jumps_list
        inputs["obj_attrs"]["directions"] = directions_list
        inputs["obj_attrs"]["heights"] = heights_list
        
        return inputs["obj_attrs"]
    
    
    def change_direction(self, threshold: int, previous_heights: 'list[float]', direction: str) -> bool:
        """This helper function checks if a particular object has changed its 
        flight direction (upwards or downwards). If object's previous direction 
        was "up" but height has been decreasing, the direction will be reversed 
        to "down", and vice versa.

        Args:
            threshold (int): The number of frames object has to move in the same
            direction before it is detected to be travelling upwards/ downwards.
            
            previous_heights (list): Previous heights recorded for the object. 
            This is stored in chronological order, with the first element being 
            the least recent and the last element being the most recent. Height 
            of the object is determined from the btm_midpoint, given by the 
            dabble node "bbox_to_btm_midpoint".
            
            direction (str): Most recent direction of the object. 

        Returns:
            Boolean: True if object has changed direction, False otherwise.
        """
        if len(previous_heights) < threshold:
            return False
        
        heights_to_consider = previous_heights[-threshold:]
        differences = np.diff(heights_to_consider)
        signs = [np.sign(difference) for difference in differences]
        
        # if all heights were moving in same direction, 
        if len(set(signs)) == 1: 
            if (((signs[0]  == 1) and (direction == "up")) or  
                ((signs[0] == -1) and (direction == "down"))):
                return True
        return False
            

