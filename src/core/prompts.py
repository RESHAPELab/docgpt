from langchain.prompts.prompt import PromptTemplate

_template = """
Given the following conversation and a follow up question, 
rephrase the follow up question to be a standalone question, 
in its original language.

When you mention something about source code, 
consider that you have access to every class, method, 
variable and any other element of the project's code. 
Search tirelessly for it until it proves not to exist!

Chat History:
{chat_history}
Follow Up Input: {question}
Standalone question:"""
DEFAULT_PROMPT = PromptTemplate.from_template(_template)
