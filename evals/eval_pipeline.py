from uuid import uuid4
from dataclasses import dataclass

from dotenv import load_dotenv

from deepeval import evaluate
from deepeval.evaluate import CacheConfig, DisplayConfig
from deepeval.integrations.langchain import CallbackHandler
from deepeval.metrics import ArgumentCorrectnessMetric, GEval,PlanAdherenceMetric, PlanQualityMetric, StepEfficiencyMetric, TaskCompletionMetric, ToolCorrectnessMetric
from deepeval.test_case import LLMTestCase, SingleTurnParams, ToolCall, ToolCallParams

from evals.tests import cases, dataset
from evals.model import eval_model
from agent.agent import agent


SUCCESSFUL_TASK_DESCRIPTION = """
If the username is missing, ask the user to provide it.
For a refund request, identify the customer and the requested purchases, and
check that each purchase is no more than 30 days old and is not in the future.
Refund only the items requested by the user. If the customer or requested item
cannot be found, do not issue a refund ticket and explain why.
Once the necessary information is available, tell the user whether a refund
ticket was issued and its amount, or explain why no refund was issued.
For an information-only request, answer the question without issuing a ticket.
"""

@dataclass(frozen=True)
class CaseResult:
    case_id: str
    tags: tuple[str, ...]
    expected_ticket_issued: bool
    expected_refund_amount: float | None
    expected_refunded_items: tuple[str, ...]
    test_case: LLMTestCase


def build_metrics():
    """Keep the thresholds and evaluator model used by the individual scripts."""
    trace_metrics = [
        TaskCompletionMetric(threshold=0.8,model=eval_model,task=SUCCESSFUL_TASK_DESCRIPTION,include_reason=True,),
        StepEfficiencyMetric(threshold=0.8, model=eval_model, include_reason=True,),
        PlanQualityMetric(threshold=0.8, model=eval_model, include_reason=True,),
        PlanAdherenceMetric(threshold=0.8, model=eval_model, include_reason=True,),
    ]
    single_turn_metrics = [
        ArgumentCorrectnessMetric( threshold=0.9, model=eval_model, include_reason=True,),
        ToolCorrectnessMetric(
            threshold=0.9, model=eval_model, include_reason=True, evaluation_params=[ToolCallParams.INPUT_PARAMETERS]),
        GEval(
            name="Answer Correctness",
            evaluation_params=[
                SingleTurnParams.INPUT,
                SingleTurnParams.ACTUAL_OUTPUT,
                SingleTurnParams.EXPECTED_OUTPUT,
            ],
            evaluation_steps=[
                "Check that the actual output and expected output have the same "
                "logical conclusion about the user's request.",
            ],
            threshold=0.8,
            model=eval_model,
            verbose_mode=True,
        ),
    ]
    return trace_metrics, single_turn_metrics


def main():
    load_dotenv()

    trace_metrics, single_turn_metrics = build_metrics()
    cache_config = CacheConfig(use_cache=False, write_cache=False)
    display_config = DisplayConfig(inspect_after_run=False)
    results: list[CaseResult] = []

    # The callback captures the trace required by the four agentic metrics.
    goldens = dataset.evals_iterator(
        metrics=trace_metrics,
        cache_config=cache_config,
        display_config=display_config,
    )
    for case, golden in zip(cases, goldens, strict=True):
        response = agent.invoke(
            {"messages": [{"role": "user", "content": golden.input}]},
            config=
            {
                "configurable": {"thread_id": str(uuid4())},
                "callbacks": [CallbackHandler()],
            },
        )

        tools_called = []
        for message in response["messages"]:
            for tool_call in getattr(message, "tool_calls", []) or []:
                tools_called.append(
                    ToolCall(
                        name=tool_call["name"],
                        input_parameters=tool_call["args"],
                    )
                )

        test_case = LLMTestCase(
                input=golden.input,
                actual_output=response["structured_response"].answer,
                expected_output=golden.expected_output,
                tools_called=tools_called,
                expected_tools=golden.expected_tools,
            )
        results.append(
            CaseResult(
                case_id=case.id,
                tags=case.tags,
                expected_ticket_issued=case.expected_ticket_issued,
                expected_refund_amount=case.expected_refund_amount,
                expected_refunded_items=case.expected_refunded_items,
                test_case=test_case,
            )
        )

    evaluate(
        test_cases=[result.test_case for result in results],
        metrics=single_turn_metrics,
        cache_config=cache_config,
        display_config=display_config,
    )
    print(f"\nCompleted all 7 metrics for {len(results)} test cases.")


if __name__ == "__main__":
    main()