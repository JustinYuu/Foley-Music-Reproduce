# Foley-Music-Reproduce
A PyTorch Re-Implementation of ECCV 2020 paper "Foley Music: Learning to Generate Music from Videos "  

**Foley Music: Learning to Generate Music from Videos** Chuang Gan, Deng Huang, Peihao Chen, Joshua B. Tenenbaum, and Antonio Torralba

[Paper link](https://arxiv.org/abs/2007.10984)  

## Introduction  

Since the authors of this paper no longer maintain the official repository and some essential python libraries are unavailable, the required environment of the original code repo **cannot** be established, which sets an obstacle for the following works. Based on such preliminaries, we uploaded a reproduced version in which the main modifications are listed as follows:

- **Remove Unavailable Reliance:**  Since [torchpie](https://github.com/SunDoge/cifar10-torchpie) is unavailable to be pulled or installed, we try to remove this package and replace all relevant usages with other implementations.   
- **Add Support for Higher Torch Versions:** Some GPUs (e.g., Tesla A100) do not support low PyTorch versions, thus it is necessary to add support for higher versions. The `nn.ParameterList` function in the higher PyTorch version could cause forward propagation errors while using `nn.DataParallel()` for multi-GPU training, so we replace it with the solution mentioned in [here](https://github.com/lucidrains/axial-attention/issues/11).
- **Update Codes and Scripts Arrangement.**  

## Prerequisites  

- PyTorch<=1.9.0  
- pyFluidSynth  
- pretty_midi  

The .wav generation also requries the installation of [FluidSynth](https://www.fluidsynth.org/), please refer to this [link](https://github.com/FluidSynth/fluidsynth) for installation instruction.  

## Data Preparation  

Please refer to the [official repository](https://github.com/chuangg/Foley-Music) for downloading the datasets required.  

## Training and Inference  

For URMP dataset:

    bash scripts/train_urmp.sh  
    bash scripts/infer_atin.sh
    
For MUSIC dataset:  

    bash scripts/train_music.sh  
    bash scripts/infer_music.sh  
    
For the AtinPiano dataset:

    bash scripts/train_atin.sh  
    bash scripts/infer_atin.sh  

Be aware to change the instrument type in the **.sh** files when training/testing on the **URMP** and **MUSIC** datasets.  

**Notes from the authors:**  

- Instrument name ($INSTRUMENT_NAME) can be found [here](https://github.com/craffel/pretty-midi/blob/master/pretty_midi/constants.py#L7)

- If you do not have the video file or you want to generate MIDI and audio only, you can add -oa flag to skip the generation of video.  

## Citation  

    @inproceedings{FoleyMusic2020,
      author    = {Chuang Gan and
                   Deng Huang and
                   Peihao Chen and
                   Joshua B. Tenenbaum and
                   Antonio Torralba},
      title     = {Foley Music: Learning to Generate Music from Videos},
      booktitle = {ECCV},
      year      = {2020},
    }
