#!/bin/bash

# Installation directory for packages
DIR_INSTALL=/usr/

# Build directory
DIR_BUILD=build

DIR_CONFIG=config

NUM_CORES=$(nproc)
DEFAULT_ARCHITECTURE=amd64

# Toolchain Paths
DIR_TOOLCHAIN_ARMHF=/opt/toolchains/cross-armhf
DIR_TOOLCHAIN_AARCH64=/opt/toolchains/cross-aarch64/
DIR_TOOLCHAIN_ARMR5=/opt/toolchains/cross-armr5
DIR_TOOLCHAIN_ESP32=/opt/toolchains/cross-esp32

# FreeRTOS include directory (necessary to build ASOA for the ARM Cortex-R5)
DIR_XILINX_HEADERS="/home/dominik/workspace/brainstem/export/brainstem/sw/brainstem/freertos10_xilinx_domain/bspinclude/include"
DIR_ESP32_HEADERS="/home/dominik/Promotion/Code/ASOA/ASOA/targets/esp32"

# Static IP address of brainstem (hardcoded in ASOA for embedded devices)
IP_BRAINSTEM_R5=10.0.0.1

