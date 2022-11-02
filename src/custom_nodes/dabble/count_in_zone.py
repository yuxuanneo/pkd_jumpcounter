"""
Node template for creating custom nodes.
"""

from typing import Any, Dict
from collections import OrderedDict
import re

from peekingduck.pipeline.nodes.abstract_node import AbstractNode


class Node(AbstractNode):
    """This is a template class of how to write a node for PeekingDuck.

    Args:
        config (:obj:`Dict[str, Any]` | :obj:`None`): Node configuration.
    """

    def __init__(self, config: Dict[str, Any] = None, **kwargs: Any) -> None:
        super().__init__(config, node_path=__name__, **kwargs)
        self.tracked_ids = {} # k=bbox id, v=zone id

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

        # result = do_something(inputs["in1"], inputs["in2"])
        # outputs = {"out1": result}
        # return outputs
        zones = inputs["zones"]
        bboxes = inputs["bboxes"]
        ids = inputs["obj_attrs"]["ids"]
        jumps = inputs["obj_attrs"]["jumps"]
        btm_midpoints = inputs["btm_midpoint"]
        
        for i, id in enumerate(ids):
            if id not in self.tracked_ids:
                btm_midpoint = btm_midpoints[i] # midpt of the bbox associated with id
                x, y = btm_midpoint
                
                for zone_i, zone in enumerate(zones):
                    # convert zone with 4 points to a zone bbox with (x1, y1), (x2, y2)
                    x1, y1 = zone[0]
                    x2, y2 = zone[2]
                    if (x1 < x) and (x < x2) and (y1 < y) and(y < y2):
                        self.tracked_ids[id] = zone_i
                    
        zones_list = []
        
        zone_counts_people = {} # k = zone id, v = people count in zone
        zone_counts_jump = {} # k = zone id, v = jump count in zone
        for i, id in enumerate(ids):
            zone_id = self.tracked_ids.get(id, "not in zone")
            zones_list.append(f"zone:{zone_id}")
            zone_counts_people[zone_id] = zone_counts_people.get(zone_id, 0) + 1
            zone_counts_jump[zone_id] = zone_counts_jump.get(zone_id, 0) + jumps[i]
        
        inputs["obj_attrs"]["zones"] = zones_list
        
        zone_counts_people = dict(sorted(zone_counts_people.items(), key=lambda x: str(x)))
        zone_counts_jump = dict(sorted(zone_counts_jump.items(), key=lambda x: str(x)))
        inputs["obj_attrs"]["jumps"] = [f"count:{count}" for count in jumps]


        return {"obj_attrs": inputs["obj_attrs"], 
                "zone_count_people": str(zone_counts_people), 
                "zone_count_jump": str(zone_counts_jump)}
            