"""Global Definition of Model- and Training-Parameters."""


class ModelConfig:
    """Model Parameters."""

    INPUT_SIZE = 56
    OUTPUT_SIZE = 40
    HIDDEN_LAYERS = [128, 128, 64]
    DROPOUT_RATE = 0.2


class TrainingConfig:
    """Training Hyperparameters."""

    LEARNING_RATE = 5e-4
    BATCH_SIZE = 32
    NUM_EPOCHS = 20
    DATA_FILE = "training_data_ffn.pt"
    LR_SCHEDULING = True
    EARLY_STOPPING_ACTIVE = True
    EARLY_STOPPING_PATIENCE = 7


class DeploymentConfig:
    """Path-Definition of final Model."""

    MODEL_PATH = "outputs/model/final_model.pt"
