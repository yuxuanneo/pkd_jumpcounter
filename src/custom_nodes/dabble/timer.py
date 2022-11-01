"""
Node template for creating custom nodes.
"""

from typing import Any, Dict

from peekingduck.pipeline.nodes.abstract_node import AbstractNode
from datetime import datetime

class Node(AbstractNode):
    """
    Uses the tracking id given by dabble.tracking to track the time object has remained
    in the video. 

    Args:
        config (:obj:`Dict[str, Any]` | :obj:`None`): Node configuration.
    """

    def __init__(self, config: Dict[str, Any] = None, **kwargs: Any) -> None:
        super().__init__(config, node_path=__name__, **kwargs)
        
        # key=tracking_id and value=time started tracking
        self.tracked_ids = {}

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
        
        # holds the time for each id that is seen in current frame
        times_list = []
        ids = inputs["obj_attrs"]["ids"]
        new_ids = [current_id for current_id in ids if current_id not in self.tracked_ids]
        
        now = datetime.now()
        if new_ids:
            for new_id in new_ids:
                self.tracked_ids[new_id] = now
        
        
        # TO IMPLEMENT: config to adjust between s mins and hrs
        # calculate time taken for all nodes 
        for current_id in ids:
            times_list.append(int((now - self.tracked_ids[current_id]).total_seconds()))
            
        inputs["obj_attrs"]["times"] = times_list
        
        return inputs["obj_attrs"]
                


        # result = do_something(inputs["in1"], inputs["in2"])
        # outputs = {"out1": result}
        # return outputs
