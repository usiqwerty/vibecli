import json
import logging

from agents import OpenAIChatCompletionsModel, TResponseInputItem, ModelSettings, Tool, AgentOutputSchemaBase, Handoff, \
    ModelTracing, ModelResponse, generation_span, _debug, Usage
from agents.logger import logger
from agents.models.openai_chatcompletions import Converter


class TunedModel(OpenAIChatCompletionsModel):
    async def get_response(
            self,
            system_instructions: str | None,
            input: str | list[TResponseInputItem],
            model_settings: ModelSettings,
            tools: list[Tool],
            output_schema: AgentOutputSchemaBase | None,
            handoffs: list[Handoff],
            tracing: ModelTracing,
            previous_response_id: str | None,
    ) -> ModelResponse:
        with generation_span(
                model=str(self.model),
                model_config=model_settings.to_json_dict() | {"base_url": str(self._client.base_url)},
                disabled=tracing.is_disabled(),
        ) as span_generation:
            response = await self._fetch_response(
                system_instructions,
                input,
                model_settings,
                tools,
                output_schema,
                handoffs,
                span_generation,
                tracing,
                stream=False,
            )
            if response.choices is None:
                logging.debug(response.model_extra)
            else:
                if _debug.DONT_LOG_MODEL_DATA:
                    logger.debug("Received model response")
                else:
                    logger.debug(
                        f"LLM resp:\n{json.dumps(response.choices[0].message.model_dump(), indent=2)}\n"
                    )

            usage = (
                Usage(
                    requests=1,
                    input_tokens=response.usage.prompt_tokens,
                    output_tokens=response.usage.completion_tokens,
                    total_tokens=response.usage.total_tokens,
                )
                if response.usage
                else Usage()
            )
            if tracing.include_data():
                span_generation.span_data.output = [response.choices[0].message.model_dump()]
            span_generation.span_data.usage = {
                "input_tokens": usage.input_tokens,
                "output_tokens": usage.output_tokens,
            }

            items = Converter.message_to_output_items(response.choices[0].message)

            return ModelResponse(
                output=items,
                usage=usage,
                response_id=None,
            )
