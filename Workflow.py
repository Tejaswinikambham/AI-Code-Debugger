"""Small LangGraph pipeline: inspect source, execute in Docker, give a hint."""
import ast
from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class TutorState(TypedDict, total=False):
    code: str
    code_summary: str
    execution: dict
    hint: str


def parse_code(state: TutorState) -> dict:
    """Parse syntax and summarize top-level definitions without executing code."""
    try:
        tree = ast.parse(state["code"])
    except SyntaxError as error:
        return {
            "code_summary": "Python syntax check failed.",
            "execution": {"ok": False, "error": f"SyntaxError at line {error.lineno}: {error.msg}"},
        }
    definitions = [node.name for node in tree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef))]
    summary = "Top-level definitions: " + (", ".join(definitions) if definitions else "none")
    return {"code_summary": summary}


def socratic_tutor(state: TutorState) -> dict:
    result = state["execution"]
    if result.get("ok"):
        hint = "Your code ran successfully. What input would you test next, including an edge case?"
    elif "SyntaxError" in result.get("error", ""):
        hint = "Look near the reported line. Which punctuation or indentation rule might Python be expecting?"
    else:
        hint = "Read the final error line and locate the first line in your code mentioned in the traceback. What value or assumption might be causing it?"
    return {"hint": hint}


graph = StateGraph(TutorState)
graph.add_node("code_parser", parse_code)
graph.add_node("socratic_tutor", socratic_tutor)
graph.add_edge(START, "code_parser")
graph.add_edge("code_parser", "test_runner")
graph.add_edge("test_runner", "socratic_tutor")
graph.add_edge("socratic_tutor", END)
tutor_app = graph.compile()


def run_tutor_workflow(code: str) -> dict:
    result = tutor_app.invoke({"code": code})
    return {"summary": result["code_summary"], "execution": result["execution"], "hint": result["hint"]}
