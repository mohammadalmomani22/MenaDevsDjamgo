from django.shortcuts import render
from requests import Response
from rest_framework.views import APIView
import os
from langchain_community.llms import Ollama
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_community.document_loaders import PDFPlumberLoader
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain.prompts import PromptTemplate

from estthmar.utlls import parse_questions


folder_path = "chroma_db"

cached_llm = Ollama(model="llama3")

embedding = FastEmbedEmbeddings()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1024, chunk_overlap=80, length_function=len, is_separator_regex=False
)


raw_prompt = PromptTemplate.from_template(
""" 
### Financial Assistant Feasibility Study Prompt
**[Introduction]**
You are regarded as an expert financial assistant with specialized skills in conducting feasibility studies for various projects. I am currently exploring a new project initiative and need your expertise to assess its potential for success. Please carry out a detailed feasibility study to evaluate the viability of this proposed project. Your analysis should provide in-depth suggestions and consultations aimed at optimizing the project’s success.
**[Objective]**
Conduct a comprehensive feasibility study that explores all relevant aspects of the proposed project. Your findings should help us make informed decisions regarding the project's potential and strategies for moving forward.
**[Request for Preliminary Questions]**
To ensure a thorough and accurate feasibility study, please develop a list of preliminary questions based on the project details I will provide. These questions should serve as a guide for our discussions and assist in collecting all necessary information needed for a comprehensive evaluation.
### Example of Preliminary Questions Required
Here is an outline of the type of questions that would guide our feasibility study. These questions are designed to delve into various critical aspects of the project:
- **Q1:** Who are the targeted customer segments?
- **Q2:** What is the target market?
- **Q3:** What is the specific problem that the project aims to solve?
- **Q4:** What is the proposed solution to this problem?
- **Q5:** What evidence supports the Problem-Solution fit?
- **Q6:** What is the unique value proposition of the project?
- **Q7:** What are the detailed product specifications?
- **Q8:** What evidence supports the Product-Market fit?
- **Q9:** Through which distribution channels will the product be marketed?
- **Q10:** What are the planned revenue streams and the sales strategy?
- **Q11:** How does the project position itself against competitors?
- **Q12:** What resources are required, and what is the plan for their acquisition?
- **Q13:** What is the detailed cost structure of the project?
- **Q14:** How will the project develop and capture value?
- **Q15:** What strategies will be implemented to develop, retain, and grow the customer base?
- **Q16:** What is the total investment cost of the project, and how will it be funded?
- **Q17:** How will you validate the business model?
- **Q18:** What is the Minimum Viable Business Product (MVBP)?
- **Q19:** What are the financial projections for the project?
- **Q20:** What is the evidence of the project’s viability?
- **Q21:** What is the detailed implementation plan?
**[Input Instructions]**
- **[INST] query Project: {context}**
- **Answer:** Based on the provided Project, enumerate the key questions we should address to advance the feasibility study.
**[End of Instruction]**
"""
)

# Create your views here.
def home(request):
    return render(request,'home.html',{})

class AIView(APIView):
    def post(self, request):
        data = request.data
        query = data.get("query")
        
        chain = raw_prompt | cached_llm
        result = chain.invoke({"context": query})
        response = cached_llm.invoke(query)
        questions_dictionary = parse_questions(response)
        return Response(questions_dictionary)

class AskPDFView(APIView):
    def post(self, request):
        data = request.data
        query = data.get("query")
        vector_store = Chroma(persist_directory=folder_path, embedding_function=embedding)
        retriever = vector_store.as_retriever(search_type="similarity_score_threshold", search_kwargs={"k": 20, "score_threshold": 0.1})
        document_chain = create_stuff_documents_chain(cached_llm, raw_prompt)
        chain = create_retrieval_chain(retriever, document_chain)
        result = chain.invoke({"input": query})
        sources = [{"source": doc.metadata["source"], "page_content": doc.page_content} for doc in result["context"]]
        return Response({"answer": result["answer"], "sources": sources})

class PDFView(APIView):
    def post(self, request):
        file = request.FILES['file']
        file_name = file.name
        save_file = "pdf/" + file_name
        file.save(save_file)
        loader = PDFPlumberLoader(save_file)
        docs = loader.load_and_split()
        chunks = text_splitter.split_documents(docs)
        vector_store = Chroma.from_documents(documents=chunks, embedding=embedding, persist_directory=folder_path)
        vector_store.persist()
        return Response({
            "status": "Successfully Uploaded",
            "filename": file_name,
            "doc_len": len(docs),
            "chunks": len(chunks),
        })
