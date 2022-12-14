"""
A custom node for debugging
"""

from typing import Any, Dict

from peekingduck.pipeline.nodes.abstract_node import AbstractNode


class Node(AbstractNode):
   """This is a simple example of creating a custom node to help with debugging.

   Args:
      config (:obj:`Dict[str, Any]` | :obj:`None`): Node configuration.
   """

   def __init__(self, config: Dict[str, Any] = None, **kwargs: Any) -> None:
      super().__init__(config, node_path=__name__, **kwargs)

   def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:  # type: ignore
      """A simple debugging custom node

      Args:
            inputs (dict): "all", to view everything in data pool

      Returns:
            outputs (dict): "none"
      """

      self.logger.info("-- debug --")
      # show what is available in PeekingDuck's data pool
      self.logger.info(f"input.keys={list(inputs.keys())}")
      # debug specific data: bboxes
      bboxes = inputs["bboxes"]
      bbox_labels = inputs["bbox_labels"]
      bbox_scores = inputs["bbox_scores"]
      ids = inputs["obj_attrs"]['ids']
      heights = inputs["obj_attrs"]['heights']
      
      self.logger.info(ids)
      
      self.logger.info(f"num bboxes={len(bboxes)}")
      for i, bbox in enumerate(bboxes):
            id, label, score, height = ids[i], bbox_labels[i], bbox_scores[i], heights[i]
            self.logger.info(f"bbox {i}:")
            self.logger.info(f"  id={id}, label={label}, score={score:0.2f}")
            self.logger.info(f"  coords={bbox}")
            self.logger.info(f"  height={height}")

      return {}  # no outputs