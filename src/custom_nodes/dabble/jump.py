"""
Node template for creating custom nodes.
"""
import numpy as np
from typing import Any, Dict

from peekingduck.pipeline.nodes.abstract_node import AbstractNode


class Node(AbstractNode):
    """This is a template class of how to write a node for PeekingDuck.

    Args:
        config (:obj:`Dict[str, Any]` | :obj:`None`): Node configuration.
    """

    def __init__(self, config: Dict[str, Any] = None, **kwargs: Any) -> None:
        super().__init__(config, node_path=__name__, **kwargs)
        self.tracked_ids = {}
        self.direction_reverse = {"up": "down",
                                  "down": "up"}
        
        # initialize/load any configs and models here
        # configs can be called by self.<config_name> e.g. self.filepath
        # self.logger.info(f"model loaded with configs: config")

    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:  # type: ignore
        """This node does ___.

        Args:
            inputs (dict): Dictionary with keys "__", "__".

        Returns:
            outputs (dict): Dictionary with keys "__".
        """
        threshold = self.config["threshold"]
        ids = inputs["obj_attrs"]["ids"]
        times = inputs["obj_attrs"]["times"]
        btm_midpoints = inputs["btm_midpoint"]
        
        # for new object, record the initial btm midpoint as reference
        for i in range(len(btm_midpoints)):
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
                    
                if self.change_direction(threshold, previous_heights, direction):
                    self.tracked_ids[ids[i]]["direction"] = self.direction_reverse[direction]
                    if direction == "up":
                        self.tracked_ids[ids[i]]["jump_count"] += 1
                
        heights_list = [midpt[1] for midpt in btm_midpoints]
        directions_list = []
        jumps_list = []        
        for current_id in ids:
            jumps_list.append(self.tracked_ids[current_id]["jump_count"])
            directions_list.append(self.tracked_ids[current_id]["direction"])
            
            # keep only the most recent previous heights, otherwise list will become infinitely long over time
            if len(self.tracked_ids[current_id]["previous_heights"]) > 3:
                self.tracked_ids[current_id]["previous_heights"] = self.tracked_ids[current_id]["previous_heights"][-threshold:]
        
        inputs["obj_attrs"]["jumps"] = jumps_list
        inputs["obj_attrs"]["directions"] = directions_list
        inputs["obj_attrs"]["heights"] = heights_list
        
        return inputs["obj_attrs"]
    
    
    def change_direction(self, threshold, previous_heights, direction):
        
        if len(previous_heights) < threshold:
            return False
        
        heights_to_consider = previous_heights[-threshold:]
        differences = np.diff(heights_to_consider)
        signs = [np.sign(difference) for difference in differences]
        
        if len(set(signs)) == 1: # if all same sign, 
            if (((signs[0]  == 1) and (direction == "up")) or  # recall that top left coord is (0,0), so a positive change is actually falling down
                ((signs[0] == -1) and (direction == "down"))):
                return True
        return False
            

