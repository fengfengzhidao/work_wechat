# @Time:2022/10/6 22:49
# @Author:fengfeng
import threading


class Singleton(object):
    """
    单例类，单列对象保存在singleton_instance中
    """
    singleton_instance = dict()


def singleton(cls):
    """
    注解式实现单例模式
    :param cls:
    :return:
    """
    _singleton_lock = threading.Lock()

    def _singleton(*args, **kargs):
        # 单例模式双检锁判断
        # Python由于GIL锁，多线程不存在可见性问题，不需要volatile标识singleton_instance
        if cls not in Singleton.singleton_instance:
            with _singleton_lock:
                if cls not in Singleton.singleton_instance:
                    Singleton.singleton_instance[cls] = cls(*args, **kargs)
        return Singleton.singleton_instance[cls]

    return _singleton
