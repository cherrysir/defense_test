import argparse
import os
import random
import sys
import numpy as np
import torch

sys.path.append('%s/../' % os.path.dirname(os.path.realpath(__file__)))

from src.mnist_model import MNIST_CNN
from src.resnet_model import ResNet18
from src.train_mart_mnist import MNIST_Training_Parameters
from src.train_mart_cifar10 import CIFAR10_Training_Parameters
from src.get_datasets import get_mnist_train_validate_loader
from src.get_datasets import get_cifar10_train_validate_loader

from Denfenses.DefenseMethods.MART import MARTDefense

def main(args):
    os.environ['CUDA_VISIBLE_DEVICES'] = args.gpu_index
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    # Set the random seed manually for reproducibility.
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    torch.manual_seed(args.seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(args.seed)
    np.random.seed(args.seed)
    random.seed(args.seed)

    dataset = args.dataset.upper()
    assert dataset == 'MNIST' or dataset == 'CIFAR10'
    # 获取MNIST/MNIST的训练参数、模型、训练集和验证集
    if dataset == 'MNIST':
        training_parameters = MNIST_Training_Parameters
        model_framework = MNIST_CNN().to(device)
        batch_size = training_parameters['batch_size']
        train_loader, valid_loader = get_mnist_train_validate_loader(dir_name='../data/MNIST/', batch_size=batch_size, valid_size=0.1,
                                                                     shuffle=True)
    else:
        training_parameters = CIFAR10_Training_Parameters
        model_framework = ResNet18().to(device)
        batch_size = training_parameters['batch_size']
        train_loader, valid_loader = get_cifar10_train_validate_loader(dir_name='../data/CIFAR10/', batch_size=batch_size, valid_size=0.1,
                                                                       augment=True, shuffle=True)
    # defense_name：防御名称
    defense_name = 'MART'
    # pat_params：防御参数
    mart_params = {
        'attack_step_num': args.step_num,
        'step_size': args.step_size,
        'epsilon': args.eps,
        'lamda': args.lamda
    }
    # 将参数传入MART防御中
    mart = MARTDefense(model=model_framework, defense_name=defense_name, dataset=dataset, training_parameters=training_parameters, device=device,
                     **mart_params)
    # 利用MART进行防御
    mart.defense(train_loader=train_loader, validation_loader=valid_loader)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='The MART Defenses')
    # dataset：数据集名称，为MNIST或CIFAR10
    # gpu_index：gpu的数量，默认为1
    # seed：随机种子数，默认为100
    parser.add_argument('--dataset', type=str, default='MNIST', help='the dataset (MNIST or CIFAR10)')
    parser.add_argument('--gpu_index', type=str, default='1', help="gpu index to use")
    parser.add_argument('--seed', type=int, default=100, help='the default random seed for numpy and torch')

    # eps：PGD对抗样本的最大扰动，默认为0.3
    # step_num：迭代次数，默认为10
    # step_size：迭代的步长，默认为0.075
    # lamda：正则化项系数，默认为6.0
    parser.add_argument('--eps', type=float, default=0.3, help='magnitude of random space')
    parser.add_argument('--step_num', type=int, default=10, help='perform how many steps when PGD perturbation')
    parser.add_argument('--step_size', type=float, default=0.075, help='the size of each perturbation')
    parser.add_argument('--lamda', type=float, default=6.0, help='the regularization coefficient')
    arguments = parser.parse_args()
    main(arguments)