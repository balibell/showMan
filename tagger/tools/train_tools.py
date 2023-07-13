import random
from enum import Enum

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter
from tqdm import tqdm


class TrainConfig:
    def __init__(
            self,
            lr=1e-5,
            batch_size: int = 256,
            epochs: int = 3000,
            valid_ratio: float = 0.2,
            seed: int = 2023,
            early_stop: int = 100,
            # model_path='./models/model.ckpt',
            model_path='',
            device='cuda' if torch.cuda.is_available() else "cpu",
            log_path='/root/tf-logs/',
    ) -> None:
        super().__init__()
        self.lr = lr
        self.batch_size = batch_size
        self.epochs = epochs
        self.valid_ratio = valid_ratio
        self.seed = seed
        self.early_stop = early_stop
        self.model_path = model_path
        self.device = device
        self.log_dir = log_path

    def __str__(self) -> str:
        return f"lr: {self.lr}, batch_size: {self.batch_size}, epochs: {self.epochs}, valid_ratio: {self.valid_ratio}, seed: {self.seed}, early_stop: {self.early_stop}, model_path: {self.model_path}, device: {self.device}, log_dir: {self.log_dir}"


def same_seed(seed):
    '''Fixes random number generator seeds for reproducibility.'''
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True


class Activation(Enum):
    RELU = 1
    SIGMOID = 2
    TANH = 3
    LEAKY_RELU = 4


def get_activation(activation: Activation):
    if activation == Activation.RELU:
        return nn.ReLU()
    elif activation == Activation.SIGMOID:
        return nn.Sigmoid()
    elif activation == Activation.LEAKY_RELU:
        return nn.LeakyReLU()
    elif activation == Activation.TANH:
        return nn.Tanh()
    else:
        return None


class LinearBlock(nn.Module):
    def __init__(self, input_size: int, output_size: int, activation: Activation = Activation.RELU):
        super(LinearBlock, self).__init__()
        self.layers = nn.Sequential(
            nn.Linear(input_size, output_size),
            # nn.BatchNorm1d(output_size),
            get_activation(activation),
        )

    def forward(self, x):
        return self.layers(x)


def train_classifier(optimizer: torch.optim.Optimizer,
                     criterion: nn.Module,
                     model: nn.Module,
                     config: TrainConfig,
                     train_loader: DataLoader,
                     val_loader: DataLoader,
                     model_version="", ):
    stale, best_acc, step = 0, 0.0, 0
    writer = SummaryWriter(log_dir=config.log_dir + "/" + model_version)
    n_epochs, device, patience = config.epochs, config.device, config.early_stop
    for epoch in range(n_epochs):

        # ---------- Training ----------
        # Make sure the model is in train mode before training.
        model.train()

        # These are used to record information in training.
        train_loss = []
        train_accs = []

        train_pbar = tqdm(train_loader)
        for batch in train_pbar:
            # A batch consists of image data and corresponding labels.
            imgs, labels = batch
            # imgs = imgs.half()
            # print(imgs.shape,labels.shape)

            # Forward the data. (Make sure data and model are on the same device.)
            logits = model(imgs.to(device))

            # Calculate the cross-entropy loss.
            # We don't need to apply softmax before computing cross-entropy as it is done automatically.
            loss = criterion(logits, labels.to(device))
            # y = labels.to(device).to(torch.float)
            # y_hat = logits.view(logits.shape[0])
            # loss = criterion(y_hat, y)

            optimizer.zero_grad()

            # Compute the gradients for parameters.
            loss.backward()

            # Clip the gradient norms for stable training.
            grad_norm = nn.utils.clip_grad_norm_(model.parameters(), max_norm=10)

            # Update the parameters with computed gradients.
            optimizer.step()

            # Compute the accuracy for current batch.
            # acc = (logits.argmax(dim=-1) == labels.to(device)).float().mean()

            # Record the loss and accuracy.
            step += 1
            loss_item = loss.detach().item()
            train_loss.append(loss_item)

            acc = (logits.argmax(dim=-1) == labels.to(device)).float().mean()
            train_accs.append(acc)
            writer.add_scalar("Batch-Loss/train", loss_item, step)

            train_pbar.set_description(f'Epoch [{epoch + 1}/{n_epochs}]')
            train_pbar.set_postfix({'loss': loss_item})

        mean_train_loss = np.mean(train_loss)
        mean_train_acc = sum(train_accs) / len(train_accs)

        print(f"[ Train | {epoch + 1:03d}/{n_epochs:03d} ] loss = {mean_train_loss:.5f}, acc = {mean_train_acc:.5f}")
        writer.add_scalar("Loss/train", mean_train_loss, step)

        # ---------- Validation ----------
        # Make sure the model is in eval mode so that some modules like dropout are disabled and work normally.
        model.eval()

        # These are used to record information in validation.
        valid_loss = []
        valid_accs = []

        # Iterate the validation set by batches.
        for batch in tqdm(val_loader):
            # A batch consists of image data and corresponding labels.
            imgs, labels = batch
            # imgs = imgs.half()

            # We don't need gradient in validation.
            # Using torch.no_grad() accelerates the forward process.
            with torch.no_grad():
                logits = model(imgs.to(device))

            # We can still compute the loss (but not the gradient).
            loss = criterion(logits, labels.to(device))
            # y = labels.to(device).to(torch.float)
            # y_hat = logits.view(logits.shape[0])
            # loss = criterion(y_hat, y)

            # Compute the accuracy for current batch.
            acc = (logits.argmax(dim=-1) == labels.to(device)).float().mean()
            # acc = metric(y_hat, y)

            # Record the loss and accuracy.
            valid_loss.append(loss.item())
            valid_accs.append(acc)
            # break

        # The average loss and accuracy for entire validation set is the average of the recorded values.
        mean_valid_loss = np.mean(valid_loss)
        mean_valid_acc = sum(valid_accs) / len(valid_accs)

        # Print the information.
        print(f"[ Valid | {epoch + 1:03d}/{n_epochs:03d} ] loss = {mean_valid_loss:.5f}, acc = {mean_valid_acc:.5f}")

        writer.add_scalar("Loss/valid", mean_valid_loss, step)
        writer.add_scalar("Acc/valid", mean_valid_acc, step)

        # save models
        if mean_valid_acc > best_acc:
            print(
                f"[ Valid | {epoch + 1:03d}/{n_epochs:03d} ] loss = {mean_valid_loss:.5f}, acc = {mean_valid_acc:.5f} -> best")
            save_path = config.model_path
            if save_path:
                torch.save(model.state_dict(),
                           config.model_path)  # only save best to prevent output memory exceed error
            best_acc = mean_valid_acc
            stale = 0
        else:
            print(
                f"[ Valid | {epoch + 1:03d}/{n_epochs:03d} ] loss = {mean_valid_loss:.5f}, acc = {mean_valid_acc:.5f}")
            stale += 1
            if stale > patience:
                print(f"No improvement {patience} consecutive epochs, early stopping")
                break
    print('best model with acc {:.5f}...'.format(best_acc))
