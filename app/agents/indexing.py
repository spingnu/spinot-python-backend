from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import SupabaseVectorStore
from langchain_openai import OpenAIEmbeddings

# Set embeddings
embd = OpenAIEmbeddings()

# Add to vectorstore
vectorstore = SupabaseVectorStore.from_texts(
    texts=texts,
    collection_name="rag-chroma",
    embedding=embd,
)

retriever = vectorstore.as_retriever()
