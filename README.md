# Somniloquy

Python software intended to log and transcribe sleep-talking (but has other uses as a transcribing voice-activated recorder).
Pull requests and issues warmly welcomed!
## Installation
Currently limited to development build installs only (more technical):

 - Install git, GitHub CLI, and Miniconda.
 - `cd` to your preferred directory.
 - Linux users: Run the following:

	    gh repo fork --clone=true --remote=true Peter-Laszcz/Somniloquy-Python
   		cd Somniloquy-Python
	    conda config --set channel_priority strict
	    conda deactivate
	    conda env remove --name somniloquy
	    conda env create --name somniloquy --file data/environment.yml
 - Windows users: Run the following:

	    gh repo fork --clone=true --remote=true Peter-Laszcz/Somniloquy-Python
   		cd Somniloquy-Python
	    conda config --set channel_priority strict
	    conda deactivate
	    conda env remove --name somniloquy
	    conda env create --name somniloquy --file data/environment_windows.yml

## Running
From within your Somniloquy directory, run:

    conda activate somniloquy
    python main.py
