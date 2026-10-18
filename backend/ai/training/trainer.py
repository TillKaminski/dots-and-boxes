"""Class for Training Process Definitions."""

from datetime import datetime
import os
import torch
import torch.nn as nn
import matplotlib.pyplot as plt

from backend.ai.config.params import TrainingConfig, ModelConfig
from ai.model.ffn import FeedForwardNet

from torch.utils.data import DataLoader, TensorDataset
from torch.optim.lr_scheduler import ReduceLROnPlateau
from sklearn.model_selection import train_test_split

base_dir = os.path.dirname(__file__)


class ModelTrainer:
    """Manages the training data setup, model configuration, and metrics calculation for the Feed-Forward Network (FFN)."""

    def __init__(self, training_file: str = "training_data_ffn.pt"):
        """Initializes the ModelTrainer, loading training data, preparing DataLoaders, and setting up the model, loss function, and optimizer."""
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        file_path = os.path.join(
            os.path.dirname(__file__), "../outputs/data", training_file
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
            dropout_rate=ModelConfig.DROPOUT_RATE,
        ).to(self.device)

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

        num_epochs = epochs if epochs else TrainingConfig.NUM_EPOCHS

        is_early_stopping_active = TrainingConfig.EARLY_STOPPING_ACTIVE

        best_val_loss = float("inf")
        patience = TrainingConfig.EARLY_STOPPING_PATIENCE
        counter = 0
        best_model_state = None
        best_epoch = 0
        final_epoch = num_epochs

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
            if is_early_stopping_active:
                if (val_loss - best_val_loss) < 1e-5:
                    best_val_loss = val_loss
                    best_model_state = self.model.state_dict()
                    best_epoch = epoch + 1
                    counter = 0
                else:
                    counter += 1
                    if counter >= patience:
                        final_epoch = epoch + 1
                        print(
                            f"\n\tINFO: No improvement for {patience} epochs. Stopping at Epoch {final_epoch}."
                        )
                        break
            else:
                if val_loss < best_val_loss:
                    best_val_loss = val_loss
                    best_model_state = self.model.state_dict()
                    best_epoch = epoch + 1

        if best_model_state:
            self.model.load_state_dict(best_model_state)

        print(
            f"\nTraining finished after {final_epoch} epochs. Best Val Loss: {best_val_loss:.4f}, Epoch: {best_epoch}"
        )

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

        axs[0].plot(losses, alpha=0.3, color="blue")
        axs[0].set_title("Batch Loss")
        axs[0].set_xlabel("Batch Update")
        axs[0].set_ylabel("Loss")

        if len(losses) > 100:
            window = 100
            smooth_loss = [
                sum(losses[i : i + window]) / window
                for i in range(len(losses) - window)
            ]
            axs[0].plot(smooth_loss, color="darkblue", label="Trend (Moving Avg)")
            axs[0].legend()

        ax_loss = axs[1]
        ax_acc = axs[1].twinx()

        lns1 = ax_loss.plot(avg_losses, color="red", label="Train Loss", linewidth=2)
        lns2 = ax_loss.plot(
            val_losses, color="orange", label="Val Loss", linestyle="--"
        )
        ax_loss.set_ylabel("Loss (CrossEntropy)")
        ax_loss.set_xlabel("Epoch")

        lns3 = ax_acc.plot(
            train_accuracies, color="green", label="Train Acc", linewidth=2
        )
        lns4 = ax_acc.plot(
            val_accuracies, color="lightgreen", label="Val Acc", linestyle="--"
        )
        ax_acc.set_ylabel("Accuracy (%)")
        ax_acc.set_ylim(0, 100)

        best_epoch = val_losses.index(min(val_losses))
        v_line = ax_loss.axvline(
            x=best_epoch, color="gray", linestyle=":", label="Best Model"
        )

        lines = lns1 + lns2 + lns3 + lns4 + [v_line]
        labs = [line.get_label() for line in lines]
        ax_loss.legend(lines, labs, loc="center right")

        ax_loss.set_title("Epoch Stats: Loss vs Accuracy")

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
