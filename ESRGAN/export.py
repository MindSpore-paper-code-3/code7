# Copyright 2022 Huawei Technologies Co., Ltd
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

"""export file."""

import argparse
import numpy as np
import mindspore
from mindspore import context, Tensor
from mindspore.train.serialization import load_checkpoint, load_param_into_net
from mindspore.train.serialization import export
from src.model.generator import RRDBNet
from src.dataset.testdataset import create_testdataset

parser = argparse.ArgumentParser(description="ESRGAN export")
parser.add_argument('--file_name', type=str, default='ESRGAN', help='output file name prefix.')
parser.add_argument('--file_format', type=str, choices=['AIR', 'ONNX', 'MINDIR'], default='MINDIR', help='file format')
parser.add_argument("--generator_path", type=str, default='./ckpt/psnr_best.ckpt')
parser.add_argument("--device_id", type=int, default=0, help="device id, default: 0.")
parser.add_argument("--test_LR_path", type=str, default='/home/root/ESRGAN/datasets/Set14/LRbicx4', \
    help='LR_path for export ONNX')
parser.add_argument("--test_GT_path", type=str, default='/home/root/ESRGAN/datasets/Set14/GTmod12', \
    help='GT_path for export ONNX')

if __name__ == '__main__':
    args = parser.parse_args()
    context.set_context(mode=context.GRAPH_MODE, device_id=args.device_id)
    generator = RRDBNet(3, 3)
    params = load_checkpoint(args.generator_path)
    load_param_into_net(generator, params)
    generator.set_train(False)
    # The model will generate different ONNX file depending on the input size.
    # Need to use validation set Set5, Set14 for model export.
    if args.file_format == 'ONNX':
        test_ds = create_testdataset(1, args.test_LR_path, args.test_GT_path)
        for sample in test_ds.create_dict_iterator(output_numpy=True):
            im_data_shape = sample['LR'].shape
            export_path = str(im_data_shape[2]) + '_' + str(im_data_shape[3])
            inputs = Tensor(np.ones(list(im_data_shape)), mindspore.float32)
            export(generator, inputs, file_name=export_path, file_format=args.file_format)
    else:
        input_shp = [1, 3, 200, 200]
        input_array = Tensor(np.random.uniform(-1.0, 1.0, size=input_shp).astype(np.float32))
        G_file = "{}_model".format(args.file_name)
        export(generator, input_array, file_name=G_file, file_format=args.file_format)
