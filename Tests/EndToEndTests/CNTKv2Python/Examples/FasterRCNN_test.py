﻿# Copyright (c) Microsoft. All rights reserved.

# Licensed under the MIT license. See LICENSE.md file in the project root
# for full license information.
# ==============================================================================

import numpy as np
import os
import pytest
import sys
from cntk import load_model
from cntk.cntk_py import DeviceKind_GPU
from cntk.device import try_set_default_device, gpu
from cntk.logging.graph import get_node_outputs
from cntk.ops.tests.ops_test_utils import cntk_device
from _cntk_py import force_deterministic_algorithms
force_deterministic_algorithms()

abs_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(abs_path)
sys.path.append(os.path.join(abs_path, "..", "..", "..", "..", "Examples", "Image", "Detection", "FasterRCNN"))

from prepare_test_data import prepare_Grocery_data, prepare_alexnet_v0_model
grocery_path = prepare_Grocery_data()
prepare_alexnet_v0_model()

from install_data_and_model import create_grocery_mappings
create_grocery_mappings(grocery_path)

from config import cfg
cfg["CNTK"].FORCE_DETERMINISTIC = True
cfg["CNTK"].DEBUG_OUTPUT = False
cfg["CNTK"].VISUALIZE_RESULTS = False
cfg["CNTK"].FAST_MODE = True
cfg["CNTK"].MAP_FILE_PATH = grocery_path

from FasterRCNN import parse_arguments, train_faster_rcnn_alternating, eval_faster_rcnn_mAP
parse_arguments()

python35_only = pytest.mark.skipif(sys.version_info[:2] != (3,5), reason="requires python 3.5")
win_only = pytest.mark.skipif(sys.platform != 'win32', reason="it runs currently only in windows")


@python35_only
@win_only
def test_fasterrcnn_grocery_training_e2e(device_id):
    if cntk_device(device_id).type() != DeviceKind_GPU:
        pytest.skip('test only runs on GPU')  # it runs very slow in CPU
    try_set_default_device(cntk_device(device_id))

    # since we do not use a reader for evaluation we need unzipped data
    externalData = 'CNTK_EXTERNAL_TESTDATA_SOURCE_DIRECTORY' in os.environ

    if externalData:
        extPath = os.environ['CNTK_EXTERNAL_TESTDATA_SOURCE_DIRECTORY']
        model_file = os.path.join(extPath, "PreTrainedModels", "AlexNet", "v0", "AlexNet.model")
    else:
        model_file = os.path.join(abs_path, *"../../../../Examples/Image/PretrainedModels/AlexNet.model".split("/"))

    from FasterRCNN import train_faster_rcnn_e2e, eval_faster_rcnn_mAP

    np.random.seed(seed=3)
    eval_model = train_faster_rcnn_e2e(model_file, debug_output=False)
    meanAP = eval_faster_rcnn_mAP(eval_model)
    assert meanAP > 0.127

@python35_only
@win_only
def test_fasterrcnn_grocery_training_4stage(device_id):
    if cntk_device(device_id).type() != DeviceKind_GPU:
        pytest.skip('test only runs on GPU')  # it runs very slow in CPU
    try_set_default_device(cntk_device(device_id))

    # since we do not use a reader for evaluation we need unzipped data
    externalData = 'CNTK_EXTERNAL_TESTDATA_SOURCE_DIRECTORY' in os.environ

    if externalData:
        extPath = os.environ['CNTK_EXTERNAL_TESTDATA_SOURCE_DIRECTORY']
        model_file = os.path.join(extPath, "PreTrainedModels", "AlexNet", "v0", "AlexNet.model")
    else:
        model_file = os.path.join(abs_path, *"../../../../Examples/Image/PretrainedModels/AlexNet.model".split("/"))

    from FasterRCNN import train_faster_rcnn_alternating, eval_faster_rcnn_mAP

    np.random.seed(seed=3)
    eval_model = train_faster_rcnn_alternating(model_file, debug_output=False)
    meanAP = eval_faster_rcnn_mAP(eval_model)
    assert meanAP > 0.135

if __name__ == '__main__':
    test_fasterrcnn_grocery_training_e2e(0)
    test_fasterrcnn_grocery_training_4stage(0)
