# Copyright 2020 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================
"""
##############export checkpoint file into air, onnx, mindir models#################
python export.py
"""
import argparse
import numpy as np

from mindspore import Tensor, load_checkpoint, load_param_into_net, export, context

from src.config import cfg_mr, cfg_subj, cfg_sst2
from src.textcnn import TextCNN
from src.dataset import MovieReview, SST2, Subjectivity

parser = argparse.ArgumentParser(description='TextCNN export')
parser.add_argument("--device_id", type=int, default=0, help="device id")
parser.add_argument("--ckpt_file", type=str, required=True, help="checkpoint file path.")
parser.add_argument("--file_name", type=str, default="textcnn", help="output file name.")
parser.add_argument('--file_format', type=str, choices=["AIR", "ONNX", "MINDIR"], default='AIR', help='file format')
parser.add_argument("--device_target", type=str, choices=["Ascend", "GPU", "CPU"], default="Ascend",
                    help="device target")
parser.add_argument('--dataset', type=str, default='MR', choices=['MR', 'SUBJ', 'SST2'],
                    help='dataset name.')

args = parser.parse_args()

context.set_context(mode=context.GRAPH_MODE, device_target=args.device_target, device_id=args.device_id)

if __name__ == '__main__':

    if args.dataset == 'MR':
        cfg = cfg_mr
        instance = MovieReview(root_dir=cfg.data_path, maxlen=cfg.word_len, split=0.9)
    elif args.dataset == 'SUBJ':
        cfg = cfg_subj
        instance = Subjectivity(root_dir=cfg.data_path, maxlen=cfg.word_len, split=0.9)
    elif args.dataset == 'SST2':
        cfg = cfg_sst2
        instance = SST2(root_dir=cfg.data_path, maxlen=cfg.word_len, split=0.9)
    else:
        raise ValueError("dataset is not support.")

    net = TextCNN(vocab_len=instance.get_dict_len(), word_len=cfg.word_len,
                  num_classes=cfg.num_classes, vec_length=cfg.vec_length)

    param_dict = load_checkpoint(args.ckpt_file)
    load_param_into_net(net, param_dict)

    input_arr = Tensor(np.ones([cfg.batch_size, cfg.word_len], np.int32))
    export(net, input_arr, file_name=args.file_name, file_format=args.file_format)
