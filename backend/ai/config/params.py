"""Global Definition of Model- and Training-Parameters."""


class ModelConfig:
    """Model Parameters."""

    INPUT_SIZE = 50
    OUTPUT_SIZE = 50
    HIDDEN_LAYERS = [128, 64]


class TrainingConfig:
    """Training Hyperparameters."""

    LEARNING_RATE = 1e-3
    BATCH_SIZE = 32
    NUM_EPOCHS = 20
    DATA_FILE = "training_data.json"


class DeploymentConfig:
    """Path-Definition of final Model."""

    MODEL_PATH = "outputs/final_model.pt"
