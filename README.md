# Simple Neural MCTS for chess


## Table of Contents

- [Installation](#installation)
- [Usage](#usage)

## Installation

### Python pakage requirement
``` pip install -r requirements.txt ```

### Stockfish chess engine and the Agent
Download stockfish at [here](https://stockfishchess.org/download/) \\
After that, create a folder name "stockfish" in the codespace, then bring all stockfish's component to it.
The agent is simulated by stockfish based on the Elo rating.

### Chess games dataset and NNs model
Using 19000 chess games happen in 2023 for training, the source of dataset is from [chess.com](https://www.chess.com/forum/view/general/chess-pgn-database-over-9-million-games)

Neural network architecture: \\
```                                             
    [8x8x14]->[8x8x32]->[8x8x64]->[4x4x64]->[256x1]->[4096x1]: Policy head
                                                   ->[1x1]: Value head
```
## Usage
### Play game
```py mcts.py```