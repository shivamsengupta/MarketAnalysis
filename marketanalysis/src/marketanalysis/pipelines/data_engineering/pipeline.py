"""
This is a boilerplate pipeline 'data_input'
generated using Kedro 0.19.3
"""

from kedro.pipeline import Pipeline, pipeline, node
from .nodes import get_input, scraping


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline([
        node(
            func= scraping,
            inputs= None,
            outputs="scraping_result",
            name="scraping_node"
        )
        
    ])
