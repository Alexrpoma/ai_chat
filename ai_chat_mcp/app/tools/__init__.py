from .business_tools import register_business_tools
from .math_tools import register_math_tools
from .text_tools import register_text_tools
from .utility_tools import register_utility_tools

ALL_TOOLS = (
    register_business_tools,
    register_math_tools,
    register_text_tools,
    register_utility_tools,
)