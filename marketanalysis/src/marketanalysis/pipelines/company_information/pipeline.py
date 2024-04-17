"""
This is a boilerplate pipeline 'company_information'
generated using Kedro 0.19.3
"""

from kedro.pipeline import Pipeline, pipeline, node
from .nodes import  assemble

def create_pipeline(**kwargs) -> Pipeline:
    return pipeline([
        node(
            func=assemble,
            inputs="scraping_result",
            outputs="company_information",
            name="company_information_node"
        )
    ])
