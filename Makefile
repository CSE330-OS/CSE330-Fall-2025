obj-m += dmcache.o 

dmcache-objs := dm_cache.o dm_lru.o

all:
		make -C /lib/modules/$(shell uname -r)/build/ M=$(PWD) modules
clean:
		make -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean
