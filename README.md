# Stable Audio Open Instrumental Finetune

This repository contains the code used to generate the dataset for fine-tuning [Stable Audio Open 1.0](https://huggingface.co/stabilityai/stable-audio-open-1.0) into our [Instrumental Finetune](https://huggingface.co/santifiorino/SAO-Instrumental-Finetune).

In the `dataset-creator` directory, you will find a pipeline that automatically synthesizes MIDI files into audio using VST3 instruments, along with text prompts describing each track. These prompts are generated from song information retrieved via external APIs, as well as additional metadata extracted during the synthesis process and from the resulting audio.

In the `train-model` directory, you will find the configuration files used to retrain the model, along with a Jupyter Notebook containing the training code.