from langchain_community.llms import OpenLLM

server_url = "http://localhost:8000"  # Replace with remote host if you are running on a remote server
llm = OpenLLM(base_url=server_url, api_key="na")

llm("To build a LLM from scratch, the following are the steps:")