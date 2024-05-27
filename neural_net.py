import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset
from data_preprocessing import parse_pgn_to_tensor, ChessDataset

class NeuralNet(nn.Module):
    def __init__(self, input_shape=(8, 8, 14)):
        """input_shape: tuple, shape of the input tensor (height, width, channels)
            14 channels = 6 channels for white pieces: Pawn, Knight, Bishop, Rook, Queen, King
                          6 channels for black pieces:
                          1 channel for indicating if it's white's turn: All 1s if white, 0s if black
                          1 channel for special rules: E.g., castling rights or en passant availability
        """
        super(NeuralNet, self).__init__()
        
        # Define the neural network architecture
        # Convolutional layers
        self.conv1 = nn.Conv2d(input_shape[2], 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)
        
        # Fully connected layers
        self.fc1 = nn.Linear(64 * 4 * 4, 256)
        
        # Policy head
        self.policy_head = nn.Linear(256, 4096) # Assume there are 4096 possible moves in a turn
        
        # Value head
        self.value_head = nn.Linear(256, 1) # Output a evaluation score between -1 and 1
        
    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = self.pool(x)
        
        x = x.view(-1, 64 * 4 * 4) # Flatten the tensor

        x = F.relu(self.fc1(x))
        
        policy = F.softmax(self.policy_head(x), dim=1)
        evaluation = torch.tanh(self.value_head(x))
        
        return policy, evaluation
    
    def train_model(self, model, train_loader, epochs, learning_rate=0.01):
        optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
        criteration_policy = nn.CrossEntropyLoss()
        criteration_value = nn.MSELoss()
        
        model.train()
        for epoch in range(epochs):
            total_loss_policy = 0
            total_loss_value = 0
            
            for data in train_loader:
                inputs, policy_targets = data
                optimizer.zero_grad()
                
                policy_pred, value_pred = model(inputs)
                
                # Convert policy_targets to Tensor
                policy_targets = torch.tensor(policy_targets, dtype=torch.long)
            
                policy_loss = criteration_policy(policy_pred, policy_targets)
                value_loss = criteration_value(value_pred, torch.zeros_like(value_pred))
                
                loss = policy_loss + value_loss
                loss.backward()
                optimizer.step()
                
                total_loss_policy += policy_loss.item()
                total_loss_value += value_loss.item()
            
            print(f"Epoch {epoch + 1}/{epochs}, Policy loss: {total_loss_policy}, Value loss: {total_loss_value}")
            
# Example usage
positions, moves = parse_pgn_to_tensor("db.pgn")

dataset = ChessDataset(positions, moves)
dataloader = DataLoader(dataset, batch_size=32, shuffle=True)

model = NeuralNet(input_shape=(8, 8, 14))
model.train_model(model=model, train_loader=dataloader, epochs=10)
