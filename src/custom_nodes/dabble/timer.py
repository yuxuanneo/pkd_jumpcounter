"""Measure time taken object has been in frame"""

from typing import Any, Dict

from peekingduck.pipeline.nodes.abstract_node import AbstractNode
from datetime import datetime

class Node(AbstractNode):
    """Uses the tracking id given by dabble.tracking node to track the duration 
    object has remained in the video. Time taken is measured in seconds.

    Inputs:
        |obj_attrs|
    Outputs:
        |obj_attrs|
 
    """

    def __init__(self, config: Dict[str, Any] = None, **kwargs: Any) -> None:
        super().__init__(config, node_path=__name__, **kwargs)
        
        self.tracked_ids = {}

    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """This node counts the duration each object has remained in the video. 
        This is done by taking the current time, then subtracting the time the 
        object was first detected. Returns a time (in seconds) for each object.

        Args:
            inputs (dict): Dictionary with keys "ids". 

        Returns:
            outputs (dict): Dictionary with additional key "times". 
        """
        
        ids = inputs["obj_attrs"]["ids"]
        new_ids = [current_id for current_id in ids if current_id not in self.tracked_ids]
        
        now = datetime.now()
        if new_ids:
            for new_id in new_ids:
                self.tracked_ids[new_id] = now
                
        # holds the time for each id that is seen in current frame
        times_list = []
        # calculate time taken for all nodes 
        for current_id in ids:
            times_list.append(f"timer:{int((now - self.tracked_ids[current_id]).total_seconds())}s")
            
        inputs["obj_attrs"]["times"] = times_list
        
        return inputs["obj_attrs"]
                
