import os
import typer
from typing import Optional
from rich.prompt import Prompt

from phi.assistant import Assistant
from phi.knowledge.pdf import PDFUrlKnowledgeBase
from phi.vectordb.pineconedb import PineconeDB
from phi.llm.anthropic import Claude
from phi.embedder.voyageai import VoyageAIEmbedder

anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
pinecone_api_key = os.getenv("PINECONE_API_KEY")
voyage_api_key = os.getenv("VOYAGE_API_KEY")

index_name = "thai-recipe"

vector_db = PineconeDB(
    name=index_name,
    dimension=1024,
    metric="cosine",
    spec={"serverless": {"cloud": "aws", "region": "us-east-1"}},
    api_key=pinecone_api_key,
    embedder=VoyageAIEmbedder(model="voyage-2", api_key=voyage_api_key),
)

knowledge_base = PDFUrlKnowledgeBase(
    urls=["https://phi-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
    vector_db=vector_db,
)

# Comment out after first run
knowledge_base.load(recreate=False, upsert=True)


def pinecone_assistant(user: str = "user"):
    run_id: Optional[str] = None

    assistant = Assistant(
        llm=Claude(model="claude-3-5-sonnet-20240620", api_key=anthropic_api_key),
        run_id=run_id,
        user_id=user,
        knowledge_base=knowledge_base,
        tool_calls=True,
        use_tools=True,
        show_tool_calls=True,
        debug_mode=True,
        # Uncomment the following line to use traditional RAG
        # add_references_to_prompt=True,
    )

    if run_id is None:
        run_id = assistant.run_id
        print(f"Started Run: {run_id}\n")
    else:
        print(f"Continuing Run: {run_id}\n")

    while True:
        message = Prompt.ask(f"[bold] :sunglasses: {user} [/bold]")
        if message in ("exit", "bye"):
            break
        assistant.print_response(message)


if __name__ == "__main__":
    typer.run(pinecone_assistant)
