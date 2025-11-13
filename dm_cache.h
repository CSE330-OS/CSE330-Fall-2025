#ifndef DM_CACHE_GUARD
#define DM_CACHE_GUARD
#include <linux/bio.h>

#define BLOCK_SHIFT 3

/* Cache block metadata structure */
struct cacheblock {
    sector_t src_block_addr;                 /* Block idx of the cacheblock on the source dev*/
    sector_t cache_block_addr;               /* Block idx of the cacheblock on the cache dev*/
    struct list_head list;
};

/* Defined in dm_cache.c */
void do_read(struct block_device *blkdev, sector_t addr);
void do_write(struct block_device *blkdev, sector_t addr);
unsigned int get_block_shift(void);

/* Defined in dm_lru.c */
void my_cache_hit(struct block_device *cache_blkdev, struct cacheblock *block,
        struct list_head *lru_head);
struct cacheblock* my_cache_miss(struct block_device *src_blkdev, struct block_device *cache_blkdev,
        sector_t src_blkaddr, struct list_head *lru_head);
void init_lru(struct list_head *lru_head, unsigned int num_blocks);
void free_lru(struct list_head *lru_head);

#endif
