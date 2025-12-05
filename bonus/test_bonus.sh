#!/bin/bash

make clean
make

sudo insmod dmcache.ko
echo 0 4194304 cache $1 $2 8 32778 | sudo dmsetup create cache
sudo dmsetup status cache

# Read Miss
sudo fio \
  --filename=/dev/mapper/cache \
  --name=random_reuse \
  --rw=randread \
  --direct=1 \
  --size=128MB \
  --randrepeat=1 \
  --randseed=12345 \
  --numjobs=1
sudo dmsetup status cache

# Read Miss
sudo fio \
  --filename=/dev/mapper/cache \
  --name=sequential_once \
  --rw=read \
  --direct=1 \
  --size=128MB \
  --offset=128MB \
  --numjobs=1
sudo dmsetup status cache

#Read Hits
sudo fio \
  --filename=/dev/mapper/cache \
  --name=random_reuse \
  --rw=randread \
  --direct=1 \
  --size=128MB \
  --randrepeat=1 \
  --randseed=12345 \
  --numjobs=1
sudo dmsetup status cache

sudo dmsetup remove cache
sudo rmmod dmcache
