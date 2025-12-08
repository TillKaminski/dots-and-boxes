"""Class for Training Process Definitions."""

from datetime import datetime
import os
import torch
import torch.nn as nn
import matplotlib.pyplot as plt

from ai.config.params import TrainingConfig, ModelConfig
from ai.model.ffn_model import FeedForwardNet

from torch.utils.data import DataLoader, TensorDataset
from torch.optim.lr_scheduler import ReduceLROnPlateau
from sklearn.model_selection import train_test_split


base_dir = os.path.dirname(__file__)


class ModelTrainer:
    """Manages the training data setup, model configuration, and metrics calculation for the Feed-Forward Network (FFN)."""

    def __init__(self):
        """Initializes the ModelTrainer, loading training data, preparing DataLoaders, and setting up the model, loss function, and optimizer."""
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        file_path = os.path.join(
            os.path.dirname(__file__), "../outputs", "training_data_ffn.pt"
        )
        data = torch.load(file_path, map_location=self.device)

        x_data = torch.stack([x for x, _ in data])

        y_data_one_hot = torch.stack([y for _, y in data])
        y_data = y_data_one_hot.argmax(dim=1).type(torch.long)

        self.x_train, self.x_val, self.y_train, self.y_val = train_test_split(
            x_data, y_data, test_size=0.2, stratify=y_data, random_state=42
        )

        self.train_loader = DataLoader(
            TensorDataset(self.x_train, self.y_train),
            batch_size=TrainingConfig.BATCH_SIZE,
            shuffle=True,
        )

        self.val_loader = DataLoader(
            TensorDataset(self.x_val, self.y_val), batch_size=TrainingConfig.BATCH_SIZE
        )

        self.model = FeedForwardNet(
            input_size=ModelConfig.INPUT_SIZE,
            hidden_layers=ModelConfig.HIDDEN_LAYERS,
            output_size=ModelConfig.OUTPUT_SIZE,
        )

        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = torch.optim.Adam(
            self.model.parameters(), lr=TrainingConfig.LEARNING_RATE
        )

        self.scheduler = None
        if TrainingConfig.LR_SCHEDULING:
            self.scheduler = ReduceLROnPlateau(
                self.optimizer, mode="min", factor=0.5, patience=3
            )

    def train(self, epochs: int | None):
        """Trains the model over a specified number of epochs. It uses configurations defined in TrainingConfig and ModelConfig for parameters like learning rate and scheduling."""
        losses, avg_losses, train_accuracies = [], [], []
        val_losses, val_accuracies = [], []

        if epochs:
            num_epochs = epochs
        else:
            num_epochs = TrainingConfig.NUM_EPOCHS

        for epoch in range(num_epochs):
            self.model.train()
            epoch_loss = 0

            for x_batch, y_batch in self.train_loader:
                x_batch, y_batch = x_batch.to(self.device), y_batch.to(self.device)
                self.optimizer.zero_grad()
                output = self.model(x_batch)
                loss = self.criterion(output, y_batch)
                loss.backward()
                self.optimizer.step()
                epoch_loss += loss.item()
                losses.append(loss.item())

            avg_loss = epoch_loss / len(self.train_loader)
            avg_losses.append(avg_loss)
            train_acc = self.calculate_accuracy(self.train_loader)
            train_accuracies.append(train_acc)

            val_loss, val_acc = self.calculate_validation()
            val_losses.append(val_loss)
            val_accuracies.append(val_acc)

            print(
                f"Epoch {epoch+1}/{num_epochs} | Loss: {avg_loss:.4f} | Train Acc: {train_acc:.2f}% | Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.2f}%"
            )

            if self.scheduler:
                self.scheduler.step(val_loss)

        self.plot_metrics(
            losses, avg_losses, train_accuracies, val_losses, val_accuracies
        )
        self.save_model()

    def calculate_accuracy(self, loader):
        """Calculates the classification accuracy of the model."""
        correct, total = 0, 0
        self.model.eval()
        with torch.no_grad():
            for x, y in loader:
                x, y = x.to(self.device), y.to(self.device)
                prediction = self.model(x).argmax(dim=1)
                correct += (prediction == y).sum().item()
                total += y.size(0)
        return correct / total * 100

    def calculate_validation(self):
        """Calculates the loss and accuracy metrics on the validation dataset."""
        val_loss, correct, total = 0.0, 0, 0
        self.model.eval()
        with torch.no_grad():
            for x, y in self.val_loader:
                x, y = x.to(self.device), y.to(self.device)
                output = self.model(x)
                val_loss += self.criterion(output, y).item()
                correct += (output.argmax(dim=1) == y).sum().item()
                total += y.size(0)
        return val_loss / len(self.val_loader), correct / total * 100

    def plot_metrics(
        self, losses, avg_losses, train_accuracies, val_losses, val_accuracies
    ):
        """Generates and saves a figure illustrating the training history, including batch loss, epoch loss, and train/validation accuracy."""
        fig, axs = plt.subplots(1, 2, figsize=(12, 4))

        axs[0].plot(losses)
        axs[0].set_title("Batch Loss")
        axs[0].set_xlabel("Batch")
        axs[0].set_ylabel("Loss")

        axs[1].plot(avg_losses, label="Train Loss")
        axs[1].plot(val_losses, label="Val Loss")
        axs[1].plot(train_accuracies, label="Train Acc")
        axs[1].plot(val_accuracies, label="Val Acc")
        axs[1].legend()
        axs[1].set_title("Epoch Stats")
        axs[1].set_xlabel("Epoch")

        plt.tight_layout()
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        filename = os.path.join(
            base_dir, "..", "outputs", "img_training", f"training_{timestamp}.png"
        )
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        plt.savefig(filename)

    def save_model(self):
        """Saves the trained model to the 'outputs/model' folder, using a timestamp in the filename."""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = os.path.join(
            base_dir, "..", "outputs", "model", f"model_ffn_{timestamp}.pt"
        )
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        torch.save(self.model.state_dict(), filename)
