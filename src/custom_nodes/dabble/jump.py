"""
Node template for creating custom nodes.
"""

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
        
        ids = inputs["obj_attrs"]["ids"]
        times = inputs["obj_attrs"]["times"]
        btm_midpoints = inputs["btm_midpoint"]
        
        # for new object, record the initial btm midpoint as reference
        for i, time in enumerate(times):
            if time == 0:
                 self.tracked_ids[ids[i]] = {"stand_height": btm_midpoints[i], 
                                             "jump_count": 0} 
            else:
                stand_height = self.tracked_ids[ids[i]]["stand_height"]
                curr_height = btm_midpoints[i]
                if (curr_height[1] - stand_height[1])/stand_height[1] >= 0.05:
                    self.tracked_ids[ids[i]]["jump_count"] += 1
            
        jumps_list = []        
        for current_id in ids:
            jumps_list.append(self.tracked_ids[current_id]["jump_count"])
        
        inputs["obj_attrs"]["jumps"] = jumps_list
        
        return inputs["obj_attrs"]
