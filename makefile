# Define variables
CC = gcc
CFLAGS = -Wall -g

all: setup rebuild_h5py

setup:
	@echo "Installing packages using poetry..." \
	&& poetry install --no-root

rebuild_h5py:
	@echo "Entering virtual environment..." \
	&& poetry shell \
	&& echo "Installing h5py..." \
	&& pip uninstall h5py -y \
	&& pip install --no-binary=h5py h5py 


.PHONY: all setup rebuild_h5py

