import os
import re
from typing import List, Dict, Any
from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger
from pathlib import Path


class ReActAgent:
    """
    SKELETON: A ReAct-style Agent that follows the Thought-Action-Observation loop.
    Students should implement the core loop logic and tool execution.
    """

    def __init__(
        self,
        llm: LLMProvider,
        tools: List[Dict[str, Any]],
        max_steps: int = 5,
    ):
        self.llm = llm
        self.tools = tools
        self.max_steps = max_steps
        self.history = []

    def get_system_prompt(self, user_input: str) -> str:
        """
        TODO: Implement the system prompt that instructs the agent to follow ReAct.
        Should include:
        1.  Available tools and their descriptions.
        2.  Format instructions: Thought, Action, Observation.
        """
        tool_descriptions = "\n".join(
            [f"- {t['name']}: {t['description']}" for t in self.tools]
        )
        tools_list = [t["name"] for t in self.tools]

        return (
            Path("src/prompts/ReAct.v2.txt")
            .read_text()
            .format(
                tools=tool_descriptions,
                # tools_list=tools_list,
                user_input=user_input,
            )
        )

    def run(self, user_input: str) -> str:
        """
        TODO: Implement the ReAct loop logic.
        1. Generate Thought + Action.
        2. Parse Action and execute Tool.
        3. Append Observation to prompt and repeat until Final Answer.
        """
        logger.log_event(
            "AGENT_START", {"input": user_input, "model": self.llm.model_name}
        )

        current_prompt = self.get_system_prompt(user_input)
        print(current_prompt)
        steps = 0

        total_tokens: int | None = None
        latency_ms = 0
        final_answer: str = (
            "Agent failed to solve the problem within the iteration limit."
        )

        while steps < self.max_steps:
            steps += 1

            logger.info(f"--- Iteration {steps} ---")
            response = self.llm.generate(current_prompt)
            llm_response = response["content"]

            if response["usage"]["total_tokens"]:
                if total_tokens is None:
                    total_tokens = 0
                total_tokens += response["usage"]["total_tokens"]

            latency_ms += response["latency_ms"]

            current_prompt += f"Observation: {llm_response}\n"
            logger.info(llm_response)

            if "Final Answer:" in llm_response:
                final_answer = llm_response.split("Final Answer:")[-1].strip()
                break

            action_match = re.search(r"Action:\s*(.*?)(?:\n|$)", llm_response)
            action_input_match = re.search(
                r"Action Input:\s*(.*?)(?:\n|$)", llm_response
            )

            if not action_match or not action_input_match:
                error_msg = "Observation: Error - Could not parse Action and Action Input. Please use the strict format."
                current_prompt += error_msg + "\n"
                logger.error(error_msg)
                continue

            action = action_match.group(1).strip()
            action_input = action_input_match.group(1).strip()

            observation = self._execute_tool(action, action_input)

            current_prompt += observation + "\n"
            logger.info(observation + "\n")

        logger.log_event(
            "AGENT_END",
            {"steps": steps, "latency_ms": latency_ms, "total_tokens": total_tokens},
        )
        return final_answer

    def _execute_tool(self, tool_name: str, args: str) -> str:
        """
        Helper method to execute tools by name.
        """

        for tool in self.tools:
            if tool["name"] == tool_name:
                return tool["func"](args)
        return f"Tool {tool_name} not found."
