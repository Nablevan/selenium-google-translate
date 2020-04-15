import asyncio
import random
import time


async def set_text(l: list):
    for i in range(10):
        # await asyncio.sleep(random.randint(1, 2))
        await asyncio.sleep(1)
        l.append('text-{}'.format(i))
        print('set{}'.format(i))


async def get_text(l: list):
    begin = time.time()
    while True:
        await asyncio.sleep(1)
        while l.__len__() > 0:
            # await asyncio.sleep(random.randint(1, 2))
            begin = time.time()
            await asyncio.sleep(1)
            print('get', l.pop(0))
        if time.time() - begin > 5:
            return


async def main(l: list):
    s = set_text(l)
    g = get_text(l)
    g2 = get_text(l)
    # tasks = [
    #     asyncio.create_task(s),
    #     asyncio.create_task(g)
    # ]
    tasks = [s, g, g2]
    await asyncio.wait(tasks)


if __name__ == '__main__':
    file_list = []
    start = time.time()
    asyncio.run(main(file_list))
    print('total: {} secs'.format(time.time()-start))
