"""
# -*- coding: utf-8 -*-
-----------------------------------------------------------------------------------
# Author: Nguyen Mau Dung
# DoC: 2020.05.21
# email: nguyenmaudung93.kstn@gmail.com
-----------------------------------------------------------------------------------
# Description: The configurations of the project will be defined here
"""

import os
import argparse
import sys

import torch
import numpy as np
from easydict import EasyDict as edict

sys.path.append('../')

from utils.misc import make_folder


def parse_configs():
    parser = argparse.ArgumentParser(description='Complexer YOLO Implementation')
    parser.add_argument('--seed', type=int, default=2020,
                        help='re-produce the results with seed random')
    parser.add_argument('--saved_fn', type=str, default='complexer_yolo', metavar='FN',
                        help='The name using for saving logs, models,...')
    ####################################################################
    ##############     Model configs            ###################
    ####################################################################
    parser.add_argument('-a', '--arch', type=str, default='yolov3', metavar='ARCH',
                        help='The name of the model architecture')
    parser.add_argument('--dropout_p', type=float, default=0.5, metavar='P',
                        help='The dropout probability of the model')
    parser.add_argument('--multitask_learning', action='store_true',
                        help='If true, the weights of different losses will be learnt (train).'
                             'If false, a regular sum of different losses will be applied')
    parser.add_argument('--no_ball', action='store_true',
                        help='If true, no local stage for ball detection.')
    parser.add_argument('--no_event', action='store_true',
                        help='If true, no event spotting detection.')
    parser.add_argument('--no_seg', action='store_true',
                        help='If true, no segmentation module.')
    parser.add_argument('--pretrained_path', type=str, default=None, metavar='PATH',
                        help='the path of the pretrained checkpoint')
    parser.add_argument('--overwrite_global_2_local', action='store_true',
                        help='If true, the weights of the local stage will be overwritten by the global stage.')

    ####################################################################
    ##############     Dataloader and Running configs            #######
    ####################################################################
    parser.add_argument('--multiscale_training', action='store_true',
                        help='If true, use scaling data for training')
    parser.add_argument('--no-test', action='store_true',
                        help='If true, dont evaluate the model on the test set')
    parser.add_argument('--val-size', type=float, default=0.2,
                        help='The size of validation set')
    parser.add_argument('--smooth-labelling', action='store_true',
                        help='If true, smoothly make the labels of event spotting')
    parser.add_argument('--num_samples', type=int, default=None,
                        help='Take a subset of the dataset to run and debug')
    parser.add_argument('--num_workers', type=int, default=8,
                        help='Number of threads for loading data')
    parser.add_argument('--batch_size', type=int, default=32,
                        help='mini-batch size (default: 16), this is the total'
                             'batch size of all GPUs on the current node when using'
                             'Data Parallel or Distributed Data Parallel')
    parser.add_argument('--print_freq', type=int, default=10, metavar='N',
                        help='print frequency (default: 10)')
    parser.add_argument('--checkpoint_freq', type=int, default=3, metavar='N',
                        help='frequency of saving checkpoints (default: 3)')
    parser.add_argument('--sigma', type=float, default=0.5, metavar='SIGMA',
                        help='standard deviation of the 1D Gaussian for the ball position target')
    parser.add_argument('--thresh_ball_pos_mask', type=float, default=0.01, metavar='THRESH',
                        help='the lower thresh for the 1D Gaussian of the ball position target')
    ####################################################################
    ##############     Training strategy            ###################
    ####################################################################

    parser.add_argument('--start_epoch', type=int, default=1, metavar='N',
                        help='the starting epoch')
    parser.add_argument('--num_epochs', type=int, default=40, metavar='N',
                        help='number of total epochs to run')
    parser.add_argument('--lr', type=float, default=1e-3, metavar='LR',
                        help='initial learning rate')
    parser.add_argument('--minimum_lr', type=float, default=1e-7, metavar='MIN_LR',
                        help='minimum learning rate during training')
    parser.add_argument('--momentum', type=float, default=0.9, metavar='M',
                        help='momentum')
    parser.add_argument('-wd', '--weight_decay', type=float, default=1e-6, metavar='WD',
                        help='weight decay (default: 1e-6)')
    parser.add_argument('--optimizer_type', type=str, default='adam', metavar='OPTIMIZER',
                        help='the type of optimizer, it can be sgd or adam')
    parser.add_argument('--lr_type', type=str, default='plateau', metavar='SCHEDULER',
                        help='the type of the learning rate scheduler (steplr or ReduceonPlateau)')
    parser.add_argument('--lr_factor', type=float, default=0.5, metavar='FACTOR',
                        help='reduce the learning rate with this factor')
    parser.add_argument('--lr_step_size', type=int, default=5, metavar='STEP_SIZE',
                        help='step_size of the learning rate when using steplr scheduler')
    parser.add_argument('--lr_patience', type=int, default=3, metavar='N',
                        help='patience of the learning rate when using ReduceoPlateau scheduler')
    parser.add_argument('--earlystop_patience', type=int, default=None, metavar='N',
                        help='Early stopping the training process if performance is not improved within this value')
    parser.add_argument('--freeze_ball', action='store_true',
                        help='If true, no update/train weights for the global stage of ball detection.')
    parser.add_argument('--freeze_event', action='store_true',
                        help='If true, no update/train weights for the event module.')
    parser.add_argument('--freeze_seg', action='store_true',
                        help='If true, no update/train weights for the segmentation module.')
    # For warmup phase
    parser.add_argument('--warmup_epochs', type=int, default=0, metavar='N',
                        help='number of epochs in the warmup phase ')
    parser.add_argument('--warmup_lr_factor', type=float, default=1.0 / 3, metavar='FACTOR',
                        help='factor for the learning rate in the warmup phase ')
    parser.add_argument('--warmup_lr_method', type=str, default='linear', metavar='METHOD',
                        help='method for the learning rate in the warmup phase ')
    parser.add_argument('--lr_power', type=float, default=0.9, metavar='POWER',
                        help='power for the learning rate (poly)')

    ####################################################################
    ##############     Loss weight            ###################
    ####################################################################
    parser.add_argument('--bce_weight', type=float, default=0.5,
                        help='The weight of BCE loss in segmentation module, the dice_loss weight = 1- bce_weight')
    parser.add_argument('--ball_weight', type=float, default=1.,
                        help='The weight of loss of the global stage for ball detection')
    parser.add_argument('--event_weight', type=float, default=1.,
                        help='The weight of loss of the event spotting module')
    parser.add_argument('--seg_weight', type=float, default=1.,
                        help='The weight of BCE loss in segmentation module')

    ####################################################################
    ##############     Distributed Data Parallel            ############
    ####################################################################
    parser.add_argument('--world-size', default=-1, type=int, metavar='N',
                        help='number of nodes for distributed training')
    parser.add_argument('--rank', default=-1, type=int, metavar='N',
                        help='node rank for distributed training')
    parser.add_argument('--dist-url', default='tcp://127.0.0.1:29500', type=str,
                        help='url used to set up distributed training')
    parser.add_argument('--dist-backend', default='nccl', type=str,
                        help='distributed backend')
    parser.add_argument('--gpu_idx', default=None, type=int,
                        help='GPU index to use.')
    parser.add_argument('--no_cuda', action='store_true',
                        help='If true, cuda is not used.')
    parser.add_argument('--multiprocessing-distributed', action='store_true',
                        help='Use multi-processing distributed training to launch '
                             'N processes per node, which has N GPUs. This is the '
                             'fastest way to use PyTorch for either single node or '
                             'multi node data parallel training')
    ####################################################################
    ##############     Evaluation configurations     ###################
    ####################################################################
    parser.add_argument('--evaluate', action='store_true',
                        help='only evaluate the model, not training')
    parser.add_argument('--resume_path', type=str, default=None, metavar='PATH',
                        help='the path of the resumed checkpoint')
    parser.add_argument('--use_best_checkpoint', action='store_true',
                        help='If true, choose the best model on val set, otherwise choose the last model')
    parser.add_argument('--seg_thresh', type=float, default=0.5,
                        help='threshold of the segmentation output')
    parser.add_argument('--event_thresh', type=float, default=0.5,
                        help='threshold of the event spotting output')
    parser.add_argument('--save_test_output', action='store_true',
                        help='If true, the image of testing phase will be saved')

    ####################################################################
    ##############     Demonstration configurations     ###################
    ####################################################################
    parser.add_argument('--video_path', type=str, default=None, metavar='PATH',
                        help='the path of the video that needs to demo')
    parser.add_argument('--output_format', type=str, default='text', metavar='PATH',
                        help='the type of the demo output')
    parser.add_argument('--show_image', action='store_true',
                        help='If true, show the image during demostration')
    parser.add_argument('--save_demo_output', action='store_true',
                        help='If true, the image of demonstration phase will be saved')

    configs = edict(vars(parser.parse_args()))

    ####################################################################
    ############## Hardware configurations ############################
    ####################################################################
    configs.device = torch.device('cpu' if configs.no_cuda else 'cuda')
    configs.ngpus_per_node = torch.cuda.device_count()

    configs.pin_memory = True

    ####################################################################
    ##############     Data configs            ###################
    ####################################################################
    configs.working_dir = '../../'
    configs.dataset_dir = os.path.join(configs.working_dir, 'dataset', 'kitti')

    ####################################################################
    ############## logs, Checkpoints, and results dir ########################
    ####################################################################
    configs.checkpoints_dir = os.path.join(configs.working_dir, 'checkpoints', configs.saved_fn)
    configs.logs_dir = os.path.join(configs.working_dir, 'logs', configs.saved_fn)
    configs.use_best_checkpoint = True

    if configs.use_best_checkpoint:
        configs.saved_weight_name = os.path.join(configs.checkpoints_dir, '{}_best.pth'.format(configs.saved_fn))
    else:
        configs.saved_weight_name = os.path.join(configs.checkpoints_dir, '{}.pth'.format(configs.saved_fn))

    configs.results_dir = os.path.join(configs.working_dir, 'results')

    make_folder(configs.checkpoints_dir)
    make_folder(configs.logs_dir)
    make_folder(configs.results_dir)

    if configs.save_test_output:
        configs.saved_dir = os.path.join(configs.results_dir, configs.saved_fn)
        make_folder(configs.saved_dir)

    if configs.save_demo_output:
        configs.save_demo_dir = os.path.join(configs.results_dir, 'demo', configs.saved_fn)
        make_folder(configs.save_demo_dir)

    configs.class_list = ["Car", "Pedestrian", "Cyclist"]

    configs.CLASS_NAME_TO_ID = {
        'Car': 0,
        'Pedestrian': 1,
        'Cyclist': 2,
        'Van': 0,
        'Person_sitting': 1,
    }

    # Front side (of vehicle) Point Cloud boundary for BEV
    configs.boundary = {
        "minX": 0,
        "maxX": 50,
        "minY": -25,
        "maxY": 25,
        "minZ": -2.73,
        "maxZ": 1.27
    }

    # Back back (of vehicle) Point Cloud boundary for BEV
    configs.boundary_back = {
        "minX": -50,
        "maxX": 0,
        "minY": -25,
        "maxY": 25,
        "minZ": -2.73,
        "maxZ": 1.27
    }

    configs.BEV_WIDTH = 608  # across y axis -25m ~ 25m
    configs.BEV_HEIGHT = 608  # across x axis 0m ~ 50m

    configs.DISCRETIZATION = (configs.boundary["maxX"] - configs.boundary["minX"]) / configs.BEV_HEIGHT

    configs.colors = [[0, 255, 255], [0, 0, 255], [255, 0, 0]]

    # Following parameters are calculated as an average from KITTI dataset for simplicity
    #####################################################################################
    configs.Tr_velo_to_cam = np.array([
        [7.49916597e-03, -9.99971248e-01, -8.65110297e-04, -6.71807577e-03],
        [1.18652889e-02, 9.54520517e-04, -9.99910318e-01, -7.33152811e-02],
        [9.99882833e-01, 7.49141178e-03, 1.18719929e-02, -2.78557062e-01],
        [0, 0, 0, 1]
    ])

    # cal mean from train set
    configs.R0 = np.array([
        [0.99992475, 0.00975976, -0.00734152, 0],
        [-0.0097913, 0.99994262, -0.00430371, 0],
        [0.00729911, 0.0043753, 0.99996319, 0],
        [0, 0, 0, 1]
    ])

    configs.P2 = np.array([[719.787081, 0., 608.463003, 44.9538775],
                           [0., 719.787081, 174.545111, 0.1066855],
                           [0., 0., 1., 3.0106472e-03],
                           [0., 0., 0., 0]
                           ])

    configs.R0_inv = np.linalg.inv(configs.R0)
    configs.Tr_velo_to_cam_inv = np.linalg.inv(configs.Tr_velo_to_cam)
    configs.P2_inv = np.linalg.pinv(configs.P2)
    #####################################################################################

    return configs


if __name__ == "__main__":
    configs = parse_configs()
    print(configs)