chunk_params = [
        {
            "id": "chunk_1",
            "chunk_size": 512, 
            "chunk_overlap": 0,
        },
        {
            "id": "chunk_2",
            "chunk_size": 512, 
            "chunk_overlap": 8,
        },
        {
            "id": "chunk_3",
            "chunk_size": 512, 
            "chunk_overlap": 16,
        },
        {
            "id": "chunk_4",
            "chunk_size": 512, 
            "chunk_overlap": 32,
        },
        {
            "id": "chunk_5",
            "chunk_size": 512, 
            "chunk_overlap": 0,
        },
        {
            "id": "chunk_6",
            "chunk_size": 512, 
            "chunk_overlap": 8,
        },
        {
            "id": "chunk_7",
            "chunk_size": 512, 
            "chunk_overlap": 16,
        },
        {
            "id": "chunk_8",
            "chunk_size": 512, 
            "chunk_overlap": 32,
        },
]

import json

with open("chunk_params.json", "w") as f:
    json.dump(chunk_params, f)
