from pydantic import BaseModel


class llmFormat(BaseModel):
    code: str


def llm_prompt() -> str:
    """
    The prompt for LLM to generate C code.
    """
    user_message = (
        "You are an assistant that helps in generating C code for fuzz testing on the processor.\n"
        "The goal is to generate diverse C code snippets that can be used as test inputs for hardware testing.\n"
        "Each generated code should be syntactically correct and should cover a variety of C constructs and operations.\n"
        "The C code should vary in complexity and should contain both simple and advanced constructs to ensure diversity.\n"
        "Please generate a piece of C code."
    )
    return user_message