import os
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage

class MockChatModel(BaseChatModel):
    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        last_msg = messages[-1].content
        return {
            "generations": [
                {
                    "text": f"MOCK RESPONSE: Processed '{last_msg[:20]}...'",
                    "message": AIMessage(content=f"MOCK RESPONSE: Processed '{last_msg[:20]}...'")
                }
            ]
        }
    
    @property
    def _llm_type(self):
        return "mock"

from .config_store import ConfigStore

class LLMFactory:
    @staticmethod
    def get_llm(config_override: dict = None) -> BaseChatModel:
        if config_override:
            # Ephemeral testing mode
            provider = config_override.get("llm_provider", "mock").lower()
            store_data = config_override # Expecting the full config dict structure or just the flat params?
            # Let's assume config_override mimics the ConfigStore structure for simplicity
            azure = config_override.get("azure_config", {})
            aws = config_override.get("aws_config", {})
            google = config_override.get("google_config", {})
        else:
            # Normal mode
            config_store = ConfigStore()
            provider = config_store.get_llm_provider().lower()
            azure = config_store.get_azure_details()
            aws = config_store.get_aws_details()
            google = config_store.get_google_details()

        if provider == "azure":
            from langchain_openai import AzureChatOpenAI
            return AzureChatOpenAI(
                azure_endpoint=azure.get("endpoint") or os.getenv("AZURE_OPENAI_ENDPOINT"),
                api_key=azure.get("api_key") or os.getenv("AZURE_OPENAI_API_KEY"),
                azure_deployment=azure.get("deployment") or os.getenv("AZURE_OPENAI_DEPLOYMENT"),
                api_version=azure.get("api_version") or os.getenv("AZURE_OPENAI_API_VERSION"),
                model_name=azure.get("model_name")
            )
            
        elif provider == "aws":
            from langchain_aws import ChatBedrock
            return ChatBedrock(
                model_id=aws.get("model_id") or os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0"),
                region_name=aws.get("region") or os.getenv("AWS_REGION", "us-east-1"),
                aws_access_key_id=aws.get("access_key_id"),
                aws_secret_access_key=aws.get("secret_access_key")
            )
            
        elif provider == "google":
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(
                model=google.get("model") or os.getenv("GOOGLE_MODEL", "gemini-1.5-pro"),
                google_api_key=google.get("api_key") or os.getenv("GOOGLE_API_KEY")
            )
            
        else:
            print(f"!!! [LLMFactory] Using MOCK LLM (Provider: {provider})")
            return MockChatModel()
