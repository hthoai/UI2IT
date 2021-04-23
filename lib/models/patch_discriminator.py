import torch.nn as nn
from torch import Tensor
from lib.layers import ConvNormRelu


class PatchDiscriminator(nn.Module):
    """Defines a PatchGAN (just a convnet:)) discriminator."""

    def __init__(
        self,
        in_channels: int,
        nd_filters: int=64,
        n_layers: int=3,
        norm_layer: nn=nn.BatchNorm2d):
        """Construct a PatchGAN discriminator.

        Parameters:
        -----------
            in_channels:    the number of channels in input images
            nd_filters:     the number of filters in the last conv layer
            n_layers:       the number of conv layers in the discriminator
            norm_layer:     normalization layer
        """
        super(PatchDiscriminator, self).__init__()
        # No need to use bias as BatchNorm2d has affine parameters
        use_bias = norm_layer == nn.InstanceNorm2d
        kw = 4
        padw = 1
        self.conv1 = nn.Conv2d(in_channels, nd_filters, kernel_size=kw, stride=2, padding=padw)
        self.leaky_relu = nn.LeakyReLU(0.2)
        nf_mult = 1
        nf_mult_prev = 1
        sequence = []
        # Gradually increase the number of filters
        for n in range(1, n_layers):
            nf_mult_prev = nf_mult
            nf_mult = min(2 ** n, 8)
            sequence += [ConvNormRelu(
                nd_filters * nf_mult_prev,
                nd_filters * nf_mult,
                conv_type="forward",
                norm_layer=norm_layer,
                kernel_size=kw,
                stride=2,
                pad_size=padw,
                use_bias=use_bias,
                leaky=0.2)]
        nf_mult_prev = nf_mult
        nf_mult = min(2 ** n_layers, 8)
        self.conv_norm_relus = nn.Sequential(*sequence)
        self.conv2 = ConvNormRelu(
            nd_filters * nf_mult_prev,
            nd_filters * nf_mult,
            conv_type="forward",
            norm_layer=norm_layer,
            kernel_size=kw,
            stride=1,
            pad_size=padw,
            use_bias=use_bias,
            leaky=0.2)
        self.output = nn.Conv2d(nd_filters * nf_mult, 1, kernel_size=kw, stride=1, padding=padw)

    def forward(self, x: Tensor) -> Tensor:
        x = self.conv1(x)
        x = self.leaky_relu(x)
        x = self.conv_norm_relus(x)
        x = self.conv2(x)
        x = self.output(x)

        return x
