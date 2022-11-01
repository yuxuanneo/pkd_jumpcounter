"""
Custom node to filter bboxes outside a zone
"""

from typing import Any, Dict
import numpy as np
from peekingduck.pipeline.nodes.abstract_node import AbstractNode


class Node(AbstractNode):
   """Custom node to filter bboxes outside a zone

   Args:
      config (:obj:`Dict[str, Any]` | :obj:`None`): Node configuration.
   """

   def __init__(self, config: Dict[str, Any] = None, **kwargs: Any) -> None:
      super().__init__(config, node_path=__name__, **kwargs)

   def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:  # type: ignore
      """Checks bounding box x-coordinates against the zone left and right borders.
      Retain bounding box if within, otherwise discard it.

      Args:
            inputs (dict): Dictionary with keys "bboxes"

      Returns:
            outputs (dict): Dictionary with keys "bboxes".
      """
      bboxes = inputs["bboxes"]
      zones = self.config["zones"]
      zone = zones[0]         # only work with one zone currently
      # convert zone with 4 points to a zone bbox with (x1, y1), (x2, y2)
      x1, y1 = zone[0]
      x2, y2 = zone[2]
      zone_bbox = np.asarray([x1, y1, x2, y2])

      retained_bboxes = []
      for bbox in bboxes:
         # filter by left and right borders (ignore top and bottom)
         if bbox[0] > zone_bbox[0] and bbox[2] < zone_bbox[2]:
            retained_bboxes.append(bbox)

      return {"bboxes": np.asarray(retained_bboxes)}