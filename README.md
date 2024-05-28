# 

A brief description of what this project does and who it's for

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Installation

### Python pakage requirement
> pip install -r requirements.txt

### Stockfish chess engine
Download at https://stockfishchess.org/download/
After that, create a folder name "stockfish" in the codespace, then bring all stockfish's component to it.

### Chess games dataset and NNs model
Using 19000 chess games happen in 2023 for training, the source of dataset is from https://www.chess.com/forum/view/general/chess-pgn-database-over-9-million-games

Neural network architecture:
                                                    ->[4096x1]: Policy head
    [8x8x14]->[8x8x32]->[8x8x64]->[4x4x64]->[256x1]/
                                                   \
                                                    ->[1x1]: Value head
