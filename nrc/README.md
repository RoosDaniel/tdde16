# NRC-implementaton

The code in `nrc.py` can be hard to interpret. The functions `process_all_remaining`, `add_scores`, `generate_data` and `vectorize_data` all have to be run (in that order) to get the final representation used to train the neural network. The intermediate `json`-files served as checkpoints if I needed to modify anything during development, since the files were quite big and took long to generate.
