#include <linux/list.h>
#include "dm_cache.h"

void
my_cache_hit(struct block_device *cache_blkdev, struct cacheblock *block,
        struct list_head *lru_head)
{
    // Write your code here
}

struct cacheblock*
my_cache_miss(struct block_device *src_blkdev, struct block_device *cache_blkdev,
        sector_t src_blkaddr, struct list_head *lru_head)
{
    // Write your code here
    struct cacheblock *block  = NULL;
    return block;
}

void
init_lru(struct list_head *lru_head, unsigned int num_blocks)
{
    // Write your code here
}

void
free_lru(struct list_head *lru_head)
{
    // Write your code here
}
