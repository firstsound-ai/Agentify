from .answer.tool import create_answer_node
from .code.tool import create_code_node
from .document_extractor.tool import create_document_extractor_node
from .end.tool import create_end_node
from .http_request.tool import create_http_request_node
from .if_else.tool import create_if_else_node
from .llm.tool import create_llm_node
from .loop.tool import create_loop_node
from .question_classifier.tool import create_question_classifier_node
from .start.tool import create_start_node
from .template_transform.tool import create_template_transform_node
from .tools.arxiv.tool import create_arxiv_search_tool
from .tools.spider.tool import create_spider_tool
from .tools.tavily.tool import create_tavily_search_tool
from .variable_aggregator.tool import create_variable_aggregator_node

tools_list = [
    create_llm_node,
    create_start_node,
    create_answer_node,
    create_end_node,
    create_code_node,
    create_template_transform_node,
    create_question_classifier_node,
    create_if_else_node,
    create_http_request_node,
    create_variable_aggregator_node,
    create_document_extractor_node,
    create_arxiv_search_tool,
    create_spider_tool,
    create_tavily_search_tool,
    # create_loop_node,
    # BUG: 循环节点暂时有问题
]
tool_map = {tool.name: tool for tool in tools_list}
