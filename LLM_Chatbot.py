
def chatbot():
    import pandas as pd
    import langchain_community
    from langchain_community.document_loaders.csv_loader import CSVLoader
    from langchain.chains.combine_documents import create_stuff_documents_chain
    from langchain.chains import create_retrieval_chain
    from langchain_core.prompts import ChatPromptTemplate
    
    from langchain_chroma import Chroma
    from langchain_community.embeddings import SentenceTransformerEmbeddings
    from langchain_core.documents import Document
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_groq import ChatGroq
    from langchain_core.runnables import RunnablePassthrough
    
    # import LLM_Chatbot_v2
    # from LLM_Chatbot_v2 import prepa_chatbot
    
    import warnings
    warnings.filterwarnings("ignore")
    print("A")
    # prepa_chatbot()
    embeddings_model = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    db = Chroma(persist_directory="./chroma_db", embedding_function=embeddings_model)

    print("B")

    # attention 'apik' c'est la cle de groq donc il faut la changer à chaque utilisateur :
    
    apik ='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'
    
    def chat_groq(t = 0, choix ="llama3-70b-8192", api =apik  ) : #choix peu prendre : llama3-8b-8192 ,mixtral-8x7b-32768, gemma-7b-it
        return ChatGroq(temperature = t, model_name=choix, groq_api_key = api)

    model_chat = chat_groq()
    
    message = """
    Tu es un  assistant spécialisé dans les métiers de l'information. Ta responsabilité est de répondre de manière personnalisée, professionnelle et agréable.
    Les utilisateurs sont très probablement des personnes à la recherche d'un emploi qui recherchent des informations sur les emplois dans le domaine de Data.
    utilise ce contexte pour repondre. si tu n'as pas de réponse dis le
    {question}

    Context:
    {context}
    """
    print("C")
    retrier = db.as_retriever()
    print("D")
    prompt = ChatPromptTemplate.from_messages([("human", message)])

    rag_chain = {"context": retrier, "question": RunnablePassthrough()} | prompt | model_chat
    print("E")
    question = input("Ask a question! ")

    r = rag_chain.invoke(question)
    print(r.content)
    return r.content

chatbot()