"""
C Major
-c '1,0,1,0,1,1,0,1,0,1,0,1'
C Minor
-c '1,0,1,1,0,1,0,1,1,0,0,1'

"""

from core.models import ModelFactory
from core.dataloaders import DataLoaderFactory
import argparse
from pathlib import Path
import torch
from pyhocon import ConfigFactory, ConfigTree
from pprint import pprint
from tqdm import tqdm
from core.dataloaders.youtube_dataset import YoutubeDataset
from core.models.music_transformer_dev.music_transformer import MusicTransformer
from core import utils
import os

DEVICE = torch.device('cuda')


def get_video_name_list(video_root):
    videos = os.listdir(video_root)
    video_list = {}
    for video in videos:
        key = video.split('.')[0]
        value = os.path.join(video_root, video)
        video_list[key] = value
    return video_list


def get_video_path(video_root, vid_name: str):  # get correspond video for ffmpeg
    videos = get_video_name_list(video_root)
    vid_path = videos[vid_name]
    return vid_path


def change_time_format(time):
    return str(int(time / 60)).zfill(2) + '_' + str(int(time % 60)).zfill(2)


def main(args):
    torch.set_grad_enabled(False)

    checkpoint_path = Path(args.checkpoint)
    video_dir = Path(args.video)
    output_dir = Path(args.output)
    if args.control is not None:
        control_tensor = utils.midi.pitch_histogram_string_to_control_tensor(args.control)
    else:
        control_tensor = None

    cp = torch.load(checkpoint_path)
    cfg = ConfigFactory.parse_file(
        args.cfg
    )
    instrument = cfg.get_string('dataset.instrument', args.instrument)
    pprint(cfg)
    print('Using Instrument:', instrument)

    model_factory = ModelFactory(cfg)
    dataloader_factory = DataLoaderFactory(cfg)

    model: MusicTransformer = model_factory.build(device=DEVICE)

    model.load_state_dict(cp['state_dict'])
    model.eval()

    dl = dataloader_factory.build(split='val')
    ds: YoutubeDataset = dl.dataset
    pprint(ds.samples[:5])

    length = cfg.get_float('dataset.duration')  # how long is your produced audio
    os.makedirs(output_dir / 'audio', exist_ok=True)
    os.makedirs(output_dir / 'video', exist_ok=True)

    for data in tqdm(ds):
        index = data['index']
        pose = data['pose']

        pose = pose.cuda(non_blocking=True)
        if control_tensor is not None:
            control_tensor = control_tensor.cuda(non_blocking=True)
        sample = ds.samples[index]

        events = model.generate(
            pose.unsqueeze(0),
            target_seq_length=ds.num_events,
            beam=5,
            pad_idx=ds.PAD_IDX,
            sos_idx=ds.SOS_IDX,
            eos_idx=ds.EOS_IDX,
            control=control_tensor,
        )
        if events.shape[1] <= 0: 
            print('=' * 100)
            print('not events')
            print(sample)
            print('=' * 100)
            continue

        print('this events shape: ', events.shape)
        print('this events length: ', len(events))
        try:
            video_path = next(video_dir.glob(f'{sample.vid}.*'))
        except Exception as e:
            print(e)
            print('skip')
            if args.only_audio:
                pass
            else:
                continue

        ss = change_time_format(sample.start_time)
        dd = change_time_format(sample.start_time + length)
        add_name = '-' + ss + '-' + dd

        midi_dir = output_dir / 'midi' / f'{sample.vid}'
        os.makedirs(midi_dir, exist_ok=True)
        midi_path = midi_dir / f'{sample.vid}{add_name}.midi'
        pm = utils.midi.tensor_to_pm(
            events.squeeze(),
            instrument=instrument
        )
        pm.write(str(midi_path))

        audio_dir = output_dir / 'audio' / f'{sample.vid}'
        os.makedirs(audio_dir, exist_ok=True)
        audio_path = audio_dir / f'{sample.vid}{add_name}.wav'

        utils.midi.pm_to_wav(
            pm,
            audio_path,
            rate=22050,
        )

        if not args.only_audio:
            # find only video in val.csv
            in_path = get_video_path(video_dir, sample.vid)
            vid_name = sample.vid
            vid_dir = os.path.join(output_dir, 'video', vid_name)
            if not os.path.exists(vid_dir):
                os.mkdir(vid_dir)

            # cut video to fixed length
            vid_dir_name = sample.vid  # just name, no suffix like .mp4
            cut_name = str(vid_dir_name) + add_name + '_middle.mp4'

            # concat audio and video
            vid_path = os.path.join(vid_dir, str(vid_dir_name) + add_name + '.mp4')
            cmd2 = f'ffmpeg -y -ss {ss} -i {in_path} -t {length} -i {str(audio_path)} -t {length} -map 0:v:0 -map 1:a:0 -c:v libx264 -c:a aac -strict experimental {vid_path}'

            os.system(cmd2)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'checkpoint'
    )
    parser.add_argument(
        '-o', '--output'
    )
    parser.add_argument(
        '-v', '--video', default=""
    )
    parser.add_argument(
        '-i', '--instrument', default='Acoustic Grand Piano'
    )
    parser.add_argument(
        '-c', '--control', default=None
    )
    parser.add_argument(
        '-oa', '--only_audio', action="store_true"
    )
    parser.add_argument(
        '--cfg', default=''
    )
    args = parser.parse_args()
    main(args)
