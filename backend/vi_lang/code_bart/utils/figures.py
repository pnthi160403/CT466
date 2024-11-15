import matplotlib.pyplot as plt
import pandas as pd
import torch
import json
import zipfile
import os
from .folders import (
    join_base,
    read,
    write,
    get_weights_file_path,
)

class LossFigure:
    def __init__(
        self,
        xlabel: str,
        ylabel: str,
        title: str,
        loss_value_path: str,
        loss_step_path: str,
    ):
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.title = title

        self.loss_value_path = loss_value_path
        self.loss_step_path = loss_step_path
        self.loss_value = []
        self.loss_step = []
        if os.path.exists(loss_value_path) and os.path.exists(loss_step_path):
            self.loss_value = read(loss_value_path)
            self.loss_step = read(loss_step_path)

    def update(
        self,
        value: float,
        step: int,
    ):
        if len(self.loss_step) != 0 and step < self.loss_step[-1] and step >= 0:
            find_index = self.loss_step.index(step)
            self.loss_value[find_index] = value
        else:
            self.loss_value.append(value)
            self.loss_step.append(step)

    def save(self):
        write(self.loss_value_path, self.loss_value)
        write(self.loss_step_path, self.loss_step)

    def load(self):
        self.loss_value = read(self.loss_value_path)
        self.loss_step = read(self.loss_step_path)

# figures
def draw_graph(config, title, xlabel, ylabel, data, steps, log_scale=True):
    try:
        save_path = join_base(config['log_dir'], f"/{title}.png")
        plt.plot(steps, data)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        if log_scale:
            plt.yscale('log')
        plt.grid(True)
        plt.savefig(save_path)
        plt.show()
        plt.close()
    except Exception as e:
        print(e)

def draw_multi_graph(config, title, xlabel, ylabel, all_data, steps):
    try:
        save_path = join_base(config['log_dir'], f"/{title}.png")
        for data, info in all_data:
            plt.plot(steps, data, label=info)
            # add multiple legends
            plt.legend()

        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.yscale('log')
        plt.grid(True)
        plt.savefig(save_path)
        plt.show()
        plt.close()
    except Exception as e:
        print(e)

def figure_list_to_csv(config, column_names, data, name_csv):
    try:
        obj = {}
        for i in range(len(column_names)):
            if data[i] is not None:
                obj[str(column_names[i])] = data[i]

        data_frame = pd.DataFrame(obj, index=[0])
        save_path = join_base(config['log_dir'], f"/{name_csv}.csv")
        data_frame.to_csv(save_path, index=False)
        return data_frame
    except Exception as e:
        print(e)

def zip_directory(directory_path, output_zip_path):
    print(f"{ directory_path } -> { output_zip_path }")
    with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                # Add file to zip, preserving the directory structure
                arcname = os.path.relpath(file_path, start=directory_path)
                zipf.write(file_path, arcname)

# save model
def save_model(model, global_step, global_val_step, optimizer, lr_scheduler, model_folder_name, model_base_name):
    model_filename = get_weights_file_path(
        model_folder_name=model_folder_name,
        model_base_name=model_base_name,    
        step=global_step
    )

    torch.save({
        "global_step": global_step,
        "global_val_step": global_val_step,
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        "lr_scheduler_state_dict": lr_scheduler.state_dict()
    }, model_filename)
    
    print(f"Saved model at {model_filename}")

# save config
def save_config(config: dict, global_step: int):
    config_filename = f"{config['config_dir']}/config_{global_step:010d}.json"
    with open(config_filename, "w") as f:
        json.dump(config, f)
    print(f"Saved config at {config_filename}")

__all__ = [
    "LossFigure",
    "read",
    "write",
    "draw_graph",
    "draw_multi_graph",
    "figure_list_to_csv",
    "save_model",
    "save_config",
    "zip_directory",
]