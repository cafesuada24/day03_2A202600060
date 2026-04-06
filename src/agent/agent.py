import json
import re
from pathlib import Path
from typing import Any, Dict, List

from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger


class ReActAgent:
    def __init__(
        self, llm: LLMProvider, tools: List[Dict[str, Any]], max_steps: int = 5
    ):
        self.llm = llm
        self.tools = tools
        self.max_steps = max_steps
        self.tool_map = {t["name"]: t["func"] for t in self.tools}

    def get_system_prompt(self, user_input: str) -> str:
        """
        Tạo prompt hệ thống bằng cách nạp từ file và format các biến.
        Hỗ trợ cả v1 và v2 để tránh lỗi KeyError.
        """
        descriptions = "\n".join(
            [f"- {t['name']}: {t['description']}" for t in self.tools]
        )
        names = ", ".join([t["name"] for t in self.tools])

        prompt_path = Path("src/prompts/ReAct.v2.txt")
        if not prompt_path.exists():
            prompt_path = Path("src/prompts/ReAct.v1.txt")

        prompt_text = prompt_path.read_text()

        return prompt_text.format(
            tools=descriptions,
            tool_descriptions=descriptions,  # Cho các template dùng tên khác
            tool_names=names,
            user_input=user_input,
        )

    def run(self, user_input: str) -> str:
        current_prompt = self.get_system_prompt(user_input)
        steps = 0

        while steps < self.max_steps:
            steps += 1
            logger.info(f"--- Iteration {steps} ---")

            # Gọi LLM
            response = self.llm.generate(current_prompt)
            llm_output = response["content"]

            # Lưu vào ngữ cảnh
            current_prompt += f"\n{llm_output}\n"

            # Kiểm tra nếu đã có câu trả lời cuối cùng
            if "Final Answer:" in llm_output:
                return llm_output.split("Final Answer:")[-1].strip()

            # Parse Action và Action Input
            action_match = re.search(r"Action:\s*\[?(\w+)\]?", llm_output)
            action_input_match = re.search(r"Action Input:\s*(.*)", llm_output)

            if action_match and action_input_match:
                tool_name = action_match.group(1).strip()
                tool_input = action_input_match.group(1).strip()

                # Thực hiện tool
                observation = self._execute_tool(tool_name, tool_input)

                # Cập nhật kết quả quan sát vào prompt
                obs_text = f"Observation: {observation}"
                current_prompt += f"{obs_text}\n"
                logger.info(obs_text)
            else:
                # Nhắc nhở model nếu nó quên format
                error_prompt = "Observation: Error - Invalid format. Use Thought, Action, Action Input, Observation."
                current_prompt += f"{error_prompt}\n"
                logger.error("Format error from LLM")

        return "Agent reached max steps without a final answer."

    def _execute_tool(self, tool_name: str, args_str: str) -> str:
        if tool_name not in self.tool_map:
            return f"Error: Tool '{tool_name}' not found."

        func = self.tool_map[tool_name]
        try:
            try:
                clean_args = args_str.strip().replace("'", '"')
                params = json.loads(clean_args)
                if isinstance(params, dict):
                    return json.dumps(func(**params))
            except:
                pass

            if "," in args_str:
                args_list = [
                    a.strip().strip('"').strip("'") for a in args_str.split(",")
                ]
                processed_args = []
                for x in args_list:
                    try:
                        processed_args.append(float(x) if "." in x else int(x))
                    except:
                        processed_args.append(x)

                return json.dumps(
                    func(*processed_args)
                )  # Unpack list thành các tham số rời

            clean_val = args_str.strip().strip('"').strip("'")
            return json.dumps(func(clean_val))

        except Exception as e:
            return f"Execution Error: {str(e)}"
