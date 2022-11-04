"""Counts the total number of jumps made by objects within a zone"""

from typing import Any, Dict

from peekingduck.pipeline.nodes.abstract_node import AbstractNode

class Node(AbstractNode):
    """Uses the bottom midpoints of all detected bounding boxes and outputs the
    number of jumps recorded by all objects in each specified zone.
    
    Object is considered in a particular zone if the bottom midpoint of its bbox
    falls within that zone. 
    
    Inputs:
        |zones|
        |obj_attrs|
        |btm_midpoint|

    Outputs:
        |obj_attrs|
        |zone_count_people|
        |zone_count_jump|

    """
    
    def __init__(self, config: Dict[str, Any] = None, **kwargs: Any) -> None:
        super().__init__(config, node_path=__name__, **kwargs)
        self.tracked_ids = {} # k=bbox id, v=zone id

    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:  # type: ignore
        """This node does the allocation of detected object into each zone from 
        the zones defined earlier in the dabble.zone_count node. Then, sum up the 
        number of jumps recorded for each zone.

        Args:
            inputs (dict): Dictionary with keys "zones", "obj_attrs", 
            "btm_midpoint".

        Returns:
            outputs (dict): Dictionary with keys "obj_attrs", "zone_count_people", 
            "zone_count_jump".
        """
        
        zones = inputs["zones"]
        ids = inputs["obj_attrs"]["ids"]
        jumps = inputs["obj_attrs"]["jumps"]
        btm_midpoints = inputs["btm_midpoint"]
        
        for i, id in enumerate(ids):
            # only allocate object to zone if it hasnt already been done
            if id not in self.tracked_ids:
                # btm midpt of the bbox associated with id
                btm_midpoint = btm_midpoints[i] 
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
        
        # iterate through detected ids in this frame and sum the number of jumps
        # in each zone. Also get the total no. of objects in each zone.
        # if object not found in zone, allocate it to 'not in zone'
        for i, id in enumerate(ids):
            zone_id = self.tracked_ids.get(id, "not in zone")
            zones_list.append(f"zone:{zone_id}")
            zone_counts_people[zone_id] = zone_counts_people.get(zone_id, 0) + 1
            zone_counts_jump[zone_id] = zone_counts_jump.get(zone_id, 0) + jumps[i]
        
        inputs["obj_attrs"]["zones"] = zones_list
        
        # sorts order of zone_counts so that its always in alphabetical order
        zone_counts_people = dict(sorted(zone_counts_people.items(), key=lambda x: str(x)))
        zone_counts_jump = dict(sorted(zone_counts_jump.items(), key=lambda x: str(x)))
        inputs["obj_attrs"]["jumps"] = [f"count:{count}" for count in jumps]


        return {"obj_attrs": inputs["obj_attrs"], 
                "zone_count_people": str(zone_counts_people), 
                "zone_count_jump": str(zone_counts_jump)}
            