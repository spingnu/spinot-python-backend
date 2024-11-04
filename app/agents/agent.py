from typing import List, Literal

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain import hub
from langchain.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_community.vectorstores import SupabaseVectorStore
from langchain_core.output_parsers import StrOutputParser
from supabase.client import Client
from typing_extensions import TypedDict

from app.supabase_client import supabase

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

class State(TypedDict):
    question: str
    generation: str
    documents: List[str]


class GradeDocuments(BaseModel):
    binary_score: str = Field(
        description="Documents are relevant to the question, 'yes' or 'no'"
    )

class RouteQuery(BaseModel):
    """Route a user query to the most relevant datasource."""

    datasource: Literal["twitter", "media"] = Field(
        ...,
        description="Given a user question choose to route it to twitter search or media(news, articles, blogs) search.",
    )

class GradeHallucinations(BaseModel):
    """Binary score for hallucination present in generation answer."""

    binary_score: str = Field(
        description="Answer is grounded in the facts, 'yes' or 'no'"
    )


def create_grader():
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    structured_llm_grader = llm.with_structured_output(GradeDocuments)

    system = """You are a grader assessing relevance of a retrieved document to a user question. \n
        If the document contains keyword(s) or semantic meaning related to the question, grade it as relevant. \n
        Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question."""
    grade_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "Retrieved document: \n\n {document} \n\n User question: {question}"),
        ]
    )
    retrieval_grader = grade_prompt | structured_llm_grader
    return retrieval_grader


def create_router():
    # LLM with function call
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    structured_llm_router = llm.with_structured_output(RouteQuery)

    # Prompt
    system = """You are an expert at routing a user question to tweets from user timeline or articles from media
    like coindesk, blockmedia, etc.
    The tweets contains user's short comments about current crypto markets, narratives, and latest cutting edge trend or research,
    The media contains detailed articles about the latest crypto trend, in more comprehensive and detailed manner,
    often containing reporter's opinions and analysis with longer content. Choose wisely based on the user question."""
    route_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "{question}"),
        ]
    )

    question_router = route_prompt | structured_llm_router
    return question_router


def create_answer_generator():
    llm = ChatOpenAI(model_name="gpt-4o", temperature=0)

    prompt = hub.pull("rlm/rag-prompt")
    # Chain
    rag_chain = prompt | llm | StrOutputParser()
    return rag_chain


def create_query_rewriter():
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    system = """You are a question rewriter that converts an input question to a better version that is optimized \n
        for internal document search. Look at the question and the optional retrieved documents, then try to reformulate the query by
        common knowledge or adding the key phrases from the documents if available."""
    re_write_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            (
                "human",
                "Here is the question: \n\n {question} document: {document} \n\n Formulate an improved question.",
            ),
        ]
    )
    question_rewriter = re_write_prompt | llm | StrOutputParser()
    return question_rewriter


def create_hallucination_grader():
    # LLM with function call
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    structured_llm_grader = llm.with_structured_output(GradeHallucinations)

    # Prompt
    system = """You are a grader assessing whether an LLM generation is grounded in / supported by a set of retrieved facts. \n
        Give a binary score 'yes' or 'no'. 'Yes' means that the answer is grounded in / supported by the set of facts."""
    hallucination_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "Set of facts: \n\n {documents} \n\n LLM generation: {generation}"),
        ]
    )
    hallucination_grader = hallucination_prompt | structured_llm_grader
    return hallucination_grader


def build_graph():
    coindesk_store = SupabaseVectorStore(client=supabase, embedding=OpenAIEmbeddings(), table_name="coindesk")
    retriever = coindesk_store.as_retriever()

    tweet_store = SupabaseVectorStore(client=supabase, embedding=OpenAIEmbeddings(), table_name="tweets")
    tweet_retriever = tweet_store.as_retriever()

    router = create_router()
    generator = create_answer_generator()
    query_rewriter = create_query_rewriter()
    grader = create_grader()
    hallucination_grader = create_hallucination_grader()

    # Nodes
    def coindesk_retrieve(state):
        documents = retriever.invoke(state["question"])
        return {"documents": documents, "question": state["question"]}

    def tweet_retrieve(state):
        documents = tweet_retriever.invoke(state["question"])
        return {"documents": documents, "question": state["question"]}

    def generate(state):
        generation = generator.invoke(({"context": state["documents"], "question": state["question"]}))
        return {"generation": generation, "documents": state["documents"], "question": state["question"]}

    def grade_documents(state):
        filtered = []
        for doc in state["documents"]:
            score = grader.invoke({"document": doc, "question": state["question"]})
            grade = score.binary_score
            if grade == "yes":
                filtered.append(doc)
        return {"documents": filtered, "question": state["question"]}

    def rewrite_query(state):
        better_question = query_rewriter.invoke({"question": state["question"]})
        return {"documents": state["documents"], "question": better_question}

    # Edges
    def route_question(state):
        question = state["question"]
        source = router.invoke({"question": question})
        if source.datasource == "tweets":
            return "tweets"
        elif source.datasource == "media":
            return "media"

    def decide_to_generate(state):
        filtered_documents = state["documents"]
        if not filtered_documents:
            return "rewrite_query"
        else:
            return "generate"

    def grade_answer(state):
        score = hallucination_grader.invoke(
            {"documents": state["documents"], "generation": state["generation"]}
        )
        # Check hallucination
        if score.binary_score == "yes":
            return "useful"
        else:
            return "not useful"

    builder = StateGraph(State)
    builder.add_node("coindesk_retrieve", coindesk_retrieve)
    builder.add_node("tweets_retrieve", tweet_retrieve)
    builder.add_node("generate", generate)
    builder.add_node("grade_documents", grade_documents)
    builder.add_node("rewrite_query", rewrite_query)

    builder.add_conditional_edges(START, route_question, {
        "tweets": "tweets_retrieve",
        "media": "coindesk_retrieve",
    })
    builder.add_edge("coindesk_retrieve", "grade_documents")
    builder.add_edge("tweets_retrieve", "grade_documents")
    builder.add_conditional_edges("grade_documents", decide_to_generate, {
        "rewrite_query": "rewrite_query",
        "generate": "generate",
    })
    builder.add_conditional_edges("rewrite_query", START)
    builder.add_conditional_edges(
        "generate", grade_answer, {"useful": END, "not useful": "rewrite_query"}
    )

    return builder.compile(checkpointer=MemorySaver())
