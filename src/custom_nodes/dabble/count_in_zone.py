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
        btm_midpoints = inputs["btm_midpoint"]
        
        bboxes_in_zone = {} # k=bbox id, v=zone id

        
        for zone_i, zone in enumerate(zones):
            # convert zone with 4 points to a zone bbox with (x1, y1), (x2, y2)
            x1, y1 = zone[0]
            x2, y2 = zone[2]
            zone_bbox = np.asarray([x1, y1, x2, y2])

            # this follows the method of dabble.zone_count, where we only consider the btm midpt of bboxes
            for btm_midpoint_i, btm_midpoint in enumerate(btm_midpoints):
                x, y = btm_midpoint
                
                if (x1 < x) and (x < x2) and (y1 < y) and(y < y2): 
                    obj_id = ids[bbox_i]
                    bboxes_in_zone[obj_id] = zone_i
        
        zones_list = []
        for id in ids:
            zones_list.append(bboxes_in_zone.get(id, "not in zone"))
            
        inputs["obj_attrs"]["zones"] = zones_list
        
        return inputs["obj_attrs"]
            