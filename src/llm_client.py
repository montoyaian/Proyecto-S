from langchain_aws import ChatBedrockConverse

from .config import (
    AWS_REGION,
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    BEDROCK_MODEL
)


def crear_llm():

    kwargs = {
        "region_name": AWS_REGION,
        "model_id": BEDROCK_MODEL
    }

    if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
        kwargs.update(
            {
                "aws_access_key_id": AWS_ACCESS_KEY_ID,
                "aws_secret_access_key": AWS_SECRET_ACCESS_KEY
            }
        )

    return ChatBedrockConverse(
        **kwargs
    )
