from sentence_transformers import SentenceTransformer
import json
import torch
from sentence_transformers import util

async def parse_messages(query, messages):
    if messages is not []:
        passages = []
        for ind_m, each_message in enumerate(messages):
            passages.append([ind_m, each_message.content])

        model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

        embeddings = model.encode(passages, convert_to_tensor=True)

        query_list = [query]

        query = model.encode(query_list, convert_to_tensor=True)

        cos_scores = util.cos_sim(query, embeddings)
        cos_scores.shape

        torch.Size([2, 2014])
        
        top_results = torch.topk(cos_scores, k=3, dim=-1)


        indices = top_results.indices.tolist()

        p_messages =[]
        for result in indices:
            for idx in result:
                p_messages.append(messages[passages[idx][0]])

        return p_messages
    else:
        return []

